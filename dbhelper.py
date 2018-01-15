# -*- coding: utf-8 -*-

from Models import *
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine
from utils import *
import datetime
from my_logger import logger

engine = create_engine("mysql+pymysql://root:123456@localhost:3306/datacenter?charset=utf8")
DBSession = sessionmaker(bind=engine)


def update_end_device(end_device: EndDevice, params):
    sess = DBSession()
    try:
        query = sess.query(EndDevice)
        _filter = query.filter_by(ext_addr=end_device.ext_addr)
        if 'end_device_id' in params:
            _filter = _filter.filter(EndDevice.end_device_id == params['end_device_id'])
        if 'ext_addr' in params:
            _filter = _filter.filter(EndDevice.ext_addr == params['ext_addr'])
        if 'net_addr' in params:
            _filter = _filter.filter(EndDevice.net_addr == params['net_addr'])
        if 'name' in params:
            _filter = _filter.filter(EndDevice.name == params['name'])
        if 'status' in params:
            _filter = _filter.filter(EndDevice.status == params['status'])
        if 'hum_freq' in params:
            _filter = _filter.filter(EndDevice.hum_freq == params['hum_freq'])
        if 'temp_freq' in params:
            _filter = _filter.filter(EndDevice.temp_freq == params['temp_freq'])
        rst = _filter.all()
        for device in rst:
            if end_device.ext_addr:
                device.ext_addr = end_device.ext_addr
            if end_device.net_addr:
                device.net_addr = end_device.net_addr
            if end_device.status:
                device.status = end_device.status
            if end_device.name:
                device.name = end_device.name
            if end_device.voltage:
                device.voltage = end_device.voltage
            if end_device.start_time:
                device.start_time = end_device.start_time
            if end_device.hum_freq:
                device.hum_freq = end_device.hum_freq
            if end_device.temp_freq:
                device.temp_freq = end_device.temp_freq
            if end_device.hum:
                device.hum = end_device.hum
            if end_device.temp:
                device.temp = end_device.temp
            if end_device.update_time:
                device.update_time = end_device.update_time
            if end_device.rssi:
                device.rssi = end_device.rssi
            if end_device.lqi:
                device.lqi = end_device.lqi
            if end_device.pv:
                device.pv = end_device.pv
            if end_device.time_window:
                device.time_window = end_device.time_window
            if end_device.parent:
                device.parent = end_device.parent
            if end_device.type:
                device.type = end_device.type
        sess.commit()
    except Exception as e:
        logger.error(e)
        sess.rollback()
        logger.warning('update end_device failed %s' % end_device)
    sess.close()
    pass


def add_temperature_all(temps):
    session = DBSession()
    result = True
    try:
        session.add_all(temps)
        session.commit()
    except:
        session.rollback()
        result = False
    session.close()
    return result
    pass


def add_humidity_all(temps):
    session = DBSession()
    result = True
    try:
        session.add_all(temps)
        session.commit()
    except:
        session.rollback()
        result = False
    session.close()
    return result
    pass


def find_end_device_id(ext_addr):
    sess = DBSession()
    rst = sess.query(EndDevice).filter(EndDevice.ext_addr == ext_addr).first()
    if rst:
        eid = rst.end_device_id
    else:
        eid = None

    sess.commit()
    sess.close()
    return eid


def add_end_device(ed: EndDevice) -> EndDevice:
    session = DBSession()
    try:

        ed.end_device_id = my_uuid()
        ed.start_time = datetime.datetime.now()
        ed.status = 0
        # ed.voltage = 0
        # ed.hum_freq = 0
        # ed.temp_freq = 0
        # ed.name = 'test'
        # ed.net_addr = '0000'
        session.add(ed)
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(e)
        logger.error('add end device fialed %s', ed)
        session.close()
    return ed


if __name__ == '__main__':
    eid = find_end_device_id('5c588b17004b1200')
    session = DBSession()
    rst = session.query(Room).first()
    print(rst)

    # add_end_device(EndDevice(ext_addr='1233333'))
    # import uuid
    # import datetime
    #
    # # session = DBSession()
    # end_device = EndDevice()
    # end_device.ext_addr = '2d48eb0e004b1200'
    # end_device.status = 2
    # update_end_device(end_device, {'ext_addr': '2d48eb0e004b1200'})
    # humiditys = []
    # humiditys.append(
    #     Humidity(humi_id=str(uuid.uuid4()), end_device_id='86a511a0-f8fd-43fa-b411-8592aa469b72', humi_value=20.3,
    #              humi_time=datetime.datetime.now()))
    #
    # humiditys.append(
    #     Humidity(humi_id=str(uuid.uuid4()), end_device_id='86a511a0-f8fd-43fa-b411-8592aa469b72', humi_value=20.3,
    #              humi_time=datetime.datetime.now()))
    #
    # humiditys.append(
    #     Humidity(humi_id=str(uuid.uuid4()), end_device_id='86a511a0-f8fd-43fa-b411-8592aa469b72', humi_value=20.3,
    #              humi_time=datetime.datetime.now()))
    #
    # add_humidity_all(humiditys)
    # session.add(humidity)
    # temperature = Temperature()
    # temperature.temp_id = uuid.uuid4()
    # temperature.temp_value = 20.3
    # temperature.temp_time = datetime.datetime.now()
    # temperature.end_device_id = '8a4cb3d9-4079-454e-8b40-b83679946e5f'
    # print(temperature)
    # session.add(temperature)

    # end_device = EndDevice()
    # end_device.end_device_id = '8a4cb3d9-4079-454e-8b40-b83679946e5f'
    # end_device.ext_addr = u'2d48eb0e004b1200'
    # end_device.net_addr = u'0aa7'
    # end_device.start_time = datetime.datetime.now()
    # end_device.voltage = 3.00
    # end_device.name = u'测试'
    # end_device.hum_freq = 10000
    # end_device.temp_freq = 1000
    # end_device.status = 0
    # rst = session.query(EndDevice).filter(EndDevice.end_device_id == '8a4cb3d9-4079-454e-8b40-b83679946e5f').first()
    # humidity = Humidity()
    # humidity.humi_id = uuid.uuid4()
    # humidity.humi_value = 20.3
    # humidity.humi_time = datetime.datetime.now()
    # humidity.end_device = rst
    # humidity.end_device_id = rst.end_device_id
    # session.add(humidity)
    # session.refresh(rst)
    # session.query(EndDevice).all()
    # session.commit()
    # session.close()

    pass
