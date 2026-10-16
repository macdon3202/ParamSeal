"""Windows gltest compatibility: unlink fd0 tempfiles after VM teardown."""
import atexit
import os
from gltest.direct import loader

original = loader._inject_message_to_fd0
paths = []

def safe(vm):
    unlink = os.unlink
    os.unlink = lambda path: paths.append(path)
    try:
        original(vm)
    finally:
        os.unlink = unlink

def cleanup():
    for path in paths:
        try:
            os.unlink(path)
        except OSError:
            pass

if os.name == "nt":
    loader._inject_message_to_fd0 = safe
    atexit.register(cleanup)

