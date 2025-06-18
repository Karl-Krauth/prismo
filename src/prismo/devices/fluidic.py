import serial
import struct

class Handler:
    def __init__(self, name, port):
        self.name = name
        self._socket = serial.Serial(port, baudrate=9600)
        self._xyz = (0, 0, 0)

    @property
    def xyz(self):
        return self._xyz

    @xyz.setter
    def xyz(self, value):
        self._xyz = value
        msg = struct.pack("<BIII", 1, *value)
        self._socket.write(msg)
        self._socket.read(1)
