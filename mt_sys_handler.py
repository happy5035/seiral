# -*- coding: utf-8 -*-
from my_logger import logger
from constants import *


def mt_sys_handler(msg, ser):
    logger.debug('sys handler')
    if len(msg.data):
        if msg.data[0] == SUCCESS:
            logger.info('success')
    pass
