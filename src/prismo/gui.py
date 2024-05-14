import multiprocess
import time

from magicgui import widgets
from napari.qt.threading import thread_worker, create_worker
from qtpy import QtCore
from qtpy.QtCore import Qt
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


class GUI:
    def __init__(self, worker_func, gui_func, update_func):
        def run_gui(pipe):
            viewer = napari.Viewer()
            def update(args):
                if isinstance(args, tuple):
                    update_func(viewer, *args)
                elif args is not None:
                    update_func(viewer, args)

            @thread_worker
            def receive():
                while True:
                    if pipe.poll(1):
                        yield pipe.recv()
                    else:
                        yield

            receiver = receive()
            receiver.yielded.connect(update)
            receiver.start()
            gui_func(viewer)
            napari.run()
            receiver.quit()
            pipe.close()

        def run_worker(pipe, running, quit):
            for x in worker_func():
                running.wait()
                if quit.is_set():
                    break
                try:
                    pipe.send(x)
                except (BrokenPipeError, IOError):
                    break

        self._running = threading.Event()
        self._running.set()
        self._quit = threading.Event()
        ctx = multiprocess.get_context("spawn")
        self._pipe, child_pipe = ctx.Pipe()
        self._gui_process = ctx.Process(target=run_gui, args=(child_pipe,))
        self._worker_thread = threading.Thread(target=run_worker, args=(self._pipe, self._running, self._quit))
        print("c")

    def start(self):
        self._gui_process.start()
        self._worker_thread.start()

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

    def __del__(self):
        self.quit()

def live(ctrl):
    def snap_img():
        while True:
            ctrl.wait()
            yield ctrl.snap()

    def init_gui(viewer):
        pass

    def update_img(viewer, img):
        if "live" in viewer.layers:
            viewer.layers[0].data = img
        else:
            viewer.add_image(img, name="live")

    gui = GUI(snap_img, init_gui, update_img)
    gui.start()

    return gui

def expand_config(config):
    new_config = {}
    for k, v in config.items():
        if isinstance(v, dict):
            new_config[k] = expand_config(v)
        elif "." in k:
            keys = k.split(".")
            new_config[keys[0]] = {keys[1]: v}
        else:
            new_config[k] = v
    return new_config


def merge_configs(config, default):
    new_config = {**default, **config}
    for k, v in new_config.items():
        if isinstance(v, dict) and k in default and k in config:
            new_config[k] = merge_configs(config[k], default[k])
    return new_config


def set_config(prop, config, c):
    for k, v in config.items():
        if isinstance(v, dict):
            set_config(prop.__getattr__(k), v, c)
        else:
            c.wait()
            prop.__setattr__(k, v)


def control_widget(ctrl):
    x = widgets.LineEdit(value=ctrl.x, label="x")
    y = widgets.LineEdit(value=ctrl.y, label="y")

    @x.changed.connect
    def on_change_x(value):
        ctrl.x = value

    @y.changed.connect
    def on_change_y(value):
        ctrl.y = value

    @thread_worker(connect={})
    def poll_ctrl():
        while True:
            x.value = ctrl.x
            y.value = ctrl.y
            time.sleep(0.1)
            yield

    worker = poll_ctrl()
    return widgets.Container(widgets=[x, y])


def acquire(ctrl, file, overlap=None, times=None, channels=None, default=None, top_left=None, bot_right=None):
    if (top_left is None or bot_right is None) and overlap is not None:
        viewer, worker = live(ctrl)

        def on_tile(top_left, bot_right):
            nonlocal viewer, worker
            worker.quit()
            viewer.layers.remove("live")
            # TODO: We need to find a way to return the xarray dataset and the worker to the caller
            # of the parent function. We can probably just make the dataset here and modify it in place
            # in the worker.
            xp, viewer = tile_acq(
                ctrl,
                file,
                top_left,
                bot_right,
                overlap,
                times=times,
                channels=channels,
                default=default,
                viewer=viewer,
            )

        viewer.window.add_dock_widget(tile_widget(ctrl, viewer, on_tile), name="Acquisition Boundaries")
    else:
        xp, viewer = tile_acq(
            ctrl,
            file,
            top_left,
            bot_right,
            overlap,
            times=times,
            channels=channels,
            default=default,
        )


