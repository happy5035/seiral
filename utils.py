# -*- coding: utf-8 -*-
import datetime
from constants import *
from my_logger import logger
import uuid
from msg_queue import *
import dill as pick

begin_time = datetime.datetime(1999, 12, 31, 16, 0, 0)  # 转换成中国时间


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


def verify_temp_time(start_time, offset):
    time = parse_date_1(start_time)
    now = datetime.datetime.utcnow()
    delta_days = (now - time).days
    if delta_days > 0:
        now = now - datetime.timedelta(seconds=offset)
        now_timestamp = now.timestamp()
        begin_time_timestamp = begin_time.timestamp()
        return now_timestamp - begin_time_timestamp
        pass
    else:
        return start_time
        pass

    pass


def update_begin_time(time, offset):
    # 如果发送回来的采集时间没有同步，则更新开始时间
    global begin_time
    time = parse_date_1(time)
    now = datetime.datetime.now()
    delta_days = (now - time).days
    if delta_days > 1:
        # 如果采集时间在一天之前，则认为采集终端时间无效,使用新的开始时间
        begin_time = now - datetime.timedelta(seconds=offset)
        pass
    else:
        # 恢复原始时间
        begin_time = datetime.datetime(1999, 12, 31, 16, 0, 0)  # 转换成中国时间
        pass
    pass


def parse_vcc(vcc):
    vcc_int = bytes_to_int(vcc)
    return vcc_int / 100.0


def parse_pv(pv):
    pv_int = bytes_to_int(pv)
    return pv_int


def parse_time_window(tw):
    tw_int = bytes_to_int(tw)
    return tw_int


def parse_parent(parent):
    return parent


def parse_rssi(rssi):
    rssi_int = bytes_to_int(rssi) - 255
    return rssi_int


def parse_lqi(lqi):
    lqi_int = bytes_to_int(lqi)
    return lqi_int


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


def build_send_data(cmd_type, cmd_id, _len, data=[]):
    send_data_len = 5 + _len
    send_data = [0] * send_data_len
    send_data[0] = MT_UART_SOF
    send_data[1] = _len
    send_data[2] = cmd_type
    send_data[3] = cmd_id
    send_data[4:4 + _len] = data[:]
    send_data[send_data_len - 1] = util_cal_fcs(send_data[1:_len + 4])
    logger.debug('serial data %s' % send_data)
    return send_data


def my_uuid():
    return str(uuid.uuid4())


handler_funcs = {}
handler_funcs_filename = 'handler_funcs.pick'


def register_func(data_func):
    logger.info('register func name:%s , code :%s' % (data_func['name'], data_func['code']))
    handler_funcs[data_func['code']] = {'func': data_func['func'], 'name': data_func['name']}
    pick.dump(handler_funcs, open(handler_funcs_filename, 'wb'))
    pass


def build_code(cmd0, cmd1):
    return '0X%02X0X%02X' % (cmd0, cmd1)
    pass


def get_handler_func(cmd0, cmd1):
    _handler_funcs = pick.load(open(handler_funcs_filename, 'rb'))
    code = build_code(cmd0, cmd1)
    if code in _handler_funcs:
        return _handler_funcs[code]
    else:
        return None
    pass


def find_params_by_name(name):
    import json
    params = json.load(open('params.json'))
    for p in params:
        if p['item_name'] == name:
            return p
        pass


class NvItem:
    item_id = 0
    item_len = 0
    item_value = 0

    def __init__(self, item_id=0, item_len=0, item_value=0):
        self.item_len = item_len
        self.item_id = item_id
        self.item_value = item_value
        pass

    def item_to_list(self):
        data = [0] * (4 + self.item_len)
        data[0:2] = int_to_array(self.item_id, 2)
        data[2:4] = int_to_array(self.item_len, 2)
        data[4:] = int_to_array(self.item_value, self.item_len)
        return len(data), data

    def __repr__(self):
        return '<NvItem (%d,%d,%s)>' % (self.item_id, self.item_len, self.item_value)

    pass
