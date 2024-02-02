import collections
import os
from typing import runtime_checkable, Protocol

import numpy as np
import pymmcore
import pymodbus.client


def load(config, path=None):
    client = None
    core = pymmcore.CMMCore()
    if path is None:
        if os.name == "nt":
            path = "C:/Program Files/Micro-Manager-2.0"
        else:
            path = "/usr/local/lib/micro-manager"

    os.environ["PATH"] += os.pathsep + path
    core.setDeviceAdapterSearchPaths([path])


    def set_props(name, props):
        for k, v in props.items():
            core.setProperty(name, k, v)

    devices = []
    ports = {}
    port_defaults = {
        "AnswerTimeout": "500.0",
        "BaudRate": "9600",
        "DTR": "Disable",
        "DataBits": "8",
        "DelayBetweenCharsMs": "0.0",
        "Fast USB to Serial": "Disable",
        "Handshaking": "Off",
        "Parity": "None",
        "StopBits": "1",
        "Verbose": "1",
    }
    for name, params in config.items():
        device = params.get("device")
        if device is None or device not in ("asi_stage", "lambda_filter1", "lambda_filter2", "lambda_shutter1", "lambda_shutter2", "sola_light"):
            continue
        if "port" not in params:
            raise ValueError(f"{name} requires a port to be specified.")

        port = params["port"]
        if device == "asi_stage":
            ports[port] = {**port_defaults, "AnswerTimeout": 2000.0}
        elif device in ("lambda_filter1", "lambda_filter2", "lambda_shutter1", "lambda_shutter2"):
            ports[port] = {**port_defaults, "AnswerTimeout": 2000.0, "BaudRate": 128000}
        elif device == "sola_light":
            ports[port] = dict(port_defaults)

    for port, params in ports.items():
        core.loadDevice(port, "SerialManager", port)
        if port in config:
            params.update(config[port])
        set_props(port, params)
        core.initializeDevice(port)

    for name, params in config.items():
        if name in ports:
            continue
        
        device = params["device"]
        if (device in ("ti_focus", "ti_filter1", "ti_filter2", "ti_lightpath", "ti_objective") and
            "ti_scope" not in core.getLoadedDevices()):
            core.loadDevice("ti_scope", "NikonTI", "TIScope")
            core.initializeDevice("ti_scope")
        elif (device in ("ti2_focus", "ti2_filter1", "ti2_filter2", "ti2_lightpath", "ti2_objective") and
            "ti_scope" not in core.getLoadedDevices()):
            core.loadDevice("ti_scope", "NikonTI", "TIScope")
            core.initializeDevice("ti_scope")

        if device == "asi_stage":
            core.loadDevice(name, "ASIStage", "XYStage")
            core.setProperty(name, "Port", params["port"])
            core.initializeDevice(name)
            devices.append(Stage(name, core))
        elif device == "demo_camera":
            core.loadDevice(name, "DemoCamera", "DCam")
            core.initializeDevice(name)
            devices.append(Camera(name, core))
        elif device == "demo_filter":
            core.loadDevice(name, "DemoCamera", "DWheel")
            core.initializeDevice(name)
            devices.append(Stage(name, core))
        elif device == "demo_stage":
            core.loadDevice(name, "DemoCamera", "DXYStage")
            core.initializeDevice(name)
            devices.append(Selector(name, core, states=params.get("states")))
        elif device == "lambda_filter1":
            core.loadDevice(name, "SutterLambda", "Wheel-A")
            core.setProperty(name, "Port", params["port"])
            core.initializeDevice(name)
            devices.append(Selector(name, core, states=params.get("states")))
        elif device == "lambda_filter2":
            core.loadDevice(name, "SutterLambda", "Wheel-B")
            core.setProperty(name, "Port", params["port"])
            core.initializeDevice(name)
            devices.append(Selector(name, core, states=params.get("states")))
        elif device == "lambda_filter3":
            core.loadDevice(name, "SutterLambda", "Wheel-C")
            core.setProperty(name, "Port", params["port"])
            core.initializeDevice(name)
            devices.append(Selector(name, core, states=params.get("states")))
        elif device == "lambda_shutter1":
            core.loadDevice(name, "SutterLambda", "Shutter-A")
            core.setProperty(name, "Port", params["port"])
            core.initializeDevice(name)
            devices.append(Shutter(name, core))
        elif device == "lambda_shutter2":
            core.loadDevice(name, "SutterLambda", "Shutter-B")
            core.setProperty(name, "Port", params["port"])
            core.initializeDevice(name)
            devices.append(Shutter(name, core))
        elif device == "sola_light":
            core.loadDevice(name, "LumencorSpectra", "Spectra")
            core.setProperty(name, "SetLE_Type", "Sola")
            core.setProperty(name, "Port", params["port"])
            core.initializeDevice(name)
            devices.append(SolaLight(name, core))
        elif device == "ti_filter1":
            core.loadDevice(name, "NikonTI", "TIFilterBlock1")
            core.setParentLabel(name, "ti_scope")
            core.initializeDevice(name)
            devices.append(Selector(name, core, params.get("states")))
        elif device == "ti_filter2":
            core.loadDevice(name, "NikonTI", "TIFilterBlock2")
            core.setParentLabel(name, "ti_scope")
            core.initializeDevice(name)
            devices.append(Selector(name, core, params.get("states")))
        elif device == "ti_lightpath":
            core.loadDevice(name, "NikonTI", "TILightPath")
            core.setParentLabel(name, "ti_scope")
            core.initializeDevice(name)
            devices.append(Selector(name, core, params.get("states", ["eye", "l100", "r100", "l80"])))
        elif device == "ti_focus":
            core.loadDevice(name, "NikonTI", "TIZDrive")
            core.setParentLabel(name, "ti_scope")
            core.initializeDevice(name)
            devices.append(Focus(name, core))
        elif device == "ti_objective":
            core.loadDevice(name, "NikonTI", "TINosePiece")
            core.setParentLabel(name, "ti_scope")
            core.initializeDevice(name)
            devices.append(Selector(name, core, params.get("states")))
        elif device == "ti2_filter1":
            core.loadDevice(name, "NikonTi2", "FilterTurret1")
            core.setParentLabel(name, "ti2_scope")
            core.initializeDevice(name)
            devices.append(Selector(name, core, params.get("states")))
        elif device == "ti2_filter2":
            core.loadDevice(name, "NikonTi2", "FilterTurret2")
            core.setParentLabel(name, "ti2_scope")
            core.initializeDevice(name)
            devices.append(Selector(name, core, params.get("states")))
        elif device == "ti2_lightpath":
            core.loadDevice(name, "NikonTi2", "LightPath")
            core.setParentLabel(name, "ti_scope")
            core.initializeDevice(name)
            devices.append(Selector(name, core, params.get("states", ["eye", "l100", "r100", "l80"])))
        elif device == "ti2_focus":
            core.loadDevice(name, "NikonTi2", "ZDrive")
            core.setParentLabel(name, "ti2_scope")
            core.initializeDevice(name)
            devices.append(Focus(name, core))
        elif device == "ti2_objective":
            core.loadDevice(name, "NikonTi2", "IntermediateMagnification")
            core.setParentLabel(name, "ti2_scope")
            core.initializeDevice(name)
            devices.append(Selector(name, core, params.get("states")))
        elif device == "wago_valves":
            if client is None:
                client = pymodbus.client.ModbusTcpClient(params["ip"])
                client.connect()
            devices.append(Valves(name, client, params.get("valves")))
        elif device == "zyla_camera":
            core.loadDevice(name, "AndorSDK3", "Andor sCMOS Camera")
            core.initializeDevice(name)
            devices.append(Camera(name, core))
        else:
            raise ValueError(f"Device {device} is not recognized.")

        for k, v in params.items():
            if k not in ["port", "device", "states", "valves", "ip"]:
                core.setProperty(name, k, v)

    return Control(core, devices=devices)


