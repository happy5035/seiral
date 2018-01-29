# -*- coding: utf-8 -*-
from my_logger import logger
from constants import *
from mt_msg import Msg
from utils import *


def mt_sys_handler(msg: Msg):
    logger.debug('sys handler')
    if len(msg.data):
        if msg.data[0] == SUCCESS:
            logger.info('success')
        handler_info = get_handler_func(msg.cmd_state1, msg.cmd_state2)
        if handler_info:
            handler_name = handler_info['name']
            handler_func = handler_info['func']
            logger.info('handler func %s' % handler_name)
            handler_func(msg)
            pass
        else:
            logger.warning('handler func not found')
    pass
