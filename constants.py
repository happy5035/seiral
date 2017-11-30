# -*- coding: utf-8 -*-

# uart state
SOP_STATE = 0x00
CMD_STATE1 = 0x01
CMD_STATE2 = 0x02
LEN_STATE = 0x03
DATA_STATE = 0x04
FCS_STATE = 0x05
MT_UART_SOF = 0xFE

POLL = 0x00
SREQ = 0x20
AREQ = 0x40
SRSP = 0x60
Reserved = 0x00
SYS = 0x01
MAC = 0x02
NWK = 0x03
AF = 0x04
ZDO = 0x05
SAPI = 0x06
UTIL = 0x07
DEBUG = 0x08
APP = 0x09
CMD0_MASK = 0x60
SUB_SYSTEM_MASK = 0x1F
TYPE_MASK = 0xE0

# cmd0
REQ_APP_MSG = SREQ | APP
REQ_SYS = SREQ | SYS

# cmd1
SYS_SET_TIME = 0x10
APP_MSG = 0x00


SUCCESS = 0x00
FAILED = 0x01
TEMP_HUM_DATA = 0xF0
COOR_START = 0xF3
MASTER_SET_CLOCK = 0xF4
MASTER_SET_FREQ_CMD = 0xF5

GENERICAPP_ENDPOINT = 10
