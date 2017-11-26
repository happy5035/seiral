# -*- coding: utf-8 -*-

import serial
from queue import Queue
from threading import Thread
from mt_sys_handler import *
from mt_app_handler import *
from mt_msg import Msg
import threading
from my_logger import logger

msg_queue = Queue()

state = SOP_STATE
timer = None
msg = {
    'sop': SOP_STATE,
    'len': 0,
    'cmd_state1': 0,
    'cmd_state2': 0,
    'data': bytes(),
    'fcs': 0
}


def timeout_timer():
    global state
    state = SOP_STATE
    logger.error('time out')


def init_msg():
    global msg
    msg = {
        'sop': SOP_STATE,
        'len': 0,
        'cmd_state1': 0,
        'cmd_state2': 0,
        'data': bytes(),
        'fcs': 0
    }


def sop_state(ser):
    global state
    global timer
    ch = ser.read()
    if len(ch) == 0:
        return
    ch = int().from_bytes(ch, 'big')
    if ch == MT_UART_SOF:
        timer = threading.Timer(1, timeout_timer)
        state = LEN_STATE
        logger.debug('read uart sof %02x' % ch)


def len_state(ser):
    global state
    ch = ser.read()
    if len(ch) == 0:
        return
    ch = int().from_bytes(ch, 'big')
    len_token = ch
    msg['len'] = len_token
    state = CMD_STATE1
    logger.debug('len state %d' % ch)


def cmd_state1(ser):
    global state
    ch = ser.read()
    if len(ch) == 0:
        return
    ch = int().from_bytes(ch, 'big')
    msg['cmd_state1'] = ch
    state = CMD_STATE2
    logger.debug('cmd state1 %02x' % ch)


def cmd_state2(ser):
    global state
    ch = ser.read()
    if len(ch) == 0:
        return
    ch = int().from_bytes(ch, 'big')
    msg['cmd_state2'] = ch
    if msg['len'] == 0:
        state = FCS_STATE
    else:
        state = DATA_STATE
    logger.debug('cmd state2 %02x' % ch)


def data_state(ser):
    global state
    data_length = msg['len'] - len(msg['data'])
    chs = ser.read(data_length)
    if len(chs) == 0:
        return
    msg['data'] += chs
    if msg['len'] == len(msg['data']):
        state = FCS_STATE
    logger.debug('data state %s' % chs.hex())


def cal_fcs():
    fcs_token = 0
    fcs_token ^= msg['len']
    fcs_token ^= msg['cmd_state1']
    fcs_token ^= msg['cmd_state2']
    for i in range(msg['len']):
        fcs_token ^= msg['data'][i]
    return fcs_token


def fcs_state(ser):
    global state
    ch = ser.read()
    if len(ch) == 0:
        return
    ch = int().from_bytes(ch, 'big')
    logger.debug('fcs %02x' % ch)
    fcs_token = cal_fcs()
    if fcs_token == ch:
        mt_msg = Msg(msg)
        msg_queue.put(mt_msg)
        logger.debug('fcs success')
    else:
        logger.debug('fcs failed')
    state = SOP_STATE
    init_msg()
    timer.cancel()


functions = {
    SOP_STATE: sop_state,
    LEN_STATE: len_state,
    CMD_STATE1: cmd_state1,
    CMD_STATE2: cmd_state2,
    DATA_STATE: data_state,
    FCS_STATE: fcs_state
}


def msg_handler(ser):
    while True:
        _msg = msg_queue.get()
        logger.debug('msg coming')
        subsystem = _msg.cmd_state1 & SUB_SYSTEM_MASK
        if subsystem == SYS:
            mt_sys_handler(_msg, ser)
            continue
        if subsystem == APP:
            mt_app_handler(_msg, ser)
            continue
    pass


if __name__ == '__main__':
    with serial.Serial('COM4', 38400) as ser:
        Thread(target=msg_handler, args=(ser,)).start()
        while True:
            func = functions[state]
            func(ser)
        pass
    pass
