# -*- coding: utf-8 -*-

import serial
from msg_queue import *
from queue import Empty
from threading import Thread
from mt_sys_handler import *
from mt_app_handler import *
from mt_msg import Msg
import threading
from my_logger import logger
from flask import Flask
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'xjtu'
socketio = SocketIO(app)

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


def len_state(ser):
    global state
    ch = ser.read()
    if len(ch) == 0:
        return
    ch = int().from_bytes(ch, 'big')
    len_token = ch
    msg['len'] = len_token
    state = CMD_STATE1


def cmd_state1(ser):
    global state
    ch = ser.read()
    if len(ch) == 0:
        return
    ch = int().from_bytes(ch, 'big')
    msg['cmd_state1'] = ch
    state = CMD_STATE2


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


def data_state(ser):
    global state
    data_length = msg['len'] - len(msg['data'])
    chs = ser.read(data_length)
    if len(chs) == 0:
        return
    msg['data'] += chs
    if msg['len'] == len(msg['data']):
        state = FCS_STATE


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
    fcs_token = cal_fcs()
    if fcs_token == ch:
        mt_msg = Msg(msg)
        msg_queue.put(mt_msg)
        logger.debug(mt_msg)
        logger.debug('fcs success')
    else:
        logger.info('fcs failed')
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
        logger.debug('msg coming ')
        t = _msg.cmd_state1 & TYPE_MASK
        if t == SRSP and len(_msg.data):
            if _msg.data[0] == SUCCESS or _msg.data[0] == FAILED:
                serial_rep_msg_queue.put(_msg.data[0])
        subsystem = _msg.cmd_state1 & SUB_SYSTEM_MASK
        if subsystem == SYS:
            mt_sys_handler(_msg, ser)
            continue
        if subsystem == APP:
            mt_app_handler(_msg, ser)
            continue
    pass


@socketio.on('my event')
def test_message(message):
    emit('my response', {'data': 'got it!'})
    print(message)


# class SerialReadThread(Thread):
#     def serial(self, ser):
#         self.ser = ser
#
#     def run(self):
#         while True:
#             serial_msg_queue.put(ser.read())
#         pass


class SerialProcessThread(Thread):
    msg = []
    idx = 0
    msg_len = 1
    state = SOP_STATE
    data = {
        'sop': SOP_STATE,
        'len': 0,
        'cmd_state1': 0,
        'cmd_state2': 0,
        'data': bytes(),
        'fcs': 0
    }

    def get_one_msg(self, idx):
        return int().from_bytes(self.msg[idx], 'little')

    def time_out_process(self):
        logger.warning('time out, state = %s' % self.state)
        if self.state != SOP_STATE:
            self.state = SOP_STATE
            self.init_msg()
        pass

    timer = None

    def init_timer(self):
        return threading.Timer(1, self.time_out_process, (self,))

    def init_msg(self):
        self.data = {
            'sop': SOP_STATE,
            'len': 0,
            'cmd_state1': 0,
            'cmd_state2': 0,
            'data': bytes(),
            'fcs': 0
        }

    def cal_fcs(self):
        fcs_token = 0
        fcs_token ^= self.data['len']
        fcs_token ^= self.data['cmd_state1']
        fcs_token ^= self.data['cmd_state2']
        for i in range(self.data['len']):
            fcs_token ^= self.data['data'][i]
        return fcs_token

    def run(self):
        self.timer = self.init_timer()
        while True:
            for _ in range(self.msg_len):
                self.msg.append(serial_in_msg_queue.get())
            if self.state == SOP_STATE:
                char = self.get_one_msg(self.idx)
                if char == MT_UART_SOF:
                    self.state = LEN_STATE
                    self.msg_len = 1
                    # self.timer.start()
            elif self.state == LEN_STATE:
                char = self.get_one_msg(self.idx)
                self.data['len'] = char
                self.state = CMD_STATE1
                self.msg_len = 1
            elif self.state == CMD_STATE1:
                char = self.get_one_msg(self.idx)
                self.data['cmd_state1'] = char
                self.state = CMD_STATE2
                self.msg_len = 1
            elif self.state == CMD_STATE2:
                char = self.get_one_msg(self.idx)
                self.data['cmd_state2'] = char
                if self.data['len'] == 0:
                    self.state = FCS_STATE
                    self.msg_len = 1
                else:
                    self.state = DATA_STATE
                    self.msg_len = self.data['len']
            elif self.state == DATA_STATE:
                chs = self.msg[self.idx - self.data['len'] + 1:self.idx + 1]
                for b in chs:
                    self.data['data'] += b
                self.state = FCS_STATE
                self.msg_len = 1
                pass
            elif self.state == FCS_STATE:
                char = self.get_one_msg(self.idx)
                fcs = self.cal_fcs()
                if fcs == char:
                    mt_msg = Msg(self.data)
                    msg_queue.put(mt_msg)
                    logger.info('add msg : %s' % mt_msg)
                    self.msg = self.msg[self.idx + 1:]
                else:
                    logger.warning('fcs failed')
                    self.msg = self.msg[1:]
                self.timer.cancel()
                self.timer = self.init_timer()
                self.state = SOP_STATE
                self.init_msg()
                self.idx = -1
                self.msg_len = 1
            self.idx += self.msg_len
        pass


class SerialSendDataThread(Thread):
    def __init__(self, seri):
        super().__init__()
        self.serial = seri

    def run(self):
        while True:
            send_data = serial_out_msg_queue.get()
            data = send_data['data']
            ser.write(data)
            try:
                rep = serial_rep_msg_queue.get(timeout=2)
                if rep == SUCCESS:
                    logger.info('rep success,data = %s' % data)
                    pass
                if rep == FAILED:
                    logger.warning('rep failed,data =  %s' % data)
                    pass
            except Empty as e:
                logger.warning('rep timeout,data =  %s' % data)
                pass

        pass


if __name__ == '__main__':
    # Thread(target=socketio.run, args=(app, '127.0.0.1', 8088,)).start()
    SerialProcessThread().start()
    with serial.Serial('COM4', 38400) as ser:
        Thread(target=msg_handler, args=(ser,)).start()
        SerialSendDataThread(ser).start()
        while True:
            serial_in_msg_queue.put(ser.read())
        pass
    pass
