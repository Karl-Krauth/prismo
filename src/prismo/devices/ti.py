class Filter:
    def __init__(self, name, core, filter, states=None):
        self.name = name
        self._core = core
        if "ti_scope" not in core.getLoadedDevices():
            core.loadDevice("ti_scope", "NikonTI", "TIScope")
            core.initializeDevice("ti_scope")
        core.loadDevice(name, "NikonTI", "TIFilterBlock" + str(filter))
        core.setParentLabel(name, "ti_scope")
        core.initializeDevice(name)

        n_states = self._core.getNumberOfStates(name)
        if states is None:
            self.states = [i for i in range(n_states)]
        else:
            self.states = states
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
        self._core = core
        if "ti_scope" not in core.getLoadedDevices():
            core.loadDevice("ti_scope", "NikonTI", "TIScope")
            core.initializeDevice("ti_scope")
        core.loadDevice(name, "NikonTI", "TILightPath")
        core.setParentLabel(name, "ti_scope")
        core.initializeDevice(name)

        self.states = ["eye", "left", "right", "aux"] if states is None else states
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
        self._core = core
        if "ti_scope" not in core.getLoadedDevices():
            core.loadDevice("ti_scope", "NikonTI", "TIScope")
            core.initializeDevice("ti_scope")
        core.loadDevice(name, "NikonTI", "TINosePiece")
        core.setParentLabel(name, "ti_scope")
        core.initializeDevice(name)

        n_states = self._core.getNumberOfStates(name)
        if states is None:
            self.states = [i for i in range(n_states)]
        else:
            self.states = states
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


class Focus:
    def __init__(self, name, core):
        self.name = name
        self._core = core
        if "ti_scope" not in core.getLoadedDevices():
            core.loadDevice("ti_scope", "NikonTI", "TIScope")
            core.initializeDevice("ti_scope")
        core.loadDevice(name, "NikonTI", "TIZDrive")
        core.setParentLabel(name, "ti_scope")
        core.initializeDevice(name)

    def wait(self):
        self._core.waitForDevice(self.name)

    @property
    def z(self):
        return self._core.getPosition(self.name)

    @z.setter
    def z(self, new_z):
        self._core.setPosition(self.name, new_z)
