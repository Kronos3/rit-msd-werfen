import abc
import threading

import numpy as np
import logging
import coloredlogs as coloredlogs

coloredlogs.install(fmt='%(asctime)s,%(msecs)03d %(levelname)s %(message)s')
log = logging.getLogger(__name__)


class Camera(abc.ABC):
    cam: int
    config: dict
    _lock: threading.Lock

    def __init__(self, cam: int, name: str):
        self.cam = cam
        self.name = name
        self._lock = threading.Lock()
        if self.is_hardware:
            from picamera2 import Picamera2
            self.camera = Picamera2(cam)

    @property
    def is_hardware(self) -> bool:
        return self.cam >= 0

    def start(self):
        if self.is_hardware:
            self.camera.configure(self.config)
            self.camera.set_controls({"AwbEnable": False})
            self.camera.start()

    def stop(self):
        if self.is_hardware:
            self.camera.stop()

    def __enter__(self):
        self.start()
        self._lock.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        self._lock.release()

    def acquire(self, name: str):
        if self.is_hardware:
            self.camera.capture_file(name)

    def acquire_array(self) -> np.ndarray:
        if self.is_hardware:
            return self.camera.capture_array()


class HqCamera(Camera):
    def __init__(self, cam: int):
        super().__init__(cam, "HQ")
        if self.is_hardware:
            self.config = self.camera.create_still_configuration(
                main={"size": (4056, 3040)},
            )


class AuxCamera(Camera):
    def __init__(self, cam: int):
        super().__init__(cam, "AUX")
        if self.is_hardware:
            self.config = self.camera.create_still_configuration(
                main={"size": (3280, 2464)},
            )
