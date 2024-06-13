import dill
import multiprocess
import time

from magicgui import widgets
from napari.qt.threading import thread_worker, create_worker
from qtpy import QtCore
from qtpy.QtCore import Qt, QTimer
from qtpy.QtWidgets import (
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
)
from qtpy.QtGui import QDoubleValidator
import napari
import dask.array as da
import numcodecs
import numpy as np
import threading
import xarray as xr
import zarr as zr

from units import ureg


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
    def __init__(self, gui_func):
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

        img = self._relay.get("img")
        self._viewer.add_image(img, name="live")

        self._live_timer.timeout.connect(self.update_img)
        self._live_timer.start(1000 // 60)
        self._viewer.window.add_dock_widget(
            TileWidget(self._relay, self.acq_step), name="Acquisition Boundaries"
        )

    def acq_step(self, top_left, bot_right):
        self._live_timer.disconnect()
        self._live_timer.stop()
        self._viewer.layers.remove("live")

        success = self._relay.get("acq", top_left, bot_right)
        if not success:
            return

        timer = QTimer()
        timer.timeout.connect(self.refresh)
        timer.start(1000)

        xp = xr.open_zarr(self._file)
        xp["image"] = tiles_to_image(xp)
        self._viewer.add_image(
            xp["image"],
            channel_axis=0,
            name=list(xp.channel.to_numpy()),
            multiscale=False,
            cache=False,
        )
        self._viewer.dims.axis_labels = ["time", "y", "x"]
        self._viewer.dims.current_step = (0,) + self._viewer.dims.current_step[1:]

    def refresh(self):
        for layer in self._viewer.layers:
            layer.refresh()

    def update_img(self):
        img = self._relay.get("img")
        self._viewer.layers[0].data = img


def acquire(ctrl, file, acq_func, times=1, channels=1, overlap=None, top_left=None, bot_right=None):
    tile = ctrl.snap()
    xp = xr.Dataset()
    acq_event = threading.Event()
    if (top_left is None or bot_right is None) and overlap is not None:
        get_pos = True
    else:
        acq_event.set()
        get_pos = False

    if isinstance(times, int):
        times = np.arange(times, dtype=int)

    if isinstance(channels, int):
        channels = np.arange(channels, dtype=int)

    gui = GUI(lambda v, r: AcqClient(v, r, file=file))

    @gui.worker
    def acq():
        while not acq_event.is_set():
            tile[:] = ctrl.snap()
            yield

        for x in acq_func(xp, xs, ys):
            yield

    @gui.route("acq")
    def start_acq(top_left, bot_right):
        if overlap is None:
            xs = np.array([ctrl.x])
            ys = np.array([ctrl.y])
        else:
            width = tile.shape[1]
            height = tile.shape[0]
            overlap_x = int(round(overlap * width))
            overlap_y = int(round(overlap * height))
            delta_x = ((width - overlap_x) * ureg.px * ctrl.px_len).to("um").magnitude
            delta_y = ((height - overlap_y) * ureg.px * ctrl.px_len).to("um").magnitude
            xs = np.arange(top_left[0], bot_right[0] + delta_x - 1, delta_x)
            ys = np.arange(top_left[1], bot_right[1] + delta_y - 1, delta_y)

        xp["tile"] = (
            ("channel", "time", "tile_row", "tile_col", "tile_y", "tile_x"),
            da.zeros(
                shape=(
                    len(channels),
                    len(times),
                    len(ys),
                    len(xs),
                    tile.shape[0],
                    tile.shape[1],
                ),
                chunks=(1, 1, 1, 1, tile.shape[0], tile.shape[1]),
                dtype=tile.dtype,
            ),
        )

        xp.coords["time"] = times
        xp.coords["channel"] = channels
        xp.attrs["acq_func"] = dill.source.getsource(acq_func)
        xp.attrs["overlap"] = overlap

        store = zr.DirectoryStore(file)
        compressor = numcodecs.Blosc(cname="zstd", clevel=5, shuffle=numcodecs.Blosc.BITSHUFFLE)
        try:
            xp.to_zarr(store, compute=False, encoding={"tile": {"compressor": compressor}})
        except:
            raise FileExistsError(f"{file} already exists.")

        zarr_tiles = zr.open(file + "/tile", mode="a", synchronizer=zr.ThreadSynchronizer())
        zarr_tiles.fill_value = 0
        tiles = da.from_zarr(zarr_tiles)
        tiles.__class__ = DiskArray
        tiles._zarr_array = zarr_tiles
        xp.tile.data = tiles

        xp["image"] = tiles_to_image(xp)
        acq_event.set()

        return True

    @gui.route("img")
    def get_img():
        return tile

    @gui.route("xy")
    def get_xy():
        return ctrl.xy

    gui.start()

    return gui, xp


class DiskArray(da.core.Array):
    __slots__ = tuple()

    def __setitem__(self, key, value):
        self._zarr_array[key] = value


def tiles_to_image(xp):
    if xp.overlap is not None and xp.overlap != 0:
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


class TileWidget(QWidget):
    def __init__(self, relay, next_step):
        super().__init__()
        self.setMaximumHeight(150)
        layout = QGridLayout(self)

        self.left_x = QLineEdit()
        self.left_x.setValidator(QDoubleValidator())
        self.left_y = QLineEdit()
        self.left_y.setValidator(QDoubleValidator())
        self.left_btn = QPushButton("Set")
        self.left_btn.setMinimumWidth(50)

        self.right_x = QLineEdit()
        self.right_x.setValidator(QDoubleValidator())
        self.right_y = QLineEdit()
        self.right_y.setValidator(QDoubleValidator())
        self.right_btn = QPushButton("Set")
        self.right_btn.setMinimumWidth(50)

        continue_btn = QPushButton("Continue")

        layout.addWidget(QLabel("x"), 0, 1, alignment=Qt.AlignHCenter)
        layout.addWidget(QLabel("y"), 0, 2, alignment=Qt.AlignHCenter)
        layout.addWidget(QLabel("Top Left"), 1, 0)
        layout.addWidget(self.left_x, 1, 1)
        layout.addWidget(self.left_y, 1, 2)
        layout.addWidget(self.left_btn, 1, 3)

        layout.addWidget(QLabel("Bottom Right"), 2, 0)
        layout.addWidget(self.right_x, 2, 1)
        layout.addWidget(self.right_y, 2, 2)
        layout.addWidget(self.right_btn, 2, 3)

        layout.addWidget(continue_btn, 3, 0)

        layout.setColumnMinimumWidth(3, 60)
        layout.setHorizontalSpacing(10)

        self.left_btn.clicked.connect(self.set_left)
        self.right_btn.clicked.connect(self.set_right)
        continue_btn.clicked.connect(self.cont)

        self._relay = relay
        self._next_step = next_step

    def set_left(self):
        xy = self._relay.get("xy")
        self.left_x.setText(str(xy[0]))
        self.left_y.setText(str(xy[1]))

    def set_right(self):
        xy = self._relay.get("xy")
        self.right_x.setText(str(xy[0]))
        self.right_y.setText(str(xy[1]))

    def cont(self):
        if (
            self.left_x.text()
            and self.left_y.text()
            and self.right_x.text()
            and self.right_y.text()
        ):
            self.close()
            self._next_step(
                (float(self.left_x.text()), float(self.left_y.text())),
                (float(self.right_x.text()), float(self.right_y.text())),
            )
        else:
            for w in [self.left_x, self.left_y, self.right_x, self.right_y]:
                if not w.text():
                    w.setStyleSheet("border: 1px solid red;")
                else:
                    w.setStyleSheet("border: 0px;")
