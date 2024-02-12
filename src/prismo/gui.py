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
                yield control.snap()
            except Exception as e:
                print(e)
                yield

    worker = snap_img()
    return viewer, worker

def tile_acq(ctrl, file, top_left, bot_right, overlap, time=None, channel=None):
    tile = ctrl.snap()
    width = tile.shape[1]
    height = tile.shape[0]
    overlap_x = np.round(overlap * width)
    overlap_y = np.round(overlap * height)
    delta_x = (width - overlap_x) * ureg.px * ctrl.px_len
    delta_y = (height - overlap_y) * ureg.px * ctrl.px_len
    xs = np.arange(top_left[0], bot_right[0], delta_x.to("um").magnitude)
    ys = np.arange(top_left[1], bot_right[1], delta_y.to("um").magnitude)

    if time is None:
        time = {"default": {}}
    if channel is None:
        channel = {"default": {}}

    shape = (len(time), len(channel), len(ys), len(xs), tile.shape[0], tile.shape[1])
    chunks = (1, 1, 1, 1, tile.shape[0], tile.shape[1])
    xp = xr.Dataset({"tile": (("time", "channel", "tile_row", "tile_col", "tile_y", "tile_x"), da.zeros(shape=shape, chunks=chunks, dtype=tile.dtype))}, {"time": list(time.keys()), "channel": list(channel.keys())})

    store = zr.DirectoryStore(file)
    compressor = numcodecs.Blosc(cname="zstd", clevel=5, shuffle=numcodecs.Blosc.BITSHUFFLE)
    xp.to_zarr(store, compute=False, encoding={"tile": {"compressor": compressor}})
    tiles = zr.open(file + "/tile", fill_value=0, mode="a")
    tiles.fill_value = 0
    xp.tile.data = da.from_zarr(tiles)
    img = xp.tile[..., : ].transpose("tile_row", "tile_col", "tile_y", "tile_x", "channel", "time")
    img = xr.concat(img, dim="tile_y")
    img = xr.concat(img, dim="tile_x")
    img = img.rename(tile_y="im_y", tile_x="im_x")
    img = img.transpose("channel", "time", "im_y", "im_x")
    xp["image"] = img

    viewer = napari.view_image(img, contrast_limits=[tile.min(), tile.max()], multiscale=False, cache=False)
    def update_img(args):
        img, idx = args
        tiles[idx] = img
        viewer.layers[0].refresh()

    import time as tm
    @thread_worker(connect={"yielded": update_img})
    def acquire():
        for j, t in enumerate(time):
            for k, y in enumerate(ys):
                iter = list(enumerate(xs))
                if k % 2 == 1:
                    iter = reversed(iter)
                for l, x in iter:
                    for i, c in enumerate(channel):
                        tm.sleep(3)
                        try:
                            yield (ctrl.snap(), (i, j, k, l))
                        except Exception as e:
                            print(e)
                            yield

    acquire()
    return xp, viewer
