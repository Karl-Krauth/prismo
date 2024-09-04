class Camera:
    def __init__(self, name: str, core):
        self.name = name
        self._core = core
        core.loadDevice(name, "DemoCamera", "DCam")
        core.initializeDevice(name)

    def snap(self) -> np.ndarray:
        self._core.setCameraDevice(self.name)
        self._core.snapImage()
        return self._core.getImage()

    def wait(self):
        self._core.waitForDevice(self.name)

    @property
    def exposure(self) -> float:
        return self._core.getExposure(self.name)

    @exposure.setter
    def exposure(self, new_exposure: float):
        self._core.setExposure(self.name, new_exposure)

    @property
    def px_len(self) -> float:
        # TODO: Find out the pixel length of the demo camera.
        return 1.0