class Control:
    def __init__(self, core, devices=None):
        if devices is None:
            devices = {}
        super(Control, self).__setattr__("devices", devices)
        self._core = core

        self._camera = None
        for device in self.devices:
            if isinstance(device, Camera):
                self._camera = device
                break

        self._stage = None
        for device in self.devices:
            if isinstance(device, Stage):
                self._stage = device
                break

        self._focus = None
        for device in self.devices:
            if isinstance(device, Focus):
                self._focus = device
                break

    @property
    def camera(self):
        return self._camera.name if self._camera is not None else None

    @camera.setter
    def camera(self, new_camera):
        self._camera = self.devices[new_camera]

    def snap(self):
        return self._camera.snap()

    @property
    def exposure(self):
        return self._camera.exposure

    @exposure.setter
    def exposure(self, new_exposure):
        self._camera.exposure = new_exposure

    @property
    def focus(self):
        return self._focus.name if self._focus is not None else None

    @focus.setter
    def focus(self, new_focus):
        self._focus = self.devices[new_focus]

    @property
    def z(self):
        return self._focus.z

    @z.setter
    def z(self, new_z):
        self._focus.z = new_z

    @property
    def stage(self):
        return self._stage.name if self._stage is not None else None

    @stage.setter
    def stage(self, new_stage):
        self._stage = self.devices[new_stage]

    @property
    def x(self):
        return self._stage.x

    @x.setter
    def x(self, new_x):
        self._stage.x = new_x

    @property
    def y(self):
        return self._stage.y

    @y.setter
    def y(self, new_y):
        self._stage.y = new_y

    @property
    def xy(self):
        return self._stage.xy

    @xy.setter
    def xy(self, new_xy):
        self._stage.xy = new_xy

    def __getattr__(self, name):
        for device in self.devices:
            if name == device.name:
                if isinstance(device, Stateful):
                    return device.state
                else:
                    return device

        return self.__getattribute__(name)

    def __setattr__(self, name, value):
        for device in self.devices:
            if name == device.name and isinstance(device, Stateful):
                device.state = value
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
        return np.flipud(self._core.getImage())

    @property
    def exposure(self):
        return self._core.getExposure(self.name)

    @exposure.setter
    def exposure(self, new_exposure):
        self._core.setExposure(self.name, new_exposure)


