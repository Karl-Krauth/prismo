class Objective:
    def __init__(self, name, zoom=1):
        self.name = name
        self.zoom = zoom

    def wait(self):
        pass

    @property
    def state(self):
        return self.zoom

    @state.setter
    def state(self, new_state):
        self.zoom = new_state

    @property
    def zoom(self):
        return self.zoom
