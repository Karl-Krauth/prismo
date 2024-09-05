from typing import runtime_checkable, Protocol

import numpy as np


@runtime_checkable
class Camera(Protocol):
    exposure: float

    def snap(self) -> np.ndarray: ...


@runtime_checkable
class Focus(Protocol):
    z: float


@runtime_checkable
class Stage(Protocol):
    x: float
    y: float
    xy: tuple[float, float]


@runtime_checkable
class State(Protocol):
    state: str | int | float


@runtime_checkable
class Valves(Protocol):
    valves: float


@runtime_checkable
class Wait(Protocol):
    def wait() -> None: ...


@runtime_checkable
class Zoom(Protocol):
    zoom: float
