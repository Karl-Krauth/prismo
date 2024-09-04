import os

# Enable local dll loading for editable pip installs.
os.add_dll_directory(os.path.dirname(os.path.realpath(__file__)))

from .thor import Light
