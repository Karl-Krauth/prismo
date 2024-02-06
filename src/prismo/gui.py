from napari.qt.threading import thread_worker
from qtpy.QtWidgets import QPushButton
import napari
import zarr as zr

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
    img = c.snap()
    width_um = img.shape[1] / ctrl.px_um
    height_um = img.shape[0] / ctrl.px_um
    delta_x = (1 - overlap) * width_um
    delta_y = (1 - overlap) * height_um
    xs = np.arange(top_left[0], bot_right[0])
    ys = np.arange(top_left[1], bot_right[1])
    

    if time is None:
        time = [{}]
    if channel is None:
        channel = [{}]
    tiles = zarr.open(file,
                      mode="w",
                      shape=(len(time), len(channel), len(ys), len(xs), img.shape[0], img.shape[1]),
                      chunks=(1, 1, 1, 1, img.shape[0], img.shape[1]),
                      dtype=img.dtype)

    viewer, layers = napari.imshow(
