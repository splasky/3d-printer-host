#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2016-11-16 19:35:27

from package.da import PrintCore
from package.debug import PrintException

try:
    p = PrintCore()
    p.startprint('/home/pi/test.gcode')

    p.send_now("M31")
    print(p.printcoreHandler.log)
except:
    PrintException()
