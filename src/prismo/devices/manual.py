class Objective:
    def __init__(self, name, zoom=1):
        self.name = name
        self._zoom = zoom

    def wait(self):
        pass

    @property
    def state(self):
        return self._zoom

    @state.setter
    def state(self, new_state):
        self._zoom = new_state

    @property
    def zoom(self):
        return self._zoom
