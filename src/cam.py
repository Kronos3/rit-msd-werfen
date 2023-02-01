from typing import Optional

from PyQt5.QtGui import QPalette

try:
    from picamera2 import Picamera2
    from picamera2.previews.q_gl_picamera2 import QGlPicamera2
    has_camera = True
except ImportError:
    print("No camera support")
    has_camera = False
    Picamera2 = None
    QGlPicamera2 = None

from fw.component import Component
from PyQt5 import QtWidgets


class Cam(Component):
    _camera: Optional[Picamera2]
    qpicamera2: Optional[QGlPicamera2]

    def __init__(self, window: QtWidgets.QMainWindow, parent: QtWidgets.QHBoxLayout):
        super().__init__()
        self.window = window
        self._camera = None
        self.qpicamera2 = None
        self.parent = parent

    def setup(self):
        self.log_info("Initializing camera")
        if has_camera:
            self._camera = Picamera2()

            bg_colour = self.window.palette().color(QPalette.Background).getRgb()[:3]
            self.qpicamera2 = QGlPicamera2(self._camera, width=800, height=600, keep_ar=True, bg_colour=bg_colour)

            self.parent.addWidget(self.qpicamera2)

            self.log_info("Configuring still capture for camera {}", str(self._camera.camera))
            camera_config = self._camera.create_preview_configuration()
            self._camera.configure(camera_config)

            self.switch_config("preview")

    def switch_config(self, new_config):
        self.log_info("Switching to config: {}", new_config)

        # Stop and change config
        self._camera.stop()
        self._camera.configure(new_config)
        self._camera.start()

    def teardown(self):
        pass
