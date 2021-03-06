# -*- coding: utf-8 -*-
import json

import serial
from msg_queue import *
from socket import *
from queue import Empty
from threading import Thread
from mt_sys_handler import *
from mt_app_handler import *
from mt_msg import Msg
import threading
from my_logger import logger
from flask import Flask
from flask_socketio import SocketIO, emit
import time
import traceback
import socketserver
import mt_sys
import dill as pickle
import config

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


def msg_handler():
    while True:
        try:

            _msg = msg_queue.get()
            logger.debug('msg coming ')
            t = _msg.cmd_state1 & TYPE_MASK
            if t == SRSP and len(_msg.data):
                if _msg.data[0] == SUCCESS or _msg.data[0] == FAILED:
                    serial_rep_msg_queue.put(_msg.data[0])
            subsystem = _msg.cmd_state1 & SUB_SYSTEM_MASK
            if subsystem == SYS:
                mt_sys_handler(_msg)
                continue
            if subsystem == APP:
                mt_app_handler(_msg)
                continue
            logger.debug('no msg handler: %s' % _msg)
        except Exception as e:
            time.sleep(5)
            logger.error('msg handler error %s' % traceback.format_exc())
    pass


@socketio.on('my event')
def test_message(message):
    emit('my response', {'data': 'got it!'})
    print(message)


class MsgProcessThread(Thread):
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
        if len(self.msg) > idx:
            return int().from_bytes(self.msg[idx], 'little')
        else:
            return None

    def time_out_process(self):
        logger.warning('time out, state = %s' % self.state)
        if self.state != SOP_STATE:
            self.state = SOP_STATE
            self.init_msg()
        pass

    timer = None

    def init_timer(self):
        return threading.Timer(1, self.time_out_process, ())

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
            try:
                for _ in range(self.msg_len):
                    self.msg.append(serial_in_msg_queue.get())
                if self.state == SOP_STATE:
                    char = self.get_one_msg(self.idx)
                    if char == MT_UART_SOF:
                        self.state = LEN_STATE
                        self.msg_len = 1
                        # if not self.timer._is_stopped:
                        #     self.timer = self.init_timer()
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
                    else:
                        logger.warning('fcs failed')
                        # self.msg = self.msg[1:]
                    self.msg = self.msg[self.idx + 1:]
                    self.timer.cancel()
                    # self.timer = self.init_timer()
                    self.state = SOP_STATE
                    self.init_msg()
                    self.idx = -1
                    self.msg_len = 1
                self.idx += self.msg_len
            except Exception as e:
                time.sleep(5)
                logger.error(e)
                pass
        pass


class SendData():
    def __init__(self, client):
        self.client = client

    def send_data(self, data):
        pass


class SerialSendData(SendData):
    def send_data(self, data):
        self.client.write(data)


class TcpSendData(SendData):
    def send_data(self, data):
        if isinstance(data, bytes):
            self.client.send(data)
        elif isinstance(data, list):
            self.client.send(bytes(data))


def serial_send_data(se, data):
    se.write(data)
    pass


def socket_send_data(soc, data):
    soc.send(bytes(data))
    pass


class MsgSendDataThread(Thread):
    def __init__(self, client):
        super().__init__()
        self.client = client

    def run(self):
        while True:
            try:
                send_data = serial_out_msg_queue.get()
                data = send_data['data']
                self.client.send_data(data)
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
            except Exception as e:
                time.sleep(5)
                logger.error(traceback.format_exc())
        pass


def serial_process():
    MsgProcessThread().start()
    with serial.Serial(config.serial_port, config.serial_rate) as ser:
        Thread(target=msg_handler, args=()).start()
        send_data = SerialSendData(ser)
        MsgSendDataThread(send_data).start()
        init_coor_device()
        while True:
            try:
                serial_in_msg_queue.put(ser.read())
            except Exception as e:
                logger.warning('ser closed. \t %s', e)
                ser.close()
                flag = 1
                while True:
                    try:
                        ser.open()
                        init_coor_device()
                        logger.warning('ser re open success')
                        break
                    except Exception as e:
                        if flag:
                            flag = 0
                            logger.warning('%s', e)
                pass

        pass
    pass


def init_coor_device():
    import mt_app_handler
    # 设置协调器时钟
    mt_app_handler.set_coor_clock()

    pass


sync_timer = None


class SyncCoorClockThread(Thread):
    def __init__(self, t):
        super().__init__()
        self.t = t

    def run(self):
        while True:
            try:
                time.sleep(self.t)
                set_coor_clock()
            except Exception as e:
                time.sleep(5)
                logger.error(e)
        pass


def tcp_process():
    msg_process_thread = MsgProcessThread()
    msg_process_thread.setDaemon(True)
    msg_process_thread.start()
    host = config.tcp_addr
    port = config.tcp_port
    addr = (host, port)
    tcp_client = socket(AF_INET, SOCK_STREAM)
    tcp_client.connect(addr)
    tcp_client.settimeout(5 * 60)  # 五分钟没有接收到数据说明直接重新连接
    init_coor_device()
    Thread(target=msg_handler, args=()).start()
    tcp_send_data = TcpSendData(tcp_client)
    msg_send_thread = MsgSendDataThread(tcp_send_data)
    msg_send_thread.setDaemon(True)
    msg_send_thread.start()
    sync_clock_thread = SyncCoorClockThread(1800)  # 30min同步一次时间
    sync_clock_thread.setDaemon(True)
    sync_clock_thread.start()
    while True:
        try:
            serial_in_msg_queue.put(tcp_client.recv(1))
        except Exception as e:
            logger.warning('tcp connect closed \t %s' % traceback.format_exc())
            tcp_client.close()
            while True:
                try:
                    logger.warning('prepare re connect')
                    tcp_client = socket(AF_INET, SOCK_STREAM)
                    tcp_client.settimeout(5 * 60)  # 五分钟没有接收到数据说明直接重新连接
                    tcp_client.connect(addr)
                    tcp_send_data.client = tcp_client
                    init_coor_device()
                    logger.warning('re connect success')
                    break
                except Exception as e:
                    tcp_client.close()
                    logger.warning('%s' % e)


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024)

        serial_out_msg_queue.put({
            'data': data
        })


class ThreadedParamRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024)
        data = str(data, 'utf-8')
        data = json.loads(data)
        items = []
        pv = data['pv']
        data = data['param']
        for d in data:
            param = find_params_by_name(d['name'])
            item = NvItem(int(param['item_id']), int(param['item_len']), int(d['value']))
            items.append(item)
            pass
        logger.info(items)
        msg_data = mt_sys.app_msg_req(pv, items)
        serial_out_msg_queue.put({
            'data': msg_data
        })
        msg_data = mt_sys.app_msg_net_param_update()
        serial_out_msg_queue.put({
            'data': msg_data
        })


class ThreadedTCPRegisterRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024)
        try:
            data_func = pickle.loads(data)
            register_func(data_func=data_func)
        except Exception as e:
            traceback.print_exc(e)
            pass


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    def handle_error(self, request, client_address):
        logger.error(request, client_address)
        pass

    pass


def setup_tcp_server():
    HOST, PORT = "localhost", 8081
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    pass


def setup_param_server():
    HOST, PORT = "localhost", 8088
    server = ThreadedTCPServer((HOST, PORT), ThreadedParamRequestHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    pass


def setup_register_func_server():
    HOST, PORT = "localhost", 8082
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRegisterRequestHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    pass


if __name__ == '__main__':
    setup_tcp_server()
    setup_param_server()
    setup_register_func_server()
    if config.connect_type == 'serial':
        serial_process()
    else:
        tcp_process()
