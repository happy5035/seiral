# -*- coding: utf-8 -*-

from Models import *
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine
from utils import *
import datetime
from my_logger import logger
from sqlalchemy import desc
import config

engine = create_engine(config.sql_url)
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


def update_router_device(router_device: RouterDevice, params):
    sess = DBSession()
    try:
        query = sess.query(RouterDevice)
        _filter = query.filter_by(ext_addr=router_device.ext_addr)
        if 'router_device_id' in params:
            _filter = _filter.filter(RouterDevice.router_device_id == params['router_id'])
        if 'ext_addr' in params:
            _filter = _filter.filter(RouterDevice.ext_addr == params['ext_addr'])
        if 'net_addr' in params:
            _filter = _filter.filter(RouterDevice.net_addr == params['net_addr'])
        if 'name' in params:
            _filter = _filter.filter(RouterDevice.name == params['name'])
        if 'status' in params:
            _filter = _filter.filter(RouterDevice.status == params['status'])
        rst = _filter.all()
        for device in rst:
            if router_device.ext_addr:
                device.ext_addr = router_device.ext_addr
            if router_device.net_addr:
                device.net_addr = router_device.net_addr
            if router_device.status:
                device.status = router_device.status
            if router_device.name:
                device.name = router_device.name
            if router_device.voltage:
                device.voltage = router_device.voltage
            if router_device.start_time:
                device.start_time = router_device.start_time
            if router_device.update_time:
                device.update_time = router_device.update_time
            if router_device.rssi:
                device.rssi = router_device.rssi
            if router_device.lqi:
                device.lqi = router_device.lqi
            if router_device.parent:
                device.parent = router_device.parent
        sess.commit()
    except Exception as e:
        logger.error(e)
        sess.rollback()
        logger.warning('update router_device failed %s' % router_device)
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


def find_router_device_id(ext_addr):
    sess = DBSession()
    rst = sess.query(RouterDevice).filter(RouterDevice.ext_addr == ext_addr).first()
    if rst:
        rid = rst.router_device_id
    else:
        rid = None

    sess.commit()
    sess.close()
    return rid


def add_end_device(ed: EndDevice) -> EndDevice:
    session = DBSession()
    try:

        ed.end_device_id = my_uuid()
        max_code = session.query(EndDevice).filter(EndDevice.code < 100).order_by(desc(EndDevice.code)).first().code
        ed.code = max_code + 1
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


def add_router_device(rd: RouterDevice) -> RouterDevice:
    session = DBSession()
    try:

        rd.router_device_id = my_uuid()
        rd_tmp = session.query(RouterDevice).order_by(
            desc(RouterDevice.code)).first()
        max_code = 0
        if rd_tmp is None or rd.code is None:
            max_code = 0
        else:
            max_code = rd.code
        rd.axis_id = 3
        rd.code = max_code + 1
        rd.start_time = datetime.datetime.now()
        rd.status = 0
        rd.name = 'test'
        rd.voltage = 0

        session.add(rd)
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(e)
        logger.error('add end device fialed %s', rd)
        session.close()
    return rd


def add_room_axis(axis: RoomAxis):
    session = DBSession()
    try:
        session.add(axis)
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(e)
        logger.error('add end device fialed %s', axis)
        session.close()
    return axis
    pass


def update_net_param(net_param: NetParams):
    sess = DBSession()
    try:
        query = sess.query(NetParams)
        rst = query.filter_by(net_param_id=1).first()
        rst.remote_uart_addr = 1234
        logger.info(rst)
        sess.commit()
    except Exception as e:
        logger.error(e)
        sess.rollback()
        logger.warning('update router_device failed %s' % net_param)
    sess.close()
    pass


def get_net_params(sess) -> NetParams:
    rst = sess.query(NetParams).filter(NetParams.net_param_id == 1).first()
    return rst

def start_session():
    return DBSession()

def commit_session(sess):
    try:
        sess.commit()
    except Exception as e:
        logger.error(e)
        sess.rollback()
        logger.warning('commit failed')
    sess.close()


if __name__ == '__main__':
    sess = start_session()
    nt = get_net_params(sess)
    nt.remote_uart_addr = 222
    commit_session(sess)
    # eid = find_end_device_id('5c588b17004b1200')
    # session = DBSession()
    # rst = session.query(Room).first()
    # print(rst)
    # x = 7
    # y = 13
    # x_delt = 50
    # y_delt = 30
    # for xi in range(x):
    #     for yi in range(y):
    #         axis = RoomAxis()
    #         axis.room_id = 1
    #         axis.x_num = xi
    #         axis.x_value = xi * x_delt
    #         axis.y_num = yi
    #         axis.y_value = yi * y_delt
    #         axis.z_num = 0
    #         axis.z_value = 0
    #         add_room_axis(axis)
    #         print(xi, yi)
    #         pass

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
