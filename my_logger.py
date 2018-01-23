# -*- coding: utf-8 -*-
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger()
logging.basicConfig(
                    format='[%(asctime)s %(name)s-%(levelname)s-%(module)s-line:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s %(name)s-%(levelname)s-%(module)s-line:%(lineno)d] %(message)s')
console.setFormatter(formatter)
# logging.getLogger('').addHandler(console)
fileshandle = logging.handlers.TimedRotatingFileHandler('log/myLog', when='D', interval=1)
fileshandle.suffix = "%Y%m%d_%H%M%S.log"
fileshandle.setLevel(logging.DEBUG)
fileshandle.setFormatter(formatter)
logger.addHandler(fileshandle)
