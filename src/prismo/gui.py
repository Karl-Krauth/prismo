import threading

from qtpy.QtCore import QTimer
from zarr.errors import ContainsGroupError
import dask.array as da
import dill
import multiprocess
import napari
import numcodecs
import numpy as np
import xarray as xr
import zarr as zr

from .widgets import BoundarySelector, PositionSelector, init_widgets


class Relay:
    def __init__(self, pipe):
        self._pipe = pipe

    def get(self, route, *args, **kwargs):
        self._pipe.send([route, args, kwargs])
        return self._pipe.recv()

    def post(self, route, *args, **kwargs):
        self._pipe.send([route, args, kwargs])


class GUI:
    def __init__(self, init_client, file=None, tile=None, attrs=None):
        def run_gui(pipe):
            viewer = napari.Viewer()
            relay = Relay(pipe)
            # Save the client in a variable so it doesn't get garbage collected.
            client = init_client(viewer, relay)
            napari.run()
            pipe.close()

        def run_router(pipe, running, quit):
            while not quit.is_set():
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
        self._attrs = attrs if attrs is not None else {}

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

    def route(self, name, func=None):
        if func is None:
            # route got called as a decorator.
            def decorator(func):
                self._routes[name] = func
                return func

            return decorator
        else:
            # route got called as a standard method.
            self._routes[name] = func

    def array(self, name, **dims):
        shape = tuple(x if isinstance(x, int) else len(x) for x in dims.values())
        xp = xr.DataArray(
            data=da.zeros(
                shape=shape + self._tile.shape,
                chunks=(1,) * len(dims) + self._tile.shape,
                dtype=self._tile.dtype,
            ),
            dims=tuple(dims.keys()) + ("y", "x"),
            name=name,
        )

        for dim_name, coords in dims.items():
            if not isinstance(coords, int):
                xp.coords[dim_name] = coords

        store = zr.DirectoryStore(self._file)
        compressor = numcodecs.Blosc(cname="zstd", clevel=5, shuffle=numcodecs.Blosc.BITSHUFFLE)

        for attr_name, attr in self._attrs.items():
            xp.attrs[attr_name] = attr

        try:
            xp.to_dataset(promote_attrs=True, name="tile").to_zarr(
                store, group=name, compute=False, encoding={"tile": {"compressor": compressor}}
            )
        except ContainsGroupError:
            raise FileExistsError(f"{self._file}/{name} already exists.")

        # Xarray/Dask don't natively support disk-writeable zarr arrays so we have to manually
        # load the zarr array and patch in a modified dask array that writes to disk when
        # __setitem__ is called.
        zarr_tiles = zr.open(
            store, path=f"{name}/tile", mode="a", synchronizer=zr.ThreadSynchronizer()
        )
        zarr_tiles.fill_value = 0
        tiles = da.from_zarr(zarr_tiles)
        tiles.__class__ = DiskArray
        tiles._zarr_array = zarr_tiles
        xp.data = tiles

        with self._array_lock:
            self._arrays[name] = xp

        return xp

    @property
    def arrays(self):
        with self._array_lock:
            arrs = dict(self._arrays)
        return arrs

    def __del__(self):
        self.quit()


