# -*- coding: utf-8 -*-
from utils import *
from constants import *
from my_logger import logger
import datetime
from Models import *
from dbhelper import *
import uuid


def set_end_freq(net_addr='0000', temp_freq=0, hum_freq=0, packet_freq=0, clock_freq=0):
    logger.debug('set %s end: temp freq:%d,hum_freq:%d,packet_freq:%d,clock_freq:%d' % (
        net_addr, temp_freq, hum_freq, packet_freq, clock_freq))
    data = [0] * 19
    idx = 0
    data[idx] = GENERICAPP_ENDPOINT
    idx += 1
    data[idx] = MASTER_SET_FREQ_CMD
    idx += 1
    data[idx:idx + 2] = [b for b in bytes().fromhex(net_addr)]
    idx += 2
    data[idx:idx + 4] = int_to_array(temp_freq, 4)
    idx += 4
    data[idx:idx + 4] = int_to_array(hum_freq, 4)
    idx += 4
    data[idx:idx + 4] = int_to_array(packet_freq, 4)
    idx += 4
    data[idx:idx + 4] = int_to_array(clock_freq, 4)
    send_data = build_send_data(REQ_APP_MSG, APP_MSG, len(data), data)
    serial_out_msg_queue.put({
        'type': 'set freq',
        'data': send_data
    })
    logger.debug('set end freq %s' % data)
    pass


def temp_hum_handler(msg):
    data = msg.data
    idx = 1

    net_addr = data[idx:idx + 2]
    idx += 2
    logger.debug('net addr %s' % net_addr.hex())

    ext_addr = data[idx:idx + 8]
    idx += 8
    logger.debug('ext addr %s' % ext_addr.hex())

    vcc = data[idx:idx + 2]
    logger.debug('vcc %.2fV' % parse_vcc(vcc))
    idx += 2

    pv = data[idx:idx + 1]
    logger.debug('params version %d' % parse_pv(pv))
    idx += 1

    tw = data[idx:idx + 2]
    logger.debug('time window %d' % parse_time_window(tw))
    idx += 2

    parent = data[idx:idx + 2]
    logger.debug('parent  %s' % parent.hex())
    idx += 2

    temp_start_time = data[idx:idx + 4]
    logger.debug('temp start time %s' % parse_date(temp_start_time))
    temp_start_time = bytes_to_int_1(temp_start_time, 4)
    idx += 4

    temp_freq = data[idx:idx + 4]
    logger.debug('temp freq %s' % parse_freq(temp_freq))
    idx += 4

    temp_number = data[idx:idx + 1]
    logger.debug('temp number %d' % temp_number[0])
    temp_number = temp_number[0]
    idx += 1

    hum_start_time = data[idx:idx + 4]
    logger.debug('hum start time %s' % parse_date(hum_start_time))
    hum_start_time = bytes_to_int_1(hum_start_time, 4)
    idx += 4

    hum_freq = data[idx:idx + 4]
    logger.debug('hum freq %s' % parse_freq(hum_freq))
    idx += 4

    hum_number = data[idx:idx + 1]
    logger.debug('hum number %d' % hum_number[0])
    hum_number = hum_number[0]
    idx += 1

    temp_data_length = temp_number * 2
    temp_data = data[idx:idx + temp_data_length]
    logger.debug('temp data %s' % parse_temp(temp_data, temp_data_length))
    idx += temp_data_length

    hum_data_length = hum_number * 2
    hum_data = data[idx:idx + hum_data_length]
    logger.debug('hum data %s' % parse_hum(hum_data, hum_data_length))
    idx += hum_data_length

    rssi = data[idx:idx + 1]
    logger.debug('rssi %d db' % parse_rssi(rssi))
    idx += 1

    lqi = data[idx:idx + 1]
    logger.debug('Link LinkQuality %d' % parse_lqi(lqi))

    ed = EndDevice()
    hums = []
    temps = []
    ed.net_addr = net_addr.hex()
    ed.ext_addr = ext_addr.hex()
    ed.voltage = parse_vcc(vcc)
    ed.temp_freq = bytes_to_int_1(temp_freq, 2)
    ed.hum_freq = bytes_to_int_1(hum_freq, 2)
    ed.rssi = parse_rssi(rssi)
    ed.lqi = parse_lqi(lqi)
    ed.pv = parse_pv(pv)
    ed.parent = parent.hex()
    ed.time_window = parse_time_window(tw)
    end_device_id = find_end_device_id(ed.ext_addr)
    if not end_device_id:
        _ed = add_end_device(ed)
        end_device_id = _ed.end_device_id
        pass
    _temps = parse_temp(temp_data, temp_data_length)
    if len(_temps):
        update_begin_time(temp_start_time, len(_temps) * (ed.temp_freq / 1000))

    for t in _temps:
        temp = Temperature()
        temp.temp_id = my_uuid()
        temp.end_device_id = end_device_id
        temp.temp_time = parse_date_1(temp_start_time)
        temp_start_time += ed.temp_freq / 1000
        temp.temp_value = t
        temps.append(temp)
    if len(temps):
        ed.temp = temps[-1].temp_value
        ed.update_time = temps[-1].temp_time
        pass
    add_temperature_all(temps)
    _hums = parse_hum(hum_data, hum_data_length)
    for h in _hums:
        hum = Humidity()
        hum.humi_id = my_uuid()
        hum.end_device_id = end_device_id
        hum.humi_time = parse_date_1(hum_start_time)
        hum_start_time += ed.hum_freq / 1000
        hum.humi_value = h
        hums.append(hum)
    if len(hums):
        ed.hum = hums[-1].humi_value
        ed.update_time = hums[-1].humi_time
        pass
    add_humidity_all(hums)
    # set_end_freq(ed.net_addr, 10000, 30000, 60000, 0)

    update_end_device(ed, {'ext_addr': ed.ext_addr})


