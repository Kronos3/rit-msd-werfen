from PyQt5.QtWidgets import QWidget, QFormLayout


class Calibrate(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QFormLayout()
        self.setLayout(self.layout)