class LiveClient:
    def __init__(self, viewer, relay, widgets):
        self._viewer = viewer
        self._relay = relay
        img = self._relay.get("img")
        self._viewer.add_image(img, name="live")
        self._timer = QTimer()
        self._timer.timeout.connect(self.update_img)
        self._timer.start(1000 // 30)
        for name, widget in widgets.items():
            self._viewer.window.add_dock_widget(widget(self._relay), name=name, tabify=False)

    def update_img(self):
        img = self._relay.get("img")
        self._viewer.layers[0].data = img


def live(ctrl):
    widgets, widget_routes = init_widgets(ctrl)
    gui = GUI(lambda v, r: LiveClient(v, r, widgets=widgets))

    img = ctrl.snap()

    @gui.worker
    def snap():
        while True:
            img[:] = ctrl.snap()
            yield

    gui.route("img", lambda: img)
    for name, func in widget_routes.items():
        gui.route(name, func)

    gui.start()

    return gui


class AcqClient:
    def __init__(self, viewer, relay, file, widgets, tiled=False, multi=False):
        self._viewer = viewer
        self._relay = relay
        self._file = file
        self._live_timer = QTimer()
        self._refresh_timer = QTimer()
        self._arrays = set()

        if tiled or multi:
            img = self._relay.get("img")
            self._viewer.add_image(img, name="live")
            self._live_timer.timeout.connect(self.update_img)
            self._live_timer.start(1000 // 30)
            if tiled:
                self._viewer.window.add_dock_widget(
                    BoundarySelector(self._relay, self.start_acq),
                    name="Acquisition Boundaries",
                    tabify=False,
                )
            elif multi:
                self._viewer.window.add_dock_widget(
                    PositionSelector(self._relay, self.start_acq),
                    name="Acquisition Positions",
                    tabify=False,
                )
        else:
            self._refresh_timer.timeout.connect(self.refresh)
            self._refresh_timer.start(100)

        for name, widget in widgets.items():
            self._viewer.window.add_dock_widget(widget(self._relay), name=name, tabify=False)

    def start_acq(self, *args):
        self._live_timer.disconnect()
        self._live_timer.stop()
        self._viewer.layers.remove("live")

        self._relay.post("start_acq", *args)
        self._refresh_timer.timeout.connect(self.refresh)
        self._refresh_timer.start(100)

    def refresh(self):
        arrays = self._relay.get("arrays")
        new_arrays = arrays - self._arrays
        first_images = len(self._arrays) == 0
        self._arrays = arrays.union(self._arrays)
        for arr in new_arrays:
            xp = xr.open_zarr(self._file, group=arr)
            xp = xp["tile"].assign_attrs(xp.attrs)
            img = tiles_to_image(xp)

            layer_names = arr
            if "channel" in img.dims:
                layer_names = [f"{arr}: {c}" for c in xp.coords["channel"].to_numpy()]

            viewer_dims = self._viewer.dims.axis_labels[:-2] + ("y", "x")
            img = img.expand_dims([d for d in viewer_dims if d not in img.dims])
            img = img.transpose("channel", ..., *viewer_dims, missing_dims="ignore")

            layers = self._viewer.add_image(
                img,
                channel_axis=0 if "channel" in img.dims else None,
                name=layer_names,
                multiscale=False,
                cache=False,
            )
            layers = layers if isinstance(layers, list) else [layers]

            for layer in layers:
                # Turn on auto-contrast for all new layers.
                self._viewer.window._qt_viewer._controls.widgets[
                    layer
                ].autoScaleBar._auto_btn.click()

            new_dims = tuple(d for d in img.dims if d not in viewer_dims and d != "channel")
            self._viewer.dims.axis_labels = new_dims + viewer_dims
            # Make sure new dimension sliders get initialized to be 0.
            self._viewer.dims.current_step = (0,) * len(new_dims) + self._viewer.dims.current_step[
                -len(new_dims) :
            ]
        for layer in self._viewer.layers:
            layer.refresh()

    def update_img(self):
        img = self._relay.get("img")
        self._viewer.layers[0].data = img


def acq(ctrl, file, acq_func):
    widgets, widget_routes = init_widgets(ctrl)
    gui = GUI(
        lambda v, r: AcqClient(v, r, file=file, widgets=widgets),
        file,
        ctrl.snap(),
        dict(acq_func=dill.source.getsource(acq_func)),
    )

    @gui.worker
    def acq():
        store = zr.DirectoryStore(file)
        for x in acq_func(gui):
            for name, xp in gui.arrays.items():
                xp.to_dataset(promote_attrs=True).to_zarr(
                    store, group=name, compute=False, mode="a"
                )
            yield

    gui.route("arrays", lambda: set(gui.arrays.keys()))
    for name, func in widget_routes.items():
        gui.route(name, func)

    gui.start()
    return gui


def multi_acq(ctrl, file, acq_func, overlap=0.0):
    tile = ctrl.snap()
    pos = [None]
    acq_event = threading.Event()

    widgets, widget_routes = init_widgets(ctrl)
    gui = GUI(
        lambda v, r: AcqClient(v, r, file=file, widgets=widgets, multi=True),
        file,
        ctrl.snap(),
        dict(overlap=overlap, acq_func=dill.source.getsource(acq_func)),
    )

    @gui.worker
    def acq():
        while not acq_event.is_set():
            tile[:] = ctrl.snap()
            yield

        store = zr.DirectoryStore(file)
        for x in acq_func(gui, pos[0]):
            for name, xp in gui.arrays.items():
                xp.to_dataset(promote_attrs=True).to_zarr(
                    store, group=name, compute=False, mode="a"
                )
            yield

    @gui.route("start_acq")
    def start_acq(xys):
        pos[0] = xys
        acq_event.set()

    gui.route("img", lambda: tile)
    gui.route("xy", lambda: ctrl.xy)
    gui.route("arrays", lambda: set(gui.arrays.keys()))
    for name, func in widget_routes.items():
        gui.route(name, func)

    gui.start()
    return gui


def tiled_acq(ctrl, file, acq_func, overlap, top_left=None, bot_right=None):
    tile = ctrl.snap()
    pos = [None, None]
    get_pos = top_left is None or bot_right is None
    acq_event = threading.Event()

    widgets, widget_routes = init_widgets(ctrl)
    gui = GUI(
        lambda v, r: AcqClient(v, r, file=file, widgets=widgets, tiled=get_pos),
        file,
        ctrl.snap(),
        dict(overlap=overlap, acq_func=dill.source.getsource(acq_func)),
    )

    @gui.worker
    def acq():
        if get_pos:
            while not acq_event.is_set():
                tile[:] = ctrl.snap()
                yield
            xs, ys = pos
        else:
            xs, ys = tile_coords(ctrl, top_left, bot_right, overlap)

        store = zr.DirectoryStore(file)
        for x in acq_func(gui, xs, ys):
            for name, xp in gui.arrays.items():
                xp.to_dataset(promote_attrs=True).to_zarr(
                    store, group=name, compute=False, mode="a"
                )
            yield

    @gui.route("start_acq")
    def start_acq(top_left, bot_right):
        xs, ys = tile_coords(ctrl, top_left, bot_right, overlap)
        pos[0] = xs
        pos[1] = ys
        acq_event.set()

    gui.route("img", lambda: tile)
    gui.route("xy", lambda: ctrl.xy)
    gui.route("arrays", lambda: set(gui.arrays.keys()))
    for name, func in widget_routes.items():
        gui.route(name, func)

    gui.start()
    return gui


class DiskArray(da.core.Array):
    __slots__ = tuple()

    def __setitem__(self, key, value):
        self._zarr_array[key] = value


def tile_coords(ctrl, top_left, bot_right, overlap):
    tile = ctrl.snap()
    width = tile.shape[1]
    height = tile.shape[0]
    overlap_x = int(round(overlap * width))
    overlap_y = int(round(overlap * height))
    delta_x = (width - overlap_x) * ctrl.px_len
    delta_y = (height - overlap_y) * ctrl.px_len
    xs = np.arange(top_left[0], bot_right[0] + delta_x - 1, delta_x)
    ys = np.arange(top_left[1], bot_right[1] + delta_y - 1, delta_y)
    return xs, ys


def tiles_to_image(xp):
    if "overlap" not in xp.attrs:
        return xp.transpose(..., "y", "x")

    if xp.attrs["overlap"] != 0:
        overlap_y = int(round(xp.attrs["overlap"] * xp.shape[-2]))
        overlap_x = int(round(xp.attrs["overlap"] * xp.shape[-1]))
        img = xp[..., :-overlap_y, :-overlap_x]
    else:
        img = xp

    if "row" in img.dims:
        img = img.transpose("row", "y", ...)
        img = xr.concat(img, dim="y")
    if "col" in img.dims:
        img = img.transpose("col", "x", ...)
        img = xr.concat(img, dim="x")

    img = img.transpose(..., "y", "x")
    return img
