import collections
import os

import numpy as np
import pymmcore


def load(config, path=None):
    core = pymmcore.CMMCore()
    if path is None:
        if os.name == "nt":
            path = "C:/Program Files/Micro-Manager-2.0"
        else:
            path = "/usr/local/lib/micro-manager"

    os.environ["PATH"] += os.pathsep + path
    core.setDeviceAdapterSearchPaths([path])

    cameras = []
    stages = []
    selectors = []
    loaded = set()
    D = collections.namedtuple("Device", ["parent", "type", "module", "device"])
    devices = {
        "andor_zyla_camera": D(None, "camera", "AndorSDK3", "Andor sCMOS Camera"),
        "mm_demo_camera": D(None, "camera", "DemoCamera", "DCam"),
        "mm_demo_filter": D(None, "selector", "DemoCamera", "DWheel"),
        "mm_demo_stage": D(None, "stage", "DemoCamera", "DXYStage"),
        "nikon_ti_hub": D(None, "hub", "NikonTI", "TIScope"),
        "nikon_ti_filter1": D("nikon_ti_hub", "selector", "NikonTI", "TIFilterBlock1"),
        "nikon_ti_filter2": D("nikon_ti_hub", "selector", "NikonTI", "TIFilterBlock2"),
        "nikon_ti_objective": D("nikon_ti_hub", "selector", "NikonTI", "TINosePiece"),
    }

    def load_device(name, params):
        device_id = params["device"]
        if device_id not in devices:
            raise ValueError(f"Device {device_id} is not recognized.")
        device = devices[device_id]

        if device.parent is not None and device.parent not in loaded:
            load_device(device.parent, {"device": device.parent})

        core.loadDevice(name, device.module, device.device)
        core.initializeDevice(name)
        loaded.add(device_id)

        if device.type == "camera":
            cameras.append(Camera(name, core))
        elif device.type == "stage":
            stages.append(Stage(name, core))
        elif device.type == "selector":
            selectors.append(Selector(name, core, params.get("states")))

    for name, params in config.items():
        try:
            load_device(name, params)
        except Exception as e:
            core.reset()
            raise e

    return Control(core, cameras=cameras, stages=stages, selectors=selectors)


def to_list(l):
    if l is None:
        return []
    return l

class Control:
    def __init__(self, core, cameras=None, stages=None, selectors=None):
        super(Control, self).__setattr__("selectors", to_list(selectors))
        self.cameras = to_list(cameras)
        self.stages = to_list(stages)
        self._core = core

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
        for selector in self.selectors:
            if name == selector.name:
                return selector.state

        for camera in self.cameras:
            if name == camera.name:
                return camera

        for stage in self.stages:
            if name == stage.name:
                return stage

        return self.__getattribute__(name)

    def __setattr__(self, name, value):
        for selector in self.selectors:
            if name == selector.name:
                selector.state = value
                return
        super(Control, self).__setattr__(name, value)

    def close(self):
        self._core.reset()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._core.reset()

    def __del__(self):
        self._core.reset()


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


class Selector:
    def __init__(self, name, core, states=None):
        self.name = name
        self.states = states
        self._core = core

        n_states = self._core.getNumberOfStates(name)
        if states is None:
            self.states = [i for i in range(n_states)]
        else:
            if len(self.states) < n_states:
                raise ValueError(f"{name} requires {n_states} states (not {len(self.states)}) to be specified.")
            for i, state in enumerate(self.states):
                self._core.defineStateLabel(name, i, state)

    @property
    def state(self):
        if isinstance(self.states[0], int):
            return self._core.getState(self.name)
        else:
            return self._core.getStateLabel(self.name)

    @state.setter
    def state(self, new_state):
        if isinstance(new_state, int):
            self._core.setState(self.name, new_state)
        else:
            self._core.setStateLabel(self.name, new_state)
