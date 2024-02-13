import time

from napari.qt.threading import thread_worker
from qtpy.QtWidgets import QPushButton
import napari
import dask.array as da
import numcodecs
import numpy as np
import xarray as xr
import zarr as zr

from units import ureg


def live(ctrl):
    viewer = napari.Viewer()
    viewer.add_image(ctrl.snap())

    def update_img(img):
        viewer.layers[0].data = img

    @thread_worker(connect={"yielded": update_img})
    def snap_img():
        while True:
            try:
                ctrl.wait()
                yield ctrl.snap()
            except Exception as e:
                print(e)
                yield

    worker = snap_img()
    return viewer, worker


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


def set_config(prop, config):
    for k, v in config.items():
        print(k, v)
        if isinstance(v, dict):
            set_config(prop[k], v)
        else:
            print("Setting", k, "to", v)
            prop.__setattr__(k, v)


def tile_acq(ctrl, file, top_left, bot_right, overlap, times=None, channels=None, default=None):
    tile = ctrl.snap()
    width = tile.shape[1]
    height = tile.shape[0]
    overlap_x = np.round(overlap * width)
    overlap_y = np.round(overlap * height)
    delta_x = (width - overlap_x) * ureg.px * ctrl.px_len
    delta_y = (height - overlap_y) * ureg.px * ctrl.px_len
    xs = np.arange(top_left[0], bot_right[0], delta_x.to("um").magnitude)
    ys = np.arange(top_left[1], bot_right[1], delta_y.to("um").magnitude)

    if times is None:
        times = {"default": {}}
    if channels is None:
        channels = {"default": {}}
    if default is None:
        default = {}
    default = expand_config(default)
    times = expand_config(times)
    channels = expand_config(channels)

    xp = xr.Dataset(
        {
            "tile": (
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
        },
        {"time": list(times.keys()), "channel": list(channels.keys())},
    )
    print(xp.tile.shape)

    store = zr.DirectoryStore(file)
    compressor = numcodecs.Blosc(cname="zstd", clevel=5, shuffle=numcodecs.Blosc.BITSHUFFLE)
    xp.to_zarr(store, compute=False, encoding={"tile": {"compressor": compressor}})
    tiles = zr.open(file + "/tile", fill_value=0, mode="a")
    tiles.fill_value = 0
    xp.tile.data = da.from_zarr(tiles)
    img = xp.tile[..., :].transpose("tile_row", "tile_col", "tile_y", "tile_x", "channel", "time")
    img = xr.concat(img, dim="tile_y")
    img = xr.concat(img, dim="tile_x")
    img = img.rename(tile_y="im_y", tile_x="im_x")
    img = img.transpose("channel", "time", "im_y", "im_x")
    xp["image"] = img

    viewer = napari.view_image(
        img, contrast_limits=[tile.min(), tile.max()], multiscale=False, cache=False
    )

    def update_img(args):
        img, idx = args
        tiles[idx] = img
        viewer.layers[0].refresh()

    @thread_worker(connect={"yielded": update_img})
    def acquire():
        start_time = time.time()
        set_config(ctrl, default)
        for j, (t, time_state) in enumerate(times.items()):
            if isinstance(t, str):
                t = ureg(t).to("s").magnitude
                print(t)
            delta_t = t - (time.time() - start_time)
            if delta_t >= 0:
                print("Waiting", delta_t, "s")
                time.sleep(delta_t)

            time_state = merge_configs(time_state, default)
            ctrl.wait()
            set_config(ctrl, time_state)
            for k, y in enumerate(ys):
                iter = list(enumerate(xs))
                if k % 2 == 1:
                    iter = reversed(iter)
                for l, x in iter:
                    for i, c in enumerate(channels.values()):
                        ctrl.wait()
                        ctrl.xy = (x, y)
                        ctrl.wait()
                        set_config(ctrl, merge_configs(c, time_state))
                        try:
                            ctrl.wait()
                            print(ctrl.wheel)
                            yield (ctrl.snap(), (i, j, k, l))
                        except Exception as e:
                            print(e)
                            yield

    acquire()
    return xp, viewer
