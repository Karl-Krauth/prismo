from typing import runtime_checkable, Protocol
import collections
import os

import numpy as np
import pymmcore

import prismo.devices as dev


def load(config, path=None):
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
        if device is None or device not in (
            "asi_stage",
            "asi_zstage",
            "lambda_filter1",
            "lambda_filter2",
            "lambda_shutter1",
            "lambda_shutter2",
            "sola_light",
            "spectra_light",
        ):
            continue
        if "port" not in params:
            raise ValueError(f"{name} requires a port to be specified.")

        port = params["port"]
        if device == "asi_stage":
            ports[port] = {**port_defaults, "AnswerTimeout": 2000.0}
        elif device == "asi_zstage":
            ports[port] = {**port_defaults, "AnswerTimeout": 2000.0}
        elif device in ("lambda_filter1", "lambda_filter2", "lambda_shutter1", "lambda_shutter2"):
            ports[port] = {**port_defaults, "AnswerTimeout": 2000.0, "BaudRate": 128000}
        elif device == "sola_light" or device == "spectra_light":
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

        device = params.pop("device")

        if device == "asi_stage":
            devices.append(dev.asi.Stage(name, core, params["port"]))
        elif device == "asi_zstage":
            devices.append(dev.asi.Focus(name, core, params["port"]))
        elif device == "demo_camera":
            devices.append(dev.demo.Camera(name, core))
        elif device == "demo_filter":
            devices.append(dev.demo.Filter(name, core, **params))
        elif device == "demo_stage":
            devices.append(dev.demo.Stage(name, core))
        elif device == "demo_valves":
            devices.append(dev.demo.Valves(name, **params))
            valves = devices[-1]
        elif device == "lambda_filter1":
            devices.append(dev.lambda.Filter(name, core, filter="A", **params))
        elif device == "lambda_filter2":
            devices.append(dev.lambda.Filter(name, core, filter="B", **params))
        elif device == "lambda_filter3":
            devices.append(dev.lambda.Filter(name, core, filter="C", **params))
        elif device == "lambda_shutter1":
            devices.append(dev.lambda.Shutter(name, core, shutter="A", **params))
        elif device == "lambda_shutter2":
            devices.append(dev.lambda.Shutter(name, core, shutter="B", **params))
        elif device == "microfluidic_mux":
            devices.append(dev.microfluidic.Mux(name, valves, **params))
        elif device == "microfluidic_minichip":
            devices.append(MiniChip(name, valves, **params))
        elif device == "microfluidic_valves":
            devices.append(dev.microfluidic.Valves(name, **params))
            valves = devices[-1]
        elif device == "sola_light":
            devices.append(dev.lumencor.Light(name, core, version="sola", **params))
        elif device == "spectra_light":
            devices.append(dev.lumencor.Light(name, core, version="spectra", **params))
        elif device == "ti_filter1":
            devices.append(dev.ti.Filter(name, core, filter=1, **params))
        elif device == "ti_filter2":
            devices.append(dev.ti.Filter(name, core, filter=2, **params))
        elif device == "ti_lightpath":
            devices.append(dev.ti.LightPath(name, core, **params))
        elif device == "ti_focus":
            devices.append(dev.ti.Focus(name, core))
        elif device == "ti_objective":
            devices.append(dev.ti.Objective(name, core, **params))
        elif device == "ti2_filter1":
            devices.append(dev.ti2.Filter(name, core, filter=1, **params))
        elif device == "ti2_filter2":
            devices.append(dev.ti2.Filter(name, core, filter=2, **params))
        elif device == "ti2_shutter1":
            devices.append(dev.ti2.Shutter(name, core, shutter=1))
        elif device == "ti2_shutter2":
            devices.append(dev.ti2.Shutter(name, core, shutter=2))
        elif device == "ti2_lightpath":
            devices.append(dev.ti2.LightPath(name, core, **params))
        elif device == "ti2_focus":
            devices.append(dev.ti2.Focus(name, core))
        elif device == "ti2_objective":
            devices.append(dev.ti2.Objective(name, core, **params))
        elif device == "zyla_camera":
            core.loadDevice(name, "AndorSDK3", "Andor sCMOS Camera")
            core.initializeDevice(name)
            devices.append(Camera(name, core))
        else:
            raise ValueError(f"Device {device} is not recognized.")

    return Control(core, devices=devices)


class Control:
    def __init__(self, core, devices=None):
        if devices is None:
            devices = {}

        # We can't directly set self.devices = devices since our overriden method
        # depends on self.devices being set.
        super(Control, self).__setattr__("devices", devices)

        self._core = core
        self._camera = None
        for device in self.devices:
            if isinstance(device, Snaps):
                self._camera = device
                break

        self._stage = None
        for device in self.devices:
            if isinstance(device, Moves):
                self._stage = device
                break

        self._focus = None
        for device in self.devices:
            if isinstance(device, Focuses):
                self._focus = device
                break

    def wait(self):
        for device in self.devices:
            if isinstance(device, Waits):
                device.wait()

    @property
    def camera(self):
        return self._camera

    @camera.setter
    def camera(self, new_camera):
        self._camera = self.devices[new_camera]

    @property
    def binning(self):
        return self._camera.binning

    @binning.setter
    def binning(self, new_binning):
        self._camera.binning = new_binning

    def snap(self):
        return self._camera.snap()

    @property
    def px_len(self):
        zoom_total = 1
        for device in self.devices:
            if isinstance(device, Zooms):
                zoom_total *= device.zoom
        return self._camera.px_len / zoom_total

    @property
    def exposure(self):
        return self._camera.exposure

    @exposure.setter
    def exposure(self, new_exposure):
        self._camera.exposure = new_exposure

    @property
    def focus(self):
        return self._focus

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
        return self._stage

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


@runtime_checkable
class Stateful(Protocol):
    state: str | int | float


@runtime_checkable
class Snaps(Protocol):
    def snap(self) -> np.ndarray: ...


@runtime_checkable
class Moves(Protocol):
    x: float
    y: float


@runtime_checkable
class Focuses(Protocol):
    z: float


@runtime_checkable
class Waits(Protocol):
    def wait() -> None: ...


@runtime_checkable
class Zooms(Protocol):
    zoom: float