class Focus:
    def __init__(self, name, core):
        self.name = name
        self._core = core

    @property
    def z(self):
        return self._core.getPosition(self.name)

    @z.setter
    def z(self, new_z):
        self._core.setPosition(self.name, new_z)


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


@runtime_checkable
class Stateful(Protocol):
    state: str | int | float

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


class Shutter:
    def __init__(self, name, core):
        self.name = name
        self._core = core

    @property
    def open(self):
        return self._core.getShutterOpen(self.name)

    @open.setter
    def open(self, new_state):
        self._core.setShutterOpen(self.name, new_state)

    @property
    def state(self):
        return "open" if self.open else "closed"

    @state.setter
    def state(self, new_state):
        self.open = new_state == "open"


class SolaLight:
    def __init__(self, name, core):
        self.name = name
        self._core = core

    @property
    def state(self):
        return int(self._core.getProperty(self.name, "White_Level"))

    @state.setter
    def state(self, new_state):
        self._core.setProperty(self.name, "White_Level", new_state)


class Valves:
    def __init__(self, name, client, valves=None):
        self.name = name
        if valves is None:
            valves = [i for i in range(48)]
        self.valves = valves
        self._client = client

    def __getitem__(self, key):
        if isinstance(key, int):
            addr = key
        else:
            addr = self.valves.index(key)
        addr += 512
        return "open" if self._client.read_coils(addr, 1).bits[0] else "closed"

    def __setitem__(self, key, value):
        if isinstance(key, int):
            addr = key
        else:
            addr = self.valves.index(key)
        self._client.write_coil(addr, value == "open")
