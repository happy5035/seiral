# -*- coding: utf-8 -*-
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class EndDevice(Base):
    __tablename__ = 'end_device'
    end_device_id = Column(String(255), primary_key=True)
    ext_addr = Column(String(16))
    net_addr = Column(String(4))
    name = Column(String(255))
    voltage = Column(Float)
    temp = Column(Float)
    hum = Column(Float)
    start_time = Column(DateTime)
    hum_freq = Column(Integer)
    temp_freq = Column(Integer)
    status = Column(Integer)
    update_time = Column(DateTime)
    rssi = Column(Integer)
    lqi = Column(Integer)
    pv = Column(Integer)
    parent = Column(String(4))
    time_window = Column(Integer)

    def __repr__(self):
        return "<EndDevice (id='%s',ext_addr='%s',ext_addr='%s',net_addr='%s',name='%s',voltage='%s'," \
               "hum_freq='%s',temp_freq='%s',status='%s')> " \
               % (self.end_device_id, self.ext_addr, self.net_addr, self.name, self.voltage, self.status, self.hum_freq,
                  self.temp_freq, self.status)


class Humidity(Base):
    __tablename__ = 'humidity'
    humi_id = Column(String(255), primary_key=True)
    end_device_id = Column(String(255), ForeignKey('end_device.end_device_id'))
    humi_value = Column(Float)
    humi_time = Column(DateTime)

    def __repr__(self):
        return "<Humidity (id = '%s', end_device_id = '%s',humi_value = '%s',humi_time= '%s')>" \
               % (self.humi_id, self.end_device_id, self.humi_value, self.humi_time)


class Temperature(Base):
    __tablename__ = 'temperature'
    temp_id = Column(String(255), primary_key=True)
    end_device_id = Column(String(255), ForeignKey('end_device.end_device_id'))
    temp_value = Column(Float)
    temp_time = Column(DateTime)

    def __repr__(self):
        return "<Temperature (id = '%s', end_device_id = '%s',temp_value = '%s',temp_time= '%s')>" \
               % (self.temp_id, self.end_device_id, self.temp_value, self.temp_time)


class EndDeviceInfo(Base):
    __tablename__ = 'end_device_info'
    end_device_info_id = Column(Integer, primary_key=True)
    end_device_id = Column(String(255), ForeignKey('end_device.end_device_id'))
    room_id = Column(Integer, ForeignKey('room.room_id'))
    x_pos_name = Column(Float)
    x_pos_value = Column(Integer)
    y_pos_name = Column(Float)
    y_pos_value = Column(Integer)
    z_temp_name = Column(Float)
    z_temp_value = Column(Integer)
    status = Column(Integer)

    def __repr__(self):
        return "<EndDeviceInfo " \
               "(id = '%s', end_device_id = '%s', room_id = '%s'," \
               "x_pos_name = '%s',x_pos_value= '%s'," \
               "y_pos_name = '%s',y_pos_value= '%s'," \
               "z_temp_name = '%s',z_temp_value= '%s')>," \
               "status = '%s'" \
               % (self.end_device_info_id, self.end_device_id, self.room_id,
                  self.x_pos_name, self.x_pos_value,
                  self.y_pos_name, self.y_pos_value,
                  self.z_temp_name, self.z_temp_value,
                  self.status)


class Room(Base):
    __tablename__ = 'room'
    room_id = Column(Integer, primary_key=True)
    room_name = Column(String(255))
    room_x = Column(Float)
    room_y = Column(Float)
    room_z = Column(Float)
    room_x_nums = Column(Integer)
    room_y_nums = Column(Integer)
    room_size = Column(Float)
    room_pos = Column(String(255))

    def __repr__(self):
        return "<Room (id = '%s', room_name = '%s',room_x = '%s',room_y= '%s'," \
               "room_x_nums= '%s',room_y_nums= '%s',room_z= '%s,room_size= '%s',room_pos= '%s')>" \
               % (self.room_id, self.room_name, self.room_x, self.room_y,  self.room_x_nums, self.room_y_nums, self.room_z, self.room_size, self.room_pos)


class RoomAxis(Base):
    __tablename__ = 'room_axis'
    room_axis_id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey('room.room_id'))
    room_axis_name = Column(String(255))
    room_axis_type = Column(Integer)

    def __repr__(self):
        return "<RoomAxis (id = '%s', room_id = '%s',room_axis_name = '%s',room_axis_type= '%s')>" \
               % (self.room_axis_id, self.room_id, self.room_axis_name, self.room_axis_type)
