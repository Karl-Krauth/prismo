from typing import runtime_checkable, Protocol
import collections
import os

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
        device = params["device"]
        if (
            device in ("ti_focus", "ti_filter1", "ti_filter2", "ti_lightpath", "ti_objective")
            and "ti_scope" not in core.getLoadedDevices()
        ):
            core.loadDevice("ti_scope", "NikonTI", "TIScope")
            core.initializeDevice("ti_scope")
        elif (
            device
            in (
                "ti2_focus",
                "ti2_filter1",
                "ti2_filter2",
                "ti2_shutter1",
                "ti2_shutter2",
                "ti2_lightpath",
                "ti2_objective",
            )
            and "ti2_scope" not in core.getLoadedDevices()
        ):
            core.loadDevice("ti2_scope", "NikonTi2", "Ti2-E__0")
            core.initializeDevice("ti2_scope")

        if device == "asi_stage":
            core.loadDevice(name, "ASIStage", "XYStage")
            core.setProperty(name, "Port", params["port"])
            core.initializeDevice(name)
            devices.append(Stage(name, core))
        elif device == "asi_zstage":
            core.loadDevice(name, "ASIStage", "ZStage")
            core.setProperty(name, "Port", params["port"])
            core.setProperty(name, "Axis", "Z")
            core.initializeDevice(name)
            devices.append(Focus(name, core))
        elif device == "demo_camera":
            core.loadDevice(name, "DemoCamera", "DCam")
            core.initializeDevice(name)
            devices.append(Camera(name, core))
        elif device == "demo_filter":
            core.loadDevice(name, "DemoCamera", "DWheel")
            core.initializeDevice(name)
            devices.append(Selector(name, core, states=params.get("states")))
        elif device == "demo_stage":
            core.loadDevice(name, "DemoCamera", "DXYStage")
            core.initializeDevice(name)
            devices.append(Stage(name, core))
        elif device == "demo_valves":
            devices.append(DemoValves(name, params.get("valves")))
            valves = devices[-1]
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
        elif device == "mux":
            devices.append(Mux(name, params["mapping"], valves))
            continue
        elif device == "minichip":
            devices.append(MiniChip(name, params["mapping"], valves))
            continue
        elif device == "sola_light":
            core.loadDevice(name, "LumencorSpectra", "Spectra")
            core.setProperty(name, "SetLE_Type", "Sola")
            core.setProperty(name, "Port", params["port"])
            core.initializeDevice(name)
            devices.append(SolaLight(name, core))
        elif device == "spectra_light":
            core.loadDevice(name, "LumencorSpectra", "Spectra")
            core.setProperty(name, "SetLE_Type", "Spectra")
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
            devices.append(
                Selector(name, core, params.get("states", ["eye", "l100", "r100", "l80"]))
            )
        elif device == "ti_focus":
            core.loadDevice(name, "NikonTI", "TIZDrive")
            core.setParentLabel(name, "ti_scope")
            core.initializeDevice(name)
            devices.append(Focus(name, core))
        elif device == "ti_objective":
            core.loadDevice(name, "NikonTI", "TINosePiece")
            core.setParentLabel(name, "ti_scope")
            core.initializeDevice(name)
            devices.append(Objective(name, core, params.get("zooms"), params.get("states")))
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
        elif device == "ti2_shutter1":
            core.loadDevice(name, "NikonTi2", "Turret1Shutter")
            core.setParentLabel(name, "ti2_scope")
            core.initializeDevice(name)
            devices.append(Shutter(name, core))
        elif device == "ti2_shutter2":
            core.loadDevice(name, "NikonTi2", "Turret2Shutter")
            core.setParentLabel(name, "ti2_scope")
            core.initializeDevice(name)
            devices.append(Shutter(name, core))
        elif device == "ti2_lightpath":
            core.loadDevice(name, "NikonTi2", "LightPath")
            core.setParentLabel(name, "ti_scope")
            core.initializeDevice(name)
            devices.append(
                Selector(name, core, params.get("states", ["eye", "l100", "r100", "l80"]))
            )
        elif device == "ti2_focus":
            core.loadDevice(name, "NikonTi2", "ZDrive")
            core.setParentLabel(name, "ti2_scope")
            core.initializeDevice(name)
            devices.append(Focus(name, core))
        elif device == "ti2_objective":
            core.loadDevice(name, "NikonTi2", "Nosepiece")
            core.setParentLabel(name, "ti2_scope")
            core.initializeDevice(name)
            devices.append(Objective(name, core, params.get("zooms"), params.get("states")))
        elif device == "wago_valves":
            if client is None:
                client = pymodbus.client.ModbusTcpClient(params["ip"])
                client.connect()
            devices.append(Valves(name, client, params.get("valves")))
            valves = devices[-1]
        elif device == "zyla_camera":
            core.loadDevice(name, "AndorSDK3", "Andor sCMOS Camera")
            core.initializeDevice(name)
            devices.append(Camera(name, core))
        else:
            raise ValueError(f"Device {device} is not recognized.")

        for k, v in params.items():
            if k not in ["port", "device", "states", "valves", "ip", "zooms"]:
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

    def wait(self):
        for device in self.devices:
            if isinstance(device, Waitable):
                device.wait()

    @property
    def camera(self):
        return self._camera.name if self._camera is not None else None

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

    def wait(self):
        self._core.waitForDevice(self.name)

    @property
    def binning(self):
        return int(self._core.getProperty(self.name, "Binning")[-1])

    @binning.setter
    def binning(self, new_binning):
        self._core.setProperty(self.name, "Binning", f"{new_binning}x{new_binning}")

    @property
    def exposure(self):
        return self._core.getExposure(self.name)

    @exposure.setter
    def exposure(self, new_exposure):
        self._core.setExposure(self.name, new_exposure)

    @property
    def px_len(self):
        return self.binning * 6.5


