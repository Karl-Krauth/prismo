import os

if os.name == "nt":
    # Enable local dll loading for editable pip installs.
    os.add_dll_directory(os.path.dirname(os.path.realpath(__file__)))
    from .fluigent import FlowController
