#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2016-12-19 20:46:45

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
        self.isStop = False
        self.__CONST_HEATTIME = 90

    @property
    def StartTime(self):
        return self.start_time

    @property
    def TotalTime(self):
        return self.total_time

    @TotalTime.setter
    def TotalTime(self, value):
        if value < 0:
            raise ValueError('Total Time must more than 0!')
        self.total_time = value + self.__CONST_HEATTIME

    def startTimer(self):
        if self.isStop is True:
            self.stop_through += int(time.time() - self.current_time)
            self.current_time = time.time()
            self.isStop = False
            return
        self.current_time = time.time()
        self.start_time = time.time()

    def stopTimer(self):
        self.current_time = time.time()
        self.isStop = True

    def getPercent(self):
        stop = time.time()
        debug("Total time:" + str(self.total_time))
        #  throughTime = int((stop - self.start_time - self.stop_through) * 100 / self.total_time)
        throughTime = (stop - self.start_time - self.stop_through)
        debug("ThroughTime:" + str(throughTime))
        if(throughTime > 100):
            return 100
        if(self.total_time != 0):
            return int((throughTime / self.total_time) * 100)
        else:
            print("set total time first!", file=sys.stderr)
            return 0

    def cleanTimer(self):
        self.__init__()