# 设置协调器时钟
def set_coor_clock():
    now = datetime.datetime.now()
    data = [0] * 11
    data[4] = now.hour
    data[5] = now.minute
    data[6] = now.second
    data[7] = now.month
    data[8] = now.day
    data[9:11] = int_to_array(now.year, 2)
    send_data = build_send_data(REQ_SYS, SYS_SET_TIME, len(data), data)
    serial_out_msg_queue.put({
        'type': 'set_clock',
        'data': send_data
    })
    logger.debug('set coor clock %s' % data)


def coor_start_handler():
    set_coor_clock()
    pass


def end_report_status_handler(msg):
    data = msg.data
    idx = 1

    net_addr = data[idx:idx + 2]
    idx += 2
    logger.debug('net addr %s' % net_addr.hex())

    ext_addr = data[idx:idx + 8]
    idx += 8
    logger.debug('ext addr %s' % ext_addr.hex())

    vcc = data[idx:idx + 2]
    logger.debug('vcc %.2fV' % parse_vcc(vcc))
    idx += 2

    pv = data[idx:idx + 1]
    logger.debug('params version %d' % parse_pv(pv))
    idx += 1

    tw = data[idx:idx + 2]
    logger.debug('time window %d' % parse_time_window(tw))
    idx += 2

    parent = data[idx:idx + 2]
    logger.debug('parent  %s' % parent.hex())
    idx += 2

    clock = data[idx:idx + 4]
    logger.debug('clock  %s' % parse_date(clock))
    idx += 4

    temp_freq = data[idx:idx + 4]
    logger.debug('temp freq %s' % parse_freq(temp_freq))
    idx += 4

    hum_freq = data[idx:idx + 4]
    logger.debug('hum freq %s' % parse_freq(hum_freq))
    idx += 4

    packet_freq = data[idx:idx + 4]
    logger.debug('packet freq %s' % parse_freq(packet_freq))
    idx += 4

    sync_clock_freq = data[idx:idx + 4]
    logger.debug('sync clock freq %s' % parse_freq(sync_clock_freq))
    idx += 4
    rssi = data[idx:idx + 1]
    logger.debug('rssi %d db' % parse_rssi(rssi))
    idx += 1

    lqi = data[idx:idx + 1]
    logger.debug('Link LinkQuality %d' % parse_lqi(lqi))

    ed = EndDevice()
    ed.net_addr = net_addr.hex()
    ed.ext_addr = ext_addr.hex()
    ed.voltage = parse_vcc(vcc)
    ed.temp_freq = bytes_to_int_1(temp_freq, 2)
    ed.hum_freq = bytes_to_int_1(hum_freq, 2)
    ed.rssi = parse_rssi(rssi)
    ed.lqi = parse_lqi(lqi)
    ed.pv = parse_pv(pv)
    ed.parent = parent.hex()
    ed.time_window = parse_time_window(tw)
    end_device_id = find_end_device_id(ed.ext_addr)
    if not end_device_id:
        _ed = add_end_device(ed)
        end_device_id = _ed.end_device_id
    update_end_device(ed, {'ext_addr': ed.ext_addr})

def mt_app_handler(msg):
    logger.debug('app handler')
    if len(msg.data):
        if msg.data[0] == TEMP_HUM_DATA:
            logger.debug('temp hum data')
            temp_hum_handler(msg)
            return
        if msg.data[0] == COOR_START:
            logger.warning('coor start')
            coor_start_handler()
            return
        if msg.data[0] == END_REPORT_STATUS_CMD:
            logger.warning('end report status')
            end_report_status_handler(msg)
            return 
        if msg.data[0] == SUCCESS:
            logger.info('cmd success')
            return
        pass
    else:
        logger.warning('app msg data empty')
