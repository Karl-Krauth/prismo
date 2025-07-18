import re
import serial
import struct

import numpy as np

class Sipper:
    def __init__(self, name, cnc_port, pump_port, valve_port, a1_pos, h12_pos, z_bottom, mapping=None, x_max=7500, y_max=6000, z_max=3000):
        self.name = name
        self._cnc_socket = serial.Serial(cnc_port, baudrate=9600)
        self._valve_socket = serial.Serial(valve_port, baudrate=9600)
        self._pump_socket = serial.Serial(pump_port, baudrate=9600)
        self._xyz = np.zeros(3)
        self._max = np.array([x_max, y_max, z_max])
        self._valve = 1
        self._frequency = 0
        self._voltage = 0
        self._a1 = a1_pos
        self._h12 = h12_pos
        self._z_bottom = z_bottom
        self._well = "none"
        self._mapping = mapping if mapping is not None else {}
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
        self._cnc_socket.write(msg)
        self._cnc_socket.read(1)

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
        self._cnc_socket.write(msg)
        self._cnc_socket.read(1)
        self._xyz = np.zeros(3)

    @property
    def flow_rate(self):
        msg = struct.pack("<B", 2)
        self._valve_socket.write(msg)
        error = self._valve_socket.read(1)
        if error != b"\x00":
            raise RuntimeError(read_byte_str(self._valve_socket))
        flow = struct.unpack("<f", self._valve_socket.read(4))[0]
        temperature, flags = struct.unpack("<fH", self._valve_socket.read(6))
        print(temperature, flags)
        return flow

    @property
    def valve(self):
        return self._valve

    @valve.setter
    def valve(self, value):
        value = 1 if value in [1, "open"] else 0
        self._valve = value
        msg = struct.pack("<B", value)
        self._valve_socket.write(msg)
        self._valve_socket.read(1)

    @property
    def frequency(self):
        return self._frequency

    @frequency.setter
    def frequency(self, value):
        if value > 800 or value < 0:
            raise ValueError("Frequency must be less than or equal to 800 Hz.")
        self._frequency = value
        self._pump_socket.write(struct.pack("<HB", self._frequency, self._voltage))
        self._pump_socket.read(1)

    @property
    def voltage(self):
        return self._voltage

    @voltage.setter
    def voltage(self, value):
        self._voltage = value
        self._pump_socket.write(struct.pack("<HB", self._frequency, self._voltage))
        self._pump_socket.read(1)

    @property
    def well(self):
        return self._well

    @well.setter
    def well(self, new_well):
        if new_well == "none":
            self.z = 0
            self._well = "none"
            return

        if new_well in self._mapping:
            pos = self._mapping[new_well]
        else:
            pos = new_well

        if new_well == self._well:
            return

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

        self.z = 0
        self.xyz = (x, y, 0)
        self.z = self._z_bottom
        self._well = new_well

    def sip(self, well):
        self.frequency = 0
        self.voltage = 0
        self.well = well
        self.valve = "closed"
        self.frequency = 200
        self.voltage = 250

    def purge(self, well):
        self.frequency = 0
        self.voltage = 0
        self.well = well
        self.valve = "open"
        self.frequency = 200
        self.voltage = 250


def read_byte_str(socket):
    received_bytes = bytearray()
    while True:
        byte = socket.read(1)
        if not byte or byte == b"\x00":
            break
        received_bytes.extend(byte)
    return received_bytes.decode("ascii")
