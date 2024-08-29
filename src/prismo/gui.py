from qtpy.QtCore import QTimer
import dill
import dask.array as da
import napari
import multiprocess
import numcodecs
import numpy as np
import threading
import xarray as xr
import zarr as zr

import widgets


class Relay:
    def __init__(self, pipe):
        self._pipe = pipe
        self._timers = []

    def poll(self, func, timeout, route, *args, **kwargs):
        def do_poll():
            self._pipe.send([route, args, kwargs])
            func(self._pipe.recv())

        timer = QTimer()
        timer.timeout.connect(do_poll)
        timer.start(timeout)
        self._timers.append(timer)

    def get(self, route, *args, **kwargs):
        self._pipe.send([route, args, kwargs])
        return self._pipe.recv()

    def post(self, route, *args, **kwargs):
        self._pipe.send([route, args, kwargs])


class GUI:
    def __init__(self, gui_func, file=None, tile=None):
        def run_gui(pipe):
            viewer = napari.Viewer()
            relay = Relay(pipe)
            gui_func(viewer, relay)
            napari.run()
            pipe.close()

        def run_router(pipe, running, quit):
            while not quit.is_set():
                running.wait()
                try:
                    route, args, kwargs = pipe.recv()
                    result = self._routes[route](*args, **kwargs)
                    if result is not None:
                        pipe.send(result)
                except (BrokenPipeError, EOFError):
                    self.quit()
                except Exception as e:
                    self.quit()
                    raise e

        self._running = threading.Event()
        self._running.set()
        self._quit = threading.Event()
        ctx = multiprocess.get_context("spawn")
        self._pipe, child_pipe = ctx.Pipe()
        self._gui_process = ctx.Process(target=run_gui, args=(child_pipe,))
        self._workers = []
        self._router = threading.Thread(
            target=run_router, args=(self._pipe, self._running, self._quit)
        )
        self._routes = {}
        self._arrays = {}
        self._array_lock = threading.Lock()
        self._file = file
        self._tile = tile

    def start(self):
        self._gui_process.start()
        for worker in self._workers:
            worker.start()
        self._router.start()

    def resume(self):
        self._running.set()

    def pause(self):
        self._running.clear()

    def quit(self):
        self._running.set()
        self._quit.set()
        if self._gui_process.is_alive():
            self._gui_process.terminate()
        self._pipe.close()

    def worker(self, func):
        def run_worker():
            for x in func():
                self._running.wait()
                if self._quit.is_set():
                    break

        self._workers.append(threading.Thread(target=run_worker))

        return func

    def route(self, route):
        def decorator(func):
            self._routes[route] = func
            return func

        return decorator

    def new_array(self, name, dims):
        xp = xr.Dataset()
        shape = tuple(x if isinstance(x, int) else len(x) for x in dims.values())
        xp["tile"] = (
            tuple(dims.keys()) + ("im_y", "im_x"),
            da.zeros(
                shape=shape + self._tile.shape,
                chunks=(1,) * len(dims) + self._tile.shape,
                dtype=self._tile.dtype,
            ),
        )

        for dim_name, coords in dims.items():
            if isinstance(coords, int):
                continue
            xp.coords[dim_name] = coords

        store = zr.DirectoryStore(self._file)
        compressor = numcodecs.Blosc(cname="zstd", clevel=5, shuffle=numcodecs.Blosc.BITSHUFFLE)
        try:
            xp.to_zarr(store, group=name, compute=False, encoding={"tile": {"compressor": compressor}})
        except:
            raise FileExistsError(f"{self._file} already exists.")

        zarr_tiles = zr.open(store, path=name + "/tile", mode="a", synchronizer=zr.ThreadSynchronizer())
        zarr_tiles.fill_value = 0
        tiles = da.from_zarr(zarr_tiles)
        tiles.__class__ = DiskArray
        tiles._zarr_array = zarr_tiles
        xp.tile.data = tiles

        with self._array_lock:
            self._arrays[name] = xp["tile"]

        return xp["tile"]

    @property
    def arrays(self):
        with self._array_lock:
            arrs = dict(self._arrays)
        return arrs
        
    def __del__(self):
        self.quit()


