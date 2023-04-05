import functools

from PyQt5 import QtWidgets, QtCore
import threading
import queue

# from mc.cli import create_system


def qasync(func):
    @functools.wraps(func)
    def append_to_queue(*args, **kwargs):
        args[0].messages.put((func, args, kwargs), block=False)
    return append_to_queue


class UiSystem(threading.Thread):
    position: int = 0
    messages: queue.Queue
    mutex: threading.Lock
    keep_alive: bool

    def __init__(self, system):
        super().__init__()
        self.system = system
        self.keep_alive = True
        self.messages = queue.Queue(50)
        self.mutex = threading.Lock()

    def run(self):
        while self.keep_alive:
            try:
                func, args, kwargs = self.messages.get(block=True, timeout=1)
                with self.mutex:
                    func(*args, **kwargs)
            except Exception:
                # Update the status flags periodically if there are no other requests
                # Otherwise other requests will handle the status updates
                with self.mutex:
                    if self.system:
                        self.system.stage.idle()

    @qasync
    def exit(self):
        self.keep_alive = False

    @qasync
    def single_card(self, delay: float, path: str):
        self.system.single_card(str(delay), path)


class StatusBar(QtWidgets.QStatusBar):
    def __init__(self, system, parent=None):
        super().__init__(parent)

        self.system = system

        self.limit_1 = QtWidgets.QLabel()
        self.limit_2 = QtWidgets.QLabel()
        self.running = QtWidgets.QLabel()
        self.led = QtWidgets.QLabel()
        self.addWidget(self.limit_1)
        self.addWidget(self.limit_2)
        self.addWidget(self.running)
        self.addWidget(self.led)

        self.interval = QtCore.QTimer()
        self.interval.connectNotify(self.update)
        self.interval.setInterval(100)
        self.interval.start(100)

    @staticmethod
    def _style_bool(value: bool, on = "ON", off = "OFF"):
        if value:
            return f'<b style="color=green">{on}</b>'
        else:
            return f'<b style="color=red">{off}</b>'

    def update(self):
        self.limit_1.setText(f"LIMIT-1: {self._style_bool(self.system.stage.limit_1)}")
        self.limit_2.setText(f"LIMIT-2: {self._style_bool(self.system.stage.limit_1)}")
        self.running.setText(f"STAGE: {self._style_bool(self.system.stage.running), 'RUNNING', 'IDLE'}")
        self.limit_2.setText(f"LED: {self._style_bool(self.system.stage.led)}")


class App(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.operate_tab = QtWidgets.QWidget()
        self.calibrate_tab = QtWidgets.QWidget()
        self.operate_tab_layout = QtWidgets.QVBoxLayout(self.operate_tab)
        self.calibrate_tab_layout = QtWidgets.QVBoxLayout(self.calibrate_tab)

        self.tabs = QtWidgets.QTabWidget()
        self.tabs.addTab(self.operate_tab, "Operate")
        self.tabs.addTab(self.calibrate_tab, "Calibrate")
        self.setCentralWidget(self.tabs)


def main(args):
    qt_app = QtWidgets.QApplication(args)

    # system = create_system(args)
    ui_system = UiSystem(None)
    ui_system.start()

    app = App()

    app.show()
    qt_app.exec()

    ui_system.exit()
    ui_system.join()


if __name__ == "__main__":
    import sys

    exit(main(sys.argv))
