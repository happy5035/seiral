# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger()
logging.basicConfig(filename='log/log.log',
                    format='[%(asctime)s %(name)s %(levelname)s line:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s %(name)s-%(levelname)s-%(module)s-line:%(lineno)d] %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
