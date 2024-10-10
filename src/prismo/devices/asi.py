import numpy as np

class Stage:
    def __init__(self, name, core, port):
        self.name = name
        self._core = core
        core.loadDevice(name, "ASIStage", "XYStage")
        core.setProperty(name, "Port", port)
        core.initializeDevice(name)

    def wait(self):
        self._core.waitForDevice(self.name)

    @property
    def x(self):
        return self._core.getXPosition(self.name)

    @x.setter
    def x(self, new_x):
        self._core.setXYPosition(self.name, new_x, self.y)

    @property
    def y(self):
        return self._core.getYPosition(self.name)

    @y.setter
    def y(self, new_y):
        self._core.setXYPosition(self.name, self.x, new_y)

    @property
    def xy(self):
        return np.array(self._core.getXYPosition(self.name))

    @xy.setter
    def xy(self, new_xy):
        self._core.setXYPosition(self.name, new_xy[0], new_xy[1])


class Focus:
    def __init__(self, name, core, port):
        self.name = name
        self._core = core
        core.loadDevice(name, "ASIStage", "ZStage")
        core.setProperty(name, "Port", port)
        core.setProperty(name, "Axis", "Z")
        core.initializeDevice(name)

    def wait(self):
        self._core.waitForDevice(self.name)

    @property
    def z(self):
        return self._core.getPosition(self.name)

    @z.setter
    def z(self, new_z):
        self._core.setPosition(self.name, new_z)
