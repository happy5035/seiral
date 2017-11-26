# -*- coding: utf-8 -*-
from utils import *
from constants import *
from my_logger import logger
import datetime


def temp_hum_handler(msg):
    data = msg.data
    idx = 1
    ext_addr = data[idx:idx + 8]
    idx += 8
    logger.debug('ext addr %s' % ext_addr.hex())

    vcc = data[idx:idx + 2]
    logger.debug('vcc %.2fV' % parse_vcc(vcc))
    idx += 2

    temp_start_time = data[idx:idx + 4]
    logger.debug('temp start time %s' % parse_date(temp_start_time))
    idx += 4

    temp_freq = data[idx:idx + 2]
    logger.debug('temp freq %s' % parse_freq(temp_freq))
    idx += 2

    temp_number = data[idx:idx + 1]
    logger.debug('temp number %d' % temp_number[0])
    idx += 1

    hum_start_time = data[idx:idx + 4]
    logger.debug('hum start time %s' % parse_date(hum_start_time))
    idx += 4

    hum_freq = data[idx:idx + 2]
    logger.debug('hum freq %s' % parse_freq(hum_freq))
    idx += 2

    hum_number = data[idx:idx + 1]
    logger.debug('hum number %d' % hum_number[0])
    idx += 1

    temp_data_length = temp_number[0] * 2
    temp_data = data[idx:idx + temp_data_length]
    logger.debug('temp data %s' % parse_temp(temp_data, temp_data_length))
    idx += temp_data_length

    hum_data_length = hum_number[0] * 2
    hum_data = data[idx:idx + hum_data_length]
    logger.debug('hum data %s' % parse_hum(hum_data, hum_data_length))
    idx += hum_data_length


# 设置协调器时钟
def set_coor_clock(ser):
    now = datetime.datetime.now()
    data = [0] * 11
    data[4] = now.hour
    data[5] = now.minute
    data[6] = now.second
    data[7] = now.month
    data[8] = now.day
    data[9:11] = int_to_array(now.year, 2)
    build_send_data(ser, REQ_SYS, SYS_SET_TIME, len(data), data)
    logger.debug('set coor clock %s' % data)


def coor_start_handler(msg, ser):
    set_coor_clock(ser)
    pass


def mt_app_handler(msg, ser):
    logger.debug('app handler')
    if len(msg.data):
        if msg.data[0] == TEMP_HUM_DATA:
            temp_hum_handler(msg)
            return
        if msg.data[0] == COOR_START:
            logger.warning('coor start')
            coor_start_handler(msg, ser)
            return
        if msg.data[0] == SUCCESS:
            logger.info('cmd success')
            return
        pass
    else:
        logger.warning('app msg data empty')
