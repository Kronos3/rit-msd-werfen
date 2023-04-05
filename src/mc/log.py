import logging
import coloredlogs as coloredlogs

coloredlogs.install(fmt='%(asctime)s,%(msecs)03d %(levelname)s %(message)s')
log = logging.getLogger(__name__)