def tile_widget(ctrl, viewer, callback):
    left_x = QLineEdit()
    left_x.setValidator(QDoubleValidator())
    left_y = QLineEdit()
    left_y.setValidator(QDoubleValidator())
    left_btn = QPushButton("Set")
    left_btn.setMinimumWidth(50)

    right_x = QLineEdit()
    right_x.setValidator(QDoubleValidator())
    right_y = QLineEdit()
    right_y.setValidator(QDoubleValidator())
    right_btn = QPushButton("Set")
    right_btn.setMinimumWidth(50)

    continue_btn = QPushButton("Continue")

    widget = QWidget()
    widget.setMaximumHeight(150)
    layout = QGridLayout(widget)

    layout.addWidget(QLabel("x"), 0, 1, alignment=Qt.AlignHCenter)
    layout.addWidget(QLabel("y"), 0, 2, alignment=Qt.AlignHCenter)
    layout.addWidget(QLabel("Top Left"), 1, 0)
    layout.addWidget(left_x, 1, 1)
    layout.addWidget(left_y, 1, 2)
    layout.addWidget(left_btn, 1, 3)

    layout.addWidget(QLabel("Bottom Right"), 2, 0)
    layout.addWidget(right_x, 2, 1)
    layout.addWidget(right_y, 2, 2)
    layout.addWidget(right_btn, 2, 3)

    layout.addWidget(continue_btn, 3, 0)

    layout.setColumnMinimumWidth(3, 60)
    layout.setHorizontalSpacing(10)

    def on_set_left():
        left_x.setText(str(ctrl.x))
        left_y.setText(str(ctrl.y))

    def on_set_right():
        right_x.setText(str(ctrl.x))
        right_y.setText(str(ctrl.y))

    def on_continue():
        if left_x.text() and left_y.text() and right_x.text() and right_y.text():
            widget.close()
            viewer.window.remove_dock_widget(widget)
            callback(
                (float(left_x.text()), float(left_y.text())),
                (float(right_x.text()), float(right_y.text())),
            )
        else:
            for w in [left_x, left_y, right_x, right_y]:
                if not w.text():
                    w.setStyleSheet("border: 1px solid red;")
                else:
                    w.setStyleSheet("border: 0px;")

    left_btn.clicked.connect(on_set_left)
    right_btn.clicked.connect(on_set_right)
    continue_btn.clicked.connect(on_continue)

    return widget


