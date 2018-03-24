# -*- coding: utf-8 -*-

connect_type_def = ['serial', 'tcp']

# 网关连接属性
connect_type = connect_type_def[0]

serial_port = 'COM3'
serial_rate = 38400

tcp_addr = '192.168.16.100'
tcp_port = 8080

# sql connect
sql_name = 'root'
sql_password = '123456'
sql_addr = 'localhost'
sql_port = '3306'
sql_database = 'datacenter'

sql_url = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' % (sql_name, sql_password, sql_addr, sql_port, sql_database)
