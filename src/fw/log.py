import enum
import logging

import coloredlogs as coloredlogs

from fw.component import Component, async_message


class Logger(Component):
    class Type(enum.Enum):
        CONSOLE = enum.auto()

    _type: Type

    def __init__(self, t: Type = Type.CONSOLE):
        super().__init__()
        self._type = t
        self.logger = None

        # Do the true setup during __init__
        # This will allow components to log during setup
        if self._type == Logger.Type.CONSOLE:
            coloredlogs.install(fmt='%(asctime)s,%(msecs)03d %(levelname)s %(message)s')
            self.logger = logging.getLogger(__name__)

        from fw.registry import registry
        registry.logger = self

    def _console_log(self, severity: Component.Severity, component: str, format_str: str, *args):
        message = format_str.format(args)

        if severity == Component.Severity.INFO:
            self.logger.info("[%s] %s", component, message)
        elif severity == Component.Severity.DEBUG:
            self.logger.debug("[%s] %s", component, message)
        elif severity == Component.Severity.ERROR:
            self.logger.error("[%s] %s", component, message)
        elif severity == Component.Severity.WARNING:
            self.logger.warning("[%s] %s", component, message)
        elif severity == Component.Severity.CRITICAL:
            self.logger.critical("[%s] %s", component, message)
        else:
            self.logger.error("[%s] %s", component, message)

    @async_message
    def log_recv(self, severity: Component.Severity,
                 component: str, format_str: str, *args):
        if self._type == Logger.Type.CONSOLE:
            self._console_log(severity, component, format_str, *args)

    def setup(self):
        pass

    def teardown(self):
        pass
