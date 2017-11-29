# -*- coding: utf-8 -*-
import datetime
from constants import *
from my_logger import logger
import uuid
from msg_queue import *

begin_time = datetime.datetime(2000, 1, 1)


def bytes_to_int(data):
    temp_str = data.hex()
    data_str = ''
    for i in range(len(temp_str), 0, -2):
        data_str += temp_str[i - 2:i]
    data_int = int().from_bytes(bytes().fromhex(data_str), 'big')
    return data_int


def bytes_to_int_1(data, length):
    data_int = 0
    for i in range(length - 1, -1, -1):
        b = data[i]
        data_int |= b
        if i is not 0:
            data_int <<= 8
    return data_int


def int_to_array(data, length):
    array = []
    for i in range(length):
        array.append(data >> (8 * i) & 0xFF)
    return array
    pass


def parse_date(time):
    time_int = bytes_to_int(time)
    time = begin_time + datetime.timedelta(seconds=time_int)
    return time


def parse_date_1(time):
    return begin_time + datetime.timedelta(seconds=time)


def parse_vcc(vcc):
    vcc_int = bytes_to_int(vcc)
    return vcc_int / 100.0


def parse_freq(freq):
    return bytes_to_int(freq)


def parse_temp(temp, length):
    temps = []
    for i in range(0, length, 2):
        _temp_bytes = temp[i:i + 2]
        _temp = bytes_to_int(_temp_bytes)
        temps.append(_temp / 100.0)
    return temps
    pass


def parse_hum(hum, length):
    hums = []
    for i in range(0, length, 2):
        _hums_bytes = hum[i:i + 2]
        _hum = bytes_to_int(_hums_bytes)
        hums.append(_hum / 100.0)
    return hums
    pass


def util_cal_fcs(data):
    fcs_token = 0
    for d in data:
        fcs_token ^= d
    return fcs_token


def build_send_data(ser, cmd_type, cmd_id, _len, data):
    send_data_len = 5 + _len
    send_data = [0] * send_data_len
    send_data[0] = MT_UART_SOF
    send_data[1] = _len
    send_data[2] = cmd_type
    send_data[3] = cmd_id
    send_data[4:4 + _len] = data[:]
    send_data[send_data_len - 1] = util_cal_fcs(send_data[1:_len + 4])
    logger.debug('serial data %s' % send_data)
    # serial_out_msg_queue.put(send_data)
    return send_data
    # ser.write(send_data)
    pass


def my_uuid():
    return str(uuid.uuid4())
