import contextlib
import os

__all__ = ["Light"]

# Thorlabs drivers are only supported in Windows.
if os.name == "nt":
    # Enable local dll loading for editable pip installs.
    os.add_dll_directory(os.path.dirname(os.path.realpath(__file__)))
    # Ignore import errors since the module is optional.
    with contextlib.suppress(ImportError):
        from .thor import Light
