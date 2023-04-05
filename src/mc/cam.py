import abc
import threading

import numpy as np

from mc.log import log


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

    def __enter__(self):
        if self.is_hardware:
            self.camera.configure(self.config)
            self.camera.start()
        self._lock.acquire()
        log.info("Starting %s camera", self.name)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._lock.release()
        log.info("Stopping %s camera", self.name)
        if self.is_hardware:
            self.camera.stop()

    def acquire(self, name: str):
        assert self._lock.locked()
        if self.is_hardware:
            self.camera.capture_file(name)

    def acquire_array(self) -> np.ndarray:
        assert self._lock.locked()
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
