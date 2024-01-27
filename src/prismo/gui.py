from napari.qt.threading import thread_worker
from qtpy.QtWidgets import QPushButton
import napari

def live(control):
    viewer = napari.Viewer()
    viewer.add_image(control.snap())
    button = QPushButton("STOP!")

    def update_img(img):
        viewer.layers[0].data = img

    @thread_worker(connect={"yielded": update_img})
    def snap_img():
        while True:
            yield control.snap()

    worker = snap_img()
    return viewer, worker
