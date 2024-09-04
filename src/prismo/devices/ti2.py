class Filter:
    def __init__(self, name, core, filter, states=None):
        self.name = name
        self.states = states
        self._core = core
        if "ti2_scope" not in core.getLoadedDevices():
            core.loadDevice("ti2_scope", "NikonTi2", "Ti2-E__0")
            core.initializeDevice("ti2_scope")
        core.loadDevice(name, "NikonTi2", "FilterTurret" + filter)
        core.setParentLabel(name, "ti2_scope")
        core.initializeDevice(name)

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


class LightPath:
    def __init__(self, name, core, states=None):
        self.name = name
        self.states = states
        self._core = core
        if "ti2_scope" not in core.getLoadedDevices():
            core.loadDevice("ti2_scope", "NikonTi2", "Ti2-E__0")
            core.initializeDevice("ti2_scope")
        core.loadDevice(name, "NikonTi2", "LightPath")
        core.setParentLabel(name, "ti_scope")
        core.initializeDevice(name)

        if states is None:
            self.states = ["eye", "l100", "r100", "l80"]
        else:
            if len(self.states) != 4:
                raise ValueError(
                    f"{name} requires 4 states (not {len(self.states)}) to be specified."
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
        if "ti2_scope" not in core.getLoadedDevices():
            core.loadDevice("ti2_scope", "NikonTi2", "Ti2-E__0")
            core.initializeDevice("ti2_scope")
        core.loadDevice(name, "NikonTi2", "Nosepiece")
        core.setParentLabel(name, "ti2_scope")
        core.initializeDevice(name)

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
    def __init__(self, name, core, shutter):
        self.name = name
        self._core = core
        if "ti2_scope" not in core.getLoadedDevices():
            core.loadDevice("ti2_scope", "NikonTi2", "Ti2-E__0")
            core.initializeDevice("ti2_scope")
        core.loadDevice(name, "NikonTi2", f"Turret{shutter}Shutter")
        core.setParentLabel(name, "ti2_scope")
        core.initializeDevice(name)

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

class Focus:
    def __init__(self, name, core):
        self.name = name
        self._core = core
        if "ti2_scope" not in core.getLoadedDevices():
            core.loadDevice("ti2_scope", "NikonTi2", "Ti2-E__0")
            core.initializeDevice("ti2_scope")
        core.loadDevice(name, "NikonTi2", "ZDrive")
        core.setParentLabel(name, "ti2_scope")
        core.initializeDevice(name)

    def wait(self):
        self._core.waitForDevice(self.name)

    @property
    def z(self):
        return self._core.getPosition(self.name)

    @z.setter
    def z(self, new_z):
        self._core.setPosition(self.name, new_z)

