#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2016-10-11 19:18:03

from package import DHT11
import time
DHT11.Init_WiringPi()
while True:
    humidity, temp = DHT11.read_DHT11()
    time.sleep(1)
    print humidity, temp
