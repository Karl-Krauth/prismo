import re
import serial
import struct

import numpy as np


class Handler:
    def __init__(self, name, port, x_max=7500, y_max=6000, z_max=3000):
        self.name = name
        self._socket = serial.Serial(port, baudrate=9600)
        self._xyz = np.zeros(3)
        self._max = np.array([x_max, y_max, z_max])
        self.home()

    @property
    def xyz(self):
        return self._xyz

    @xyz.setter
    def xyz(self, value):
        value = np.array(value)
        if np.any(value < 0) or np.any(value > 1):
            raise ValueError("Coordinates must be in the range [0, 1].")
        self._xyz = value
        value = (value * self._max).astype(np.uint32)
        msg = struct.pack("<BIII", 1, *value)
        self._socket.write(msg)
        self._socket.read(1)

    @property
    def x(self):
        return self._xyz[0]

    @x.setter
    def x(self, value):
        self.xyz = (value, self._xyz[1], self._xyz[2])

    @property
    def y(self):
        return self._xyz[1]

    @y.setter
    def y(self, value):
        self.xyz = (self._xyz[0], value, self._xyz[2])

    @property
    def z(self):
        return self._xyz[2]

    @z.setter
    def z(self, value):
        self.xyz = (self._xyz[0], self._xyz[1], value)

    def home(self):
        msg = struct.pack("<B", 0)
        self._socket.write(msg)
        self._socket.read(1)
        self._xyz = np.zeros(3)


class Plate96:
    def __init__(self, name, handler, a1_pos, h12_pos, z_bottom, mapping=None):
        self.name = name
        self._handler = handler
        self._a1 = a1_pos
        self._h12 = h12_pos
        self._z_bottom = z_bottom
        self._position = "none"
        self._mapping = mapping if mapping is not None else {}

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        if new_state == "none":
            self._handler.z = 0
            self._state = "none"
            return

        if new_state in self._mapping:
            pos = self._mapping[new_state]
        else:
            pos = new_state

        if not re.fullmatch(r"[A-H]1?[0-9]", pos) or int(pos[1:]) > 12:
            raise ValueError("Plate position must be in the format [A-Z][1-12].")

        col = int(pos[1:]) - 1
        if self._a1[0] < self._h12[0]:
            x = self._a1 + col * (self._h12[0] - self._a1[0]) / 11
        else:
            col = 11 - col
            x = self._h12[0] + col * (self._a1[0] - self._h12[0]) / 11

        row = ord(pos[0]) - ord("A")
        if self._a1[1] < self._h12[1]:
            y = self._a1[1] + row * (self._h12[1] - self._a1[1]) / 7
        else:
            row = 7 - row
            y = self._h12[1] + row * (self._a1[1] - self._h12[1]) / 7

        self._handler.z = 0
        self._handler.xyz = (x, y, 0)
        self._handler.z = self._z_bottom
        self._state = new_state
