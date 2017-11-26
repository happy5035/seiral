# -*- coding: utf-8 -*-
import datetime

s = 'b0efaa21'
re_s = ''
for i in range(len(s), 0, -2):
    re_s += s[i - 2:i]
print(re_s)
bytes_s = bytes().fromhex(re_s)
result = int().from_bytes(bytes_s, byteorder='big')
print(result)
begin = datetime.datetime(2000, 1, 1)
now = begin + datetime.timedelta(seconds=result)
print(now)
