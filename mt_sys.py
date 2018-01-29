# -*- coding: utf-8 -*-
import types

from utils import *
import socket

import dill as pickle


def sys_osal_nv_read_req(item_id):
    data = [0] * 3
    data[:2] = int_to_array(item_id, 2)
    data[2] = 0
    return build_send_data(0x21, 0x08, 3, data)

    pass


def sys_osal_nv_read_rsp(msg):
    status = msg.data[0]
    if status == 0:
        status = 'Success'
    else:
        status = 'Failure'
    length = msg.data[1]
    value = msg.data[2:]
    logger.info(
        'nv read  \nStatus:%s\nLen:%x\nValue:%s' % (status, length, ','.join('0X{:02x}'.format(x) for x in value)))
    pass


def sys_osal_nv_write_req(item_id, item_len, item_value):
    data = [0] * (4 + len(item_value))
    data[0:2] = int_to_array(item_id, 2)
    data[2] = 0
    data[3] = item_len
    data[4:] = item_value
    return build_send_data(0x21, 0x09, len(data), data)
    pass


def sys_osal_nv_write_rsp(msg):
    data = msg.data
    logger.info('nv write rsp : 0X%02X' % bytes_to_int(msg.data))
    pass


def sys_osal_nv_init_req(item_id, item_len):
    data = [0] * 5
    data[:2] = int_to_array(item_id, 2)
    data[2:4] = int_to_array(item_len, 2)
    data[4] = 0
    return build_send_data(0x21, 0x07, 5, data)
    pass


def sys_osal_nv_init_rsp(msg):
    data = msg.data
    data = bytes_to_int_1(data, 1)
    if data == 0:
        logger.info('Item already exists')
    elif data == 0x09:
        logger.info('Success')
    elif data == 0x0A:
        logger.info('Initialization failed')
    pass


def sys_get_time_req():
    return build_send_data(0x21, 0x11, 0)
    pass


def sys_get_time_rsp(msg):
    data = msg.data
    utc_time = bytes_to_int_1(data[:4], 4)
    hour = data[4]
    minute = data[5]
    second = data[6]
    month = data[7]
    day = data[8]
    year = bytes_to_int_1(data[9:], 2)
    logger.info(
        'get time resp:\nutc_time:%d\ndate:%d-%d-%d %d:%d:%d' % (utc_time, year, month, day, hour, minute, second))
    pass


def sys_set_time():
    pass


def sys_ping_req():
    return build_send_data(0x21, 0x01, 0)
    pass


def sys_ping_rsp(msg):
    logger.info(msg)
    cap = ['MT_CAP_SYS', 'MT_CAP_MAC', 'MT_CAP_NWK', 'MT_CAP_AF', 'MT_CAP_ZDO', 'MT_CAP_SAPI', 'MT_CAP_UTIL',
           'MT_CAP_DEBUG', 'MT_CAP_APP', 'MT_CAP_ZOAD']
    mask = 0x01
    value = bytes_to_int_1(msg.data, 2)
    cap_str = []
    for idx, c in enumerate(cap):
        if (value & mask << idx) != 0:
            cap_str.append(c)
            pass
        pass
    logger.info('Capabilities:%s' % cap_str)
    pass


def sys_reset_req(_type):
    return build_send_data(cmd_type=0x41, cmd_id=0x00, _len=1, data=[_type])
    pass


def client(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    return sock


def register_func1():
    sock = client('localhost', 8082)

    code = build_code(0x61, 0x09)
    data = pickle.dumps({'code': code, 'func': sys_osal_nv_write_rsp, 'name': 'sys_osal_nv_write_rsp'})
    sock.send(data)
    sock.close()
    pass


def app_msg_req():
    pv = 6
    size = 1
    item_id = 1026
    item_len = 4
    item_value = int_to_array(5000, 4)
    data = [0] * 13
    idx = 0
    data[idx] = GENERICAPP_ENDPOINT
    idx += 1
    data[idx] = MASTER_SET_NV_CONFIG_CMD
    idx += 1
    data[idx] = pv
    idx += 1
    data[idx] = size
    idx += 1
    data[idx] = 8
    idx += 1
    data[idx:idx + 2] = int_to_array(item_id, 2)
    idx += 2
    data[idx:idx + 2] = int_to_array(item_len, 2)
    idx += 2
    data[idx:idx + 4] = item_value
    idx += 4
    return build_send_data(0x29, 0x00, len(data), data)
    pass


def find_params_by_name(name):
    import json
    params = json.load(open('params.json'))
    for p in params:
        if p['item_name'] == name:
            return p
        pass


def send_cmd():
    sock = client('localhost', 8081)
    pf = find_params_by_name('param_flag')
    # data = sys_osal_nv_write_req(pf['item_id'], pf['item_len'], item_value=[0, 0, 0, 0])
    # pv = sys_osal_nv_read_req(1025)
    data = app_msg_req()
    sock.send(bytes(data))
    data = sys_osal_nv_read_req(1025)
    sock.send(bytes(data))
    sock.close()


if __name__ == '__main__':
    # register_func1()
    send_cmd()
    # data = '28f701220f0f34011de207'
    # b_data = bytearray.fromhex(data)
    # sys_get_time_rsp(b_data)
