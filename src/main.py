from typing import List

from PyQt5 import QtWidgets, uic

from cam import Cam
from fw.component import Component
from fw.log import Logger


class App(QtWidgets.QMainWindow):
    camera: Cam
    components: List[Component]

    def __init__(self):
        super().__init__()

        self.tabs = Tabs()

        layout_h = QtWidgets.QHBoxLayout()
        layout_h.addWidget(self.tabs)

        self.setLayout(layout_h)

        self.logger = Logger()
        self.camera = Cam(self, layout_h)

        self.components = [
            self.logger,
            self.camera
        ]

    def setup(self):
        self.logger.log(Component.Severity.INFO, "Initializing components")
        self.tabs.setup()
        for comp in self.components:
            comp.setup()

    def start(self):
        for comp in self.components:
            comp.start()

    def teardown(self):
        for comp in self.components:
            comp.teardown()

    def exit(self):
        for comp in self.components:
            comp.exit()
            comp.join()


def main(args):
    qt_app = QtWidgets.QApplication(args)
    app = App()

    app.setup()
    app.start()
    app.showMaximized()

    qt_app.exec()

    app.exit()
    app.teardown()


if __name__ == "__main__":
    import sys

    exit(main(sys.argv))
