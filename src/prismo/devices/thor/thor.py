from . import thor_lib


class Light:
    def __init__(self, name, port):
        self.name = name
        self._device_id = thor_lib.init(port)

    def wait(self):
        # TODO: Implement this.
        pass

    @property
    def state(self):
        return thor_lib.get_amps(self._device_id)

    @state.setter
    def state(self, new_state):
        thor_lib.set_amps(new_state)
        thor_lib.toggle(self._device_id, new_state > 0)