class LiveClient:
    def __init__(self, viewer, relay):
        self._viewer = viewer
        self._relay = relay
        img = self._relay.get("img")
        self._viewer.add_image(img, name="live")
        self._relay.poll(self.update_img, 1000 // 60, "img")

    def update_img(self, img):
        self._viewer.layers[0].data = img


def live(ctrl):
    gui = GUI(LiveClient)

    img = ctrl.snap()

    @gui.worker
    def snap():
        while True:
            img[:] = ctrl.snap()
            yield

    @gui.route("img")
    def get_img():
        return img

    gui.start()

    return gui


class AcqClient:
    def __init__(self, viewer, relay, file):
        self._viewer = viewer
        self._relay = relay
        self._file = file
        self._live_timer = QTimer()
        self._refresh_timer = QTimer()
        self._arrays = set()

        img = self._relay.get("img")
        self._viewer.add_image(img, name="live")

        self._live_timer.timeout.connect(self.update_img)
        self._live_timer.start(1000 // 60)
        self._viewer.window.add_dock_widget(
            widgets.BoundarySelector(self._relay, self.acq_step),
            name="Acquisition Boundaries",
            tabify=False,
        )
        self._viewer.window.add_dock_widget(
            widgets.ValveController(self._relay), name="Valve Controls", tabify=False
        )

    def acq_step(self, top_left, bot_right):
        self._live_timer.disconnect()
        self._live_timer.stop()
        self._viewer.layers.remove("live")

        self._relay.post("acq", top_left, bot_right)
        self._refresh_timer.timeout.connect(self.refresh)
        self._refresh_timer.start(1000)


    def refresh(self):
        arrays = self._relay.get("arrays")
        new_arrays = arrays - self._arrays
        self._arrays = arrays.union(self._arrays)
        for arr in new_arrays:
            xp = xr.open_zarr(self._file, group=arr)
            xp["image"] = tiles_to_image(xp)
            dims = xp["image"].dims
            self._viewer.add_image(
                xp["image"],
                channel_axis=dims.index("channel") if "channel" in dims else None,
                name=list(xp["channel"].to_numpy()) if "channel" in xp else None,
                multiscale=False,
                cache=False,
            )
            # self._viewer.dims.axis_labels = ["time", "y", "x"]
            # self._viewer.dims.current_step = (0,) + self._viewer.dims.current_step[1:]
        for layer in self._viewer.layers:
            layer.refresh()

    def update_img(self):
        img = self._relay.get("img")
        self._viewer.layers[0].data = img


def acquire(ctrl, file, acq_func, overlap=None, top_left=None, bot_right=None):
    tile = ctrl.snap()
    pos = [None, None]
    acq_event = threading.Event()
    if (top_left is None or bot_right is None) and overlap is not None:
        get_pos = True
    else:
        acq_event.set()
        get_pos = False

    gui = GUI(lambda v, r: AcqClient(v, r, file=file), file, ctrl.snap())

    @gui.worker
    def acq():
        while not acq_event.is_set():
            tile[:] = ctrl.snap()
            yield

        xs, ys = pos
        store = zr.DirectoryStore(file)
        for x in acq_func(gui, xs, ys):
            for name, xp in gui.arrays.items():
                xp.to_zarr(store, group=name, compute=False, mode="a")
            yield

    @gui.route("valves")
    def get_valves():
        return ctrl.valves.valves

    @gui.route("set_valve")
    def set_valve(idx, value):
        ctrl.valves[idx] = value

    @gui.route("acq")
    def start_acq(top_left, bot_right):
        if overlap is None:
            xs = np.array([ctrl.x])
            ys = np.array([ctrl.y])
        else:
            tile = ctrl.snap()
            width = tile.shape[1]
            height = tile.shape[0]
            overlap_x = int(round(overlap * width))
            overlap_y = int(round(overlap * height))
            delta_x = (width - overlap_x) * ctrl.px_len
            delta_y = (height - overlap_y) * ctrl.px_len
            xs = np.arange(top_left[0], bot_right[0] + delta_x - 1, delta_x)
            ys = np.arange(top_left[1], bot_right[1] + delta_y - 1, delta_y)

        pos[0] = xs
        pos[1] = ys
        acq_event.set()

    @gui.route("arrays")
    def get_arrays():
        return set(gui.arrays.keys())

    @gui.route("img")
    def get_img():
        return tile

    @gui.route("xy")
    def get_xy():
        return ctrl.xy

    gui.start()
    return gui


class DiskArray(da.core.Array):
    __slots__ = tuple()

    def __setitem__(self, key, value):
        self._zarr_array[key] = value


def tiles_to_image(xp):
    if "overlap" not in xp:
        return xp.tile

    if xp.overlap != 0:
        overlap_y = int(round(xp.overlap * xp.tile.shape[-2]))
        overlap_x = int(round(xp.overlap * xp.tile.shape[-1]))
        img = xp.tile[..., :-overlap_y, :-overlap_x]
    else:
        img = xp.tile

    img = img.transpose("tile_row", "tile_col", "tile_y", "tile_x", "channel", "time")
    img = xr.concat(img, dim="tile_y")
    img = xr.concat(img, dim="tile_x")
    img = img.rename(tile_y="im_y", tile_x="im_x")
    img = img.transpose("channel", "time", "im_y", "im_x")
    return img