def tile_acq(
    ctrl, file, top_left, bot_right, overlap=None, times=None, channels=None, default=None, viewer=None
):
    tile = ctrl.snap()
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

    if times is None:
        times = {"0s": {}}
    if channels is None:
        channels = {"default": {}}
    if default is None:
        default = {}
    default = expand_config(default)
    #  times = {
    #      ureg(k).to("s").magnitude if isinstance(k, str) else k: v
    #     for k, v in expand_config(times).items()
    # }
    acq_times = {}
    for k, v in times.items():
        times[k]["wait"] = ureg(times[k]["wait"]).to("s").magnitude
        if "acq" in v:
            acq_times[k] = v
    channels = expand_config(channels)

    xp = xr.Dataset(
        {
            "tile": (
                ("channel", "time", "tile_row", "tile_col", "tile_y", "tile_x"),
                da.zeros(
                    shape=(
                        len(channels),
                        len(acq_times),
                        len(ys),
                        len(xs),
                        tile.shape[0],
                        tile.shape[1],
                    ),
                    chunks=(1, 1, 1, 1, tile.shape[0], tile.shape[1]),
                    dtype=tile.dtype,
                ),
            ),
        },
        {
            "time": list(acq_times.keys()),
            "channel": list(channels.keys()),
        },
        {
            "default_state": default,
            "time_states": times,
            "channel_states": channels,
            "overlap": overlap,
        },
    )

    store = zr.DirectoryStore(file)
    compressor = numcodecs.Blosc(cname="zstd", clevel=5, shuffle=numcodecs.Blosc.BITSHUFFLE)
    xp.to_zarr(store, compute=False, encoding={"tile": {"compressor": compressor}})

    tiles = zr.open(file + "/tile", mode="a", synchronizer=zr.ThreadSynchronizer())
    tiles.fill_value = 0
    xp.tile.data = da.from_zarr(tiles)

    if overlap is not None and overlap != 0:
        img = xp.tile[..., : -overlap_y, : -overlap_x]
    else:
        img = xp.tile
    img = img.transpose("tile_row", "tile_col", "tile_y", "tile_x", "channel", "time")
    img = xr.concat(img, dim="tile_y")
    img = xr.concat(img, dim="tile_x")
    img = img.rename(tile_y="im_y", tile_x="im_x")
    img = img.transpose("channel", "time", "im_y", "im_x")
    xp["image"] = img

    if viewer is None:
        viewer = napari.Viewer()
    viewer.add_image(
        img,
        channel_axis=0,
        name=list(channels.keys()),
        multiscale=False,
        cache=False,
    )
    viewer.dims.axis_labels = ["time", "y", "x"]
    viewer.dims.current_step = (0,) + viewer.dims.current_step[1:]

    def update_img(args):
        if args is None:
            return

        img, idxs = args
        tiles[idxs] = img
        layer = viewer.layers[idxs[0]]
        if idxs[1] == 0 and idxs[2] == 0 and idxs[3] == 0:
            layer.contrast_limits = (img.min(), img.max())
        layer.refresh()

    def acq(channel=None, time=None, y=None, x=None):
        if isinstance(channel, str):
            channel = list(channels.keys()).index(channel)

    @thread_worker(connect={"yielded": update_img})
    def acquire():
        dts = xr.Dataset(
            {
                "datetime": (
                    ("channel", "time", "tile_col", "tile_row"),
                    np.zeros((len(channels), len(acq_times), len(ys), len(xs)), dtype="datetime64[ns]"),
                )
            }
        )
        start_time = time.time()
        set_config(ctrl, default, ctrl)
        j_true = -1
        for j, (t, time_state) in enumerate(times.items()):
            # delta_t = t # t - (time.time() - start_time)
            delta_t = time_state["wait"]
            del time_state["wait"]
            do_acq = "acq" in time_state
            if do_acq:
                del time_state["acq"]
            time_state = merge_configs(time_state, default)
            ctrl.wait()
            set_config(ctrl, time_state, ctrl)
            if delta_t >= 0:
                time.sleep(delta_t)
                yield
            if not do_acq:
                continue
            j_true += 1
            for k, y in enumerate(ys):
                iter = list(enumerate(xs))
                if k % 2 == 1:
                    iter = reversed(iter)
                for l, x in iter:
                    ctrl.wait()
                    ctrl.xy = (x, y)
                    time.sleep(1)
                    for i, c in enumerate(channels.values()):
                        ctrl.wait()
                        set_config(ctrl, merge_configs(c, time_state), ctrl)
                        for tries in range(10):
                            try:
                                time.sleep(0.2)
                                ctrl.wait()
                                yield (ctrl.snap(), (i, j_true, k, l))
                                break
                            except Exception as e:
                                if tries == 9:
                                    raise e
                        # dts.datetime[i, j, k, l] = np.datetime64(time.time_ns(), "ns")
                        set_config(ctrl, default, ctrl)
                        # dts.to_zarr(store, mode="a")
        set_config(ctrl, default, ctrl)

    acquire()
    return xp, viewer
