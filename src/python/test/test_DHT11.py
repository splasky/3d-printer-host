#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2017-05-10 20:58:19

from package.dht11 import libDHT11


def test_DHT11():
    assert libDHT11.Init_WiringPi() == 1
    humidity, humidityfloat, temperature, temperaturefloat, checksum = libDHT11.read_DHT11()
    assert humidity is not 0
    assert temperature is not 0
    assert checksum is not 0
    assert humidity + temperature == checksum
