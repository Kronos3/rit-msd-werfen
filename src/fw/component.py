import queue
import threading
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Optional, Callable, Tuple


def async_message(handler: Callable):
    def queue_message(*args):
        self: Component = args[0]
        self._message_queue.put_nowait((handler, args))

    return queue_message


class Component(threading.Thread, ABC):
    _message_queue: queue.Queue[Tuple[Callable, Tuple[any]]]
    _name: str
    _keep_alive: bool

    class Severity(Enum):
        DEBUG = auto()
        INFO = auto()
        WARNING = auto()
        ERROR = auto()
        CRITICAL = auto()

    def __init__(self, name: Optional[str] = None):
        super().__init__()
        self._message_queue = queue.Queue()
        self._name = name if name is not None else self.__class__.__name__

        self._keep_alive = True

    def __str__(self):
        return self._name

    def run(self):
        while self._keep_alive:
            handler, args = self._message_queue.get()
            handler(*args)
            self._message_queue.task_done()

    @async_message
    def exit(self):
        self._keep_alive = False

    @async_message
    def quit(self):
        self._keep_alive = False

    def log(self, severity: Severity, format_str: str, *args):
        from fw.registry import registry
        registry.logger.log_recv(severity, self._name, format_str, *args)

    def log_debug(self, format_str: str, *args):
        self.log(Component.Severity.DEBUG, format_str, *args)

    def log_info(self, format_str: str, *args):
        self.log(Component.Severity.INFO, format_str, *args)

    def log_warning(self, format_str: str, *args):
        self.log(Component.Severity.WARNING, format_str, *args)

    def log_error(self, format_str: str, *args):
        self.log(Component.Severity.ERROR, format_str, *args)

    def log_critical(self, format_str: str, *args):
        self.log(Component.Severity.CRITICAL, format_str, *args)

    @abstractmethod
    def setup(self):
        """
        Called at bootup time
        Perform initial setup
        """
        ...

    @abstractmethod
    def teardown(self):
        """
        Call at closing time
        """
        ...
