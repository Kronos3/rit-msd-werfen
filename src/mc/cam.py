import abc
from picamera2 import Picamera2


class Camera(abc.ABC):
    cam: int
    camera: Picamera2
    config: dict

    def __init__(self, cam: int):
        self.cam = cam
        if self.is_hardware:
            self.camera = Picamera2(cam)

    @property
    def is_hardware(self) -> bool:
        return self.cam >= 0

    def start(self):
        if self.is_hardware:
            self.camera.configure(self.config)
            self.camera.start()

    def stop(self):
        if self.is_hardware:
            self.camera.stop()

    def acquire(self, name: str):
        if self.is_hardware:
            self.camera.capture_file(name)

    def acquire_array(self):
        if self.is_hardware:
            return self.camera.capture_array()


class HqCamera(Camera):
    def __init__(self, cam: int):
        super().__init__(cam)
        self.config = self.camera.create_still_configuration(
            main={"size": (4056, 3040)},
        )


class AuxCamera(Camera):
    def __init__(self, cam: int):
        super().__init__(cam)
        self.config = self.camera.create_still_configuration(
            main={"size": (3280, 2464)},
        )