class Focus:
    def __init__(self, name, core):
        self.name = name
        self._core = core

    def wait(self):
        self._core.waitForDevice(self.name)

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


@runtime_checkable
class Stateful(Protocol):
    state: str | int | float


@runtime_checkable
class Waitable(Protocol):
    def wait() -> None: ...


@runtime_checkable
class Zooms(Protocol):
    zoom: float


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
                raise ValueError(
                    f"{name} requires {n_states} states (not {len(self.states)}) to be specified."
                )
            for i, state in enumerate(self.states):
                self._core.defineStateLabel(name, i, state)

    def wait(self):
        self._core.waitForDevice(self.name)

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


class Objective:
    def __init__(self, name, core, zooms, states=None):
        self.name = name
        self.states = states
        self._core = core

        n_states = self._core.getNumberOfStates(name)
        if states is None:
            self.states = [i for i in range(n_states)]
        else:
            if len(self.states) < n_states:
                raise ValueError(
                    f"{name} requires {n_states} states (not {len(self.states)}) to be specified."
                )
            for i, state in enumerate(self.states):
                self._core.defineStateLabel(name, i, state)
        self.zooms = {state: zoom for state, zoom in zip(self.states, zooms)}

    def wait(self):
        self._core.waitForDevice(self.name)

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

    @property
    def zoom(self):
        return self.zooms[self.state]


class Shutter:
    def __init__(self, name, core):
        self.name = name
        self._core = core

    def wait(self):
        self._core.waitForDevice(self.name)

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

    def wait(self):
        self._core.waitForDevice(self.name)

    @property
    def state(self):
        return int(self._core.getProperty(self.name, "White_Level"))

    @state.setter
    def state(self, new_state):
        self._core.setProperty(self.name, "White_Level", new_state)


class DemoValves:
    def __init__(self, name, valves=None):
        self.name = name
        if valves is None:
            valves = [i for i in range(48)]
        self.valves = {k: 1 for k in valves}

    def __getitem__(self, key):
        return self.valves[key]

    def __setitem__(self, key, value):
        self.valves[key] = int((value != "off") and (value != 0))


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
        return 0 if self._client.read_coils(addr, 1).bits[0] else 1

    def __setitem__(self, key, value):
        if isinstance(key, int):
            addr = key
        else:
            addr = self.valves.index(key)
        self._client.write_coil(addr, (value == "off") or (value == 0))


