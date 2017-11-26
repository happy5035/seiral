# -*- coding: utf-8 -*-
from constants import *

class Msg:
    def __init__(self, msg):
        self.sop = SOP_STATE
        self.len = msg['len']
        self.cmd_state1 = msg['cmd_state1']
        self.cmd_state2 = msg['cmd_state2']
        self.data = msg['data']
        self.fcs = msg['fcs']
