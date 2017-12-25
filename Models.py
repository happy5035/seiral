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
    start_time = Column(DateTime())
    hum_freq = Column(Integer)
    temp_freq = Column(Integer)
    status = Column(Integer)

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
