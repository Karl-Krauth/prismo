import numpy as np


class Camera:
    def __init__(self, name, core, rotate=0):
        self.name = name
        self._core = core
        self._rotate = rotate
        core.loadDevice(name, "AndorSDK3", "Andor sCMOS Camera")
        core.initializeDevice(name)

    def snap(self) -> np.ndarray:
        self._core.setCameraDevice(self.name)
        self._core.snapImage()
        return np.rot90(self._core.getImage(), k=self._rotate)

    def wait(self):
        self._core.waitForDevice(self.name)

    @property
    def binning(self) -> int:
        return int(self._core.getProperty(self.name, "Binning")[-1])

    @binning.setter
    def binning(self, new_binning: int):
        self._core.setProperty(self.name, "Binning", f"{new_binning}x{new_binning}")

    @property
    def exposure(self) -> float:
        return self._core.getExposure(self.name)

    @exposure.setter
    def exposure(self, new_exposure: float):
        self._core.setExposure(self.name, new_exposure)

    @property
    def px_len(self) -> float:
        return self.binning * 6.5
