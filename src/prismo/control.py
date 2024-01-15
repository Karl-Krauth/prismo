import numpy as np
import pymmcore


def load(config):
    core = pymmcore.CMMCore()
    core.setDeviceAdapterSearchPaths(["/usr/local/lib/micro-manager"])
    cameras = []
    stages = []
    filters = []
    for name, params in config.items():
        device = params["device"]
        if device == "demo_camera":
            core.loadDevice(name, "DemoCamera", "DCam")
            core.initializeDevice(name)
            cameras.append(Camera(name, core))
        elif device == "demo_stage":
            core.loadDevice(name, "DemoCamera", "DXYStage")
            core.initializeDevice(name)
            stages.append(Stage(name, core))
        elif device == "demo_filter":
            core.loadDevice(name, "DemoCamera", "DWheel")
            core.initializeDevice(name)
            filters.append(Filter(name, core, params.get("channels")))

    return Control(cameras=cameras, stages=stages, filters=filters)


def to_list(l):
    if l is None:
        return []
    return l

class Control:
    def __init__(self, cameras=None, stages=None, filters=None):
        super(Control, self).__setattr__("filters", to_list(filters))
        self.cameras = to_list(cameras)
        self.stages = to_list(stages)

        if self.cameras is not None:
            self._camera_idx = 0
        else:
            self._camera_idx = None

        if self.stages is not None:
            self._stage_idx = 0
        else:
            self._stage_idx = None

    @property
    def default_camera(self):
        if len(self.cameras) == 0:
            return None
        else:
            return self.cameras[self._camera_idx].name

    @default_camera.setter
    def default_camera(self, new_camera):
        for i, camera in enumerate(self.cameras):
            if camera.name == new_camera:
                self._camera_idx = i

    def snap(self):
        return self.cameras[self._camera_idx].snap()

    @property
    def default_stage(self):
        return self.stages[self._stage_idx].name

    @default_stage.setter
    def default_stage(self, new_stage):
        for i, stage in enumerate(self.stages):
            if stage.name == new_stage:
                self._stage_idx = i

    @property
    def x(self):
        return self.stages[self._stage_idx].x

    @x.setter
    def x(self, new_x):
        self.stages[self._stage_idx].x = new_x

    @property
    def y(self):
        return self.stages[self._stage_idx].y

    @y.setter
    def y(self, new_y):
        self.stages[self._stage_idx].y = new_y

    @property
    def xy(self):
        return self.stages[self._stage_idx].xy

    @xy.setter
    def xy(self, new_xy):
        self.stages[self._stage_idx].xy = new_xy

    def __getattr__(self, name):
        for filter in self.filters:
            if name == filter.name:
                return filter.channel

        for camera in self.cameras:
            if name == camera.name:
                return camera

        for stage in self.stages:
            if name == stage.name:
                return stage

        return self.__getattribute__(name)

    def __setattr__(self, name, value):
        for filter in self.filters:
            if name == filter.name:
                filter.channel = value
                return
        super(Control, self).__setattr__(name, value)


class Camera:
    def __init__(self, name, core):
        self.name = name
        self._core = core

    def snap(self):
        self._core.setCameraDevice(self.name)
        self._core.snapImage()
        return self._core.getImage()


class Stage:
    def __init__(self, name, core):
        self.name = name
        self._core = core

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


class Filter:
    def __init__(self, name, core, channels=None):
        self.name = name
        self.channels = channels
        self._core = core

        n_channels = self._core.getNumberOfStates(name)
        if channels is None:
            self.channels = [i for i in range(n_channels)]
        else:
            if len(self.channels) < n_channels:
                raise ValueError(f"Filter {name} has more channels than specified.")
            for i, channel in enumerate(self.channels):
                self._core.defineStateLabel(name, i, channel)

    @property
    def channel(self):
        if isinstance(self.channels[0], int):
            return self._core.getState(self.name)
        else:
            return self._core.getStateLabel(self.name)

    @channel.setter
    def channel(self, new_channel):
        if isinstance(new_channel, int):
            self._core.setState(self.name, new_channel)
        else:
            self._core.setStateLabel(self.name, new_channel)
