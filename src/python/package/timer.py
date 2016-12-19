#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2016-12-19 16:29:54

from __future__ import print_function
import time
import sys
from logging import debug


class PercentTimer(object):

    def __init__(self):
        self.start_time = 0  # start print time
        self.stop_through = 0
        self.current_time = 0  # all time that stop print
        self.total_time = 0

    @property
    def StartTime(self):
        value = int(self.start_time)
        return value

    @property
    def TotalTime(self):
        value = int(self.total_time)
        return value

    @TotalTime.setter
    def TotalTime(self, value):
        if not isinstance(value, int):
            raise ValueError('score must be an integer!')
        if value < 0:
            raise ValueError('score must more than 0!')
        self.total_time = value

    def startTimer(self):
        if self.current_time != 0:
            self.stop_through += time.time() - self.current_time
            self.current_time = time.time()
            return
        self.start_time = time.time()
        self.current_time = time.time()

    def stopTimer(self):
        self.current_time = time.time()

    def getPercent(self):
        self.stopTimer()
        stop = time.time()
        debug("Total time:" + str(self.TotalTime))
        throughTime = int(stop - self.start_time - self.stop_through) * 100 / self.total_time
        debug("throughTime:" + str(throughTime))
        self.startTimer()
        if(throughTime > 100):
            return 100
        if(self.total_time != 0):
            return throughTime
        print("set total time first!", file=sys.stderr)
        return 0

    def cleanTimer(self):
        self.__init__()
