import abc
import threading

import cv2
import numpy as np
import logging
import coloredlogs as coloredlogs

coloredlogs.install(fmt='%(asctime)s,%(msecs)03d %(levelname)s %(message)s')
log = logging.getLogger(__name__)


class Camera(abc.ABC):
    cam: int
    still_config: dict
    stream_config: dict
    preview_config: dict
    _lock: threading.Lock

    preview: bool

    def __init__(self, cam: int, name: str):
        self.cam = cam
        self.name = name
        self.preview = False
        self._lock = threading.Lock()
        if self.is_hardware:
            from picamera2 import Picamera2
            self.camera = Picamera2(cam)

    @property
    def is_hardware(self) -> bool:
        return self.cam >= 0

    def start(self, still=True):
        if self.is_hardware:
            self.camera.configure(self.still_config if still else self.stream_config)
            self.camera.set_controls({"AwbMode": 4})
            self.camera.start()

    def start_preview(self):
        from picamera2 import Preview

        self.camera.configure(self.preview_config)
        self.camera.start_preview(Preview.QTGL)
        self.camera.start()
        self.preview = True

    def stop_preview(self):
        self.camera.stop_preview()
        self.preview = False

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
            img = self.camera.capture_array()
            return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


class HqCamera(Camera):
    def __init__(self, cam: int):
        super().__init__(cam, "HQ")
        if self.is_hardware:
            self.still_config = self.camera.create_still_configuration(
                main={"size": (4056, 3040)},
            )
            self.preview = self.camera.create_video_configuration()

            self.stream_config = self.camera.create_preview_configuration()
            self.preview_config = self.camera.create_preview_configuration(main={"size": (2028, 1520)})


class AuxCamera(Camera):
    def __init__(self, cam: int):
        super().__init__(cam, "AUX")
        if self.is_hardware:
            self.still_config = self.camera.create_still_configuration(
                main={"size": (3280, 2464)},
            )
            self.stream_config = self.camera.create_preview_configuration()
            self.preview_config = self.camera.create_preview_configuration(main={"size": (1640, 1232)})