class Mux:
    def __init__(self, name, mapping, valves):
        self.name = name
        num_bits = (len(mapping) - 2) // 2
        self._zeros = [mapping[f"{i}_0"] for i in reversed(range(num_bits))]
        self._ones = [mapping[f"{i}_1"] for i in reversed(range(num_bits))]
        self._waste = mapping["waste"]
        self._io = mapping["io"]
        self._all = self._zeros + self._ones + [self._waste, self._io]
        self._valves = valves

    @property
    def state(self):
        waste_state = 1 - self._valves[self._waste]
        io_state = 1 - self._valves[self._io]
        zeros_state = np.array([1 - self._valves[v] for v in self._zeros])
        ones_state = np.array([1 - self._valves[v] for v in self._ones])
        all_state = np.array([1 - self._valves[v] for v in self._all])
        if np.all(all_state):
            return "open"
        elif not np.any(all_state):
            return "closed"
        elif waste_state and not io_state and not np.any(zeros_state) and not np.any(ones_state):
            return "waste"
        elif np.all(zeros_state + ones_state == 1) and io_state:
            return sum(b * 2**i for i, b in enumerate(reversed(ones_state)))
        else:
            return "invalid"

    @state.setter
    def state(self, new_state):
        if new_state == "open":
            for v in self._all:
                self._valves[v] = 0
        elif new_state == "closed":
            for v in self._all:
                self._valves[v] = 1
        elif new_state == "waste":
            for v in self._all:
                self._valves[v] = 1
            self._valves[self._waste] = 0
        elif isinstance(new_state, int):
            for v in self._all:
                self._valves[v] = 1
            for i, b in enumerate(bin(new_state)[2:].zfill(len(self._ones))):
                if b == "0":
                    self._valves[self._zeros[i]] = 0
                else:
                    self._valves[self._ones[i]] = 0
            self._valves[self._io] = 0
        elif "waste" in new_state:
            new_state = int(new_state.split("_")[0])
            for v in self._all:
                self._valves[v] = 1
            for i, b in enumerate(bin(new_state)[2:].zfill(len(self._ones))):
                if b == "0":
                    self._valves[self._zeros[i]] = 0
                else:
                    self._valves[self._ones[i]] = 0
            self._valves[self._waste] = 0


class MiniChip:
    def __init__(self, name, mapping, valves):
        self.name = name
        num_bits = (len(mapping) - 2) // 2
        self._zeros = [mapping[f"{i}_0"] for i in reversed(range(num_bits))]
        self._ones = [mapping[f"{i}_1"] for i in reversed(range(num_bits))]
        self._all_io = self._zeros + self._ones
        self._buttons = mapping["buttons"]
        self._sandwiches = mapping["sandwiches"]
        self._valves = valves

    @property
    def io(self):
        zeros_state = np.array([1 - self._valves[v] for v in self._zeros])
        ones_state = np.array([1 - self._valves[v] for v in self._ones])
        all_state = np.array([1 - self._valves[v] for v in self._all_io])
        if np.all(all_state):
            return "open"
        elif not np.any(all_state):
            return "closed"
        elif np.all(zeros_state + ones_state == 1):
            return sum(b * 2**i for i, b in enumerate(reversed(ones_state)))
        else:
            return "invalid"

    @io.setter
    def io(self, new_state):
        if new_state == "open":
            for v in self._all_io:
                self._valves[v] = 0
        elif new_state == "closed":
            for v in self._all_io:
                self._valves[v] = 1
        else:
            for v in self._all_io:
                self._valves[v] = 1

            for i, b in enumerate(bin(new_state)[2:].zfill(len(self._ones))):
                if b == "0":
                    self._valves[self._zeros[i]] = 0
                else:
                    self._valves[self._ones[i]] = 0

    @property
    def btn(self):
        return "closed" if self._valves[self._buttons] else "open"

    @btn.setter
    def btn(self, new_state):
        if new_state == "open" or not new_state:
            self._valves[self._buttons] = "off"
        else:
            self._valves[self._buttons] = "on"

    @property
    def snw(self):
        return "closed" if self._valves[self._sandwiches] else "open"

    @snw.setter
    def snw(self, new_state):
        if new_state == "open" or not new_state:
            self._valves[self._sandwiches] = "off"
        else:
            self._valves[self._sandwiches] = "on"
