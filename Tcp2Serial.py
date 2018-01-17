# -*- coding: utf-8 -*-

import threading
import asyncio
import serial_asyncio
from threading import Thread
import serial
from socket import *

from  constants import *
from utils import *


def timeout():
    print('timeout')


def test1():
    data = [0] * 11
    data[0] = GENERICAPP_ENDPOINT
    data[1] = 0xF7
    data[2] = 21
    data[3] = 1
    data[4] = 6
    data[5:7] = int_to_array(38, 2)
    data[7:9] = int_to_array(1, 2)
    data[9:11] = int_to_array(100, 2)
    _data = build_send_data(REQ_APP_MSG, APP_MSG, len(data), data)
    print(data)
    print(_data)
    _data1 = [hex(b) for b in _data]
    print(_data1)


transport9 = None
transport4 = None


def change_mt_data_fcs(data):
    temp = data[:(len(data) - 1)]
    temp += bytes([data[-1] + 1])
    return temp
    pass


class OutPut9(asyncio.Protocol):
    def connection_made(self, transport):
        global transport9
        self.transport = transport
        print('port opened', transport)
        transport9 = transport
        transport.serial.rts = False

    def data_received(self, data):
        print('com 9 data received', data.hex())
        res = verify_mt_data(data)
        if res:
            data = change_mt_data_fcs(data)
            print('com 4 write data ', data.hex())
            transport4.write(data)
        pass

    def connection_lost(self, exc):
        print('port closed')
        self.transport.loop.stop()


class OutPut4(asyncio.Protocol):
    def connection_made(self, transport):
        global transport4
        transport4 = transport
        print('port opened', transport)
        transport.serial.rts = False

    def data_received(self, data):
        print('com 4 data received', data.hex())
        transport9.write(data)
        pass

    def eof_received(self):
        print('eof')

    def connection_lost(self, exc):
        print('port closed')
        self.transport.loop.stop()


def cal_fcs(data):
    fcs = 0
    for d in data:
        fcs ^= d
    return fcs


def verify_mt_data(data):
    if len(data) >= 5:
        begin_sof = data[0]
        data_len = data[1]
        cmd0 = data[2]
        cmd1 = data[3]
        _data = data[4:(len(data) - 1)]
        fcs = data[-1]
        if begin_sof == 0XFE and len(_data) == data_len and cal_fcs(data[1:(len(data) - 1)]) == fcs:
            print('verify success %s' % data)
            return True
    return False
    pass


def serial_intercept():
    # 拦截串口信息并转发到另外一个串口
    loop = asyncio.get_event_loop()
    coro9 = serial_asyncio.create_serial_connection(loop, OutPut9, 'COM9', baudrate=38400)
    coro4 = serial_asyncio.create_serial_connection(loop, OutPut4, 'COM4', baudrate=38400)
    loop.run_until_complete(coro4)
    loop.run_until_complete(coro9)
    loop.run_forever()
    loop.close()


class SerialThreadSend(Thread):
    def __init__(self, serial, tcp):
        super().__init__()
        self.serial = serial
        self.tcp = tcp

    def run(self):
        while True:
            data = self.serial.read()
            if (len(data)):
                self.tcp.send(data)
            pass
        pass

class TcpThreadSend(Thread):
    def __init__(self, serial, tcp):
        super().__init__()
        self.serial = serial
        self.tcp = tcp

    def run(self):
        while True:
            data = self.tcp.recv(1)
            if (len(data)):
                self.serial.write(data)
            pass
        pass


if __name__ == '__main__':
    host = '192.168.11.254'
    port = 8080
    addr = (host, port)
    tcpClient = socket(AF_INET, SOCK_STREAM)
    tcpClient.connect(addr)
    with serial.Serial('COM8', 38400) as ser:
        serial_thread = SerialThreadSend(ser,tcpClient)
        tcp_thread = TcpThreadSend(ser,tcpClient)
        serial_thread.start()
        tcp_thread.start()
        while True:
            pass
