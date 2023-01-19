from typing import List

from PyQt5 import QtWidgets, QtCore, uic

from cam import Cam
from fw.component import Component
from fw.log import Logger


class App(QtWidgets.QMainWindow):
    cameraFrame: QtWidgets.QFrame
    go: QtWidgets.QPushButton
    destination_open: QtWidgets.QToolButton
    positions_open: QtWidgets.QToolButton
    home: QtWidgets.QPushButton

    positions: QtWidgets.QLineEdit
    destination: QtWidgets.QLineEdit

    camera: Cam
    components: List[Component]

    def __init__(self):
        super().__init__()  # Call the inherited classes __init__ method
        uic.loadUi('mainwindow.ui', self)  # Load the .ui file

        self.logger = Logger()

        # self.camera = Cam(self.cameraFrame)

        self.components = [
            self.logger,
            # self.camera
        ]

    def on_go_clicked(self):
        pass

    def on_destination_open_clicked(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(
            self, self.tr("Open Directory"),
            "/home",
            QtWidgets.QFileDialog.ShowDirsOnly | QtWidgets.QFileDialog.DontResolveSymlinks)

        if directory:
            self.destination.setText(self.tr(directory))

    def on_positions_open_clicked(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(
            self,
            self.tr("Open Positions"), "~",
            self.tr("Position Files (*.pos)"))

        if filename:
            self.positions.setText(self.tr(filename[0]))

    def setup(self):
        self.logger.log(Component.Severity.INFO, "Initializing components")

        self.go.clicked.disconnect()
        self.go.clicked.connect(self.on_go_clicked)

        self.destination_open.clicked.disconnect()
        self.destination_open.clicked.connect(self.on_destination_open_clicked)

        self.positions_open.clicked.disconnect()
        self.positions_open.clicked.connect(self.on_positions_open_clicked)

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
    app.show()

    qt_app.exec()

    app.exit()
    app.teardown()


if __name__ == "__main__":
    import sys

    exit(main(sys.argv))
