#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2017-05-10 20:37:22

from package.dht11 import libDHT11


def test_DHT11(self):
    DHT11.Init_WiringPi()
    humidity, humidityfloat, temperature, temperaturefloat, checksum = libDHT11.read_DHT11()
    assert humidity is not 0
    assert humidityfloat is not 0
    assert temperaturefloat is not 0
    assert temperature is not 0
    assert checksum is not 0
