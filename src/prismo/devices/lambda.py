class Selector:
    def __init__(self, name, core, wheel, port, states=None):
        self.name = name
        self.states = states
        self._core = core
        core.loadDevice(name, "SutterLambda", "Wheel-" + wheel)
        core.setProperty(name, "Port", port)
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


class Shutter:
    def __init__(self, name, core, shutter, port):
        self.name = name
        self._core = core
        core.loadDevice(name, "SutterLambda", "Shutter-" + shutter)
        core.setProperty(name, "Port", port)
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
