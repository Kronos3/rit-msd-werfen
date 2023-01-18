from typing import Optional

try:
    from picamera2 import Picamera2
    from picamera2.previews.q_gl_picamera2 import QGlPicamera2
    has_camera = True
except ImportError:
    print("No camera support")
    has_camera = False
    Picamera2 = None
    QGlPicamera2 = None

from fw.component import Component, async_message

from PyQt5 import QtWidgets


class Cam(Component):
    _camera: Optional[Picamera2]
    qpicamera2: Optional[QGlPicamera2]

    def __init__(self, parent: QtWidgets.QFrame):
        super().__init__()
        self._camera = None
        self.qpicamera2 = None
        self.parent = parent

    def setup(self):
        self.log_info("Initializing camera")
        if has_camera:
            self._camera = Picamera2()

            self.qpicamera2 = QGlPicamera2(self._camera, width=800, height=600, keep_ar=True)
            self.qpicamera2.setParent(self.parent)

            self.log_info("Configuring still capture for camera {}", str(self._camera.camera))
            camera_config = self._camera.create_still_configuration()
            self._camera.configure(camera_config)

    def teardown(self):
        pass
