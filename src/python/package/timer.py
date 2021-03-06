#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2017-05-10 21:48:50


import time
import sys
from logging import debug
from .debug import PrintException


class Timer(object):

    def __init__(self, func=time.time):
        self.elapsed = 0.0
        self._func = func
        self._start = 0
        self.isStopped = False

    def __add__(self, other):
        return int.__add__(self.elapsed + other.elapsed)

    def start(self):
        if self._start is not 0:
            raise RuntimeError('Timer already started')
        self._start = self._func()

    def resume(self):
        self._start = self._func()
        self.isStopped = False

    def stop(self):
        end = self._func()
        self.elapsed += round(end - self._start)
        self._start = 0
        self.isStopped = True

    def get_elapsed(self):
        if(self.isStopped):
            return self.elapsed
        end = self._func()
        self.elapsed += round(end - self._start)
        self._start = 0
        time = self.elapsed
        self.start()
        return time

    def reset(self):
        self._start = 0
        self.elapsed = 0.0

    @property
    def isrunning(self):
        return self._start is not 0

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()


class PercentTimer(Timer):

    def __init__(self, value=0):
        super(PercentTimer, self).__init__()
        if value < 0:
            raise ValueError('Total Time must more than 0!')

        self.__CONST_HEATTIME = 60
        self.total_time = round(value + self.__CONST_HEATTIME)

    def set_total_time(self, value):
        if value <= 0:
            raise ValueError('Total Time must more than 0!')
        self.total_time = round(value + self.__CONST_HEATTIME)

    # get timer elapsed percent
    def getPercent(self):
        assert self.set_total_time is not 0
        elapsed = self.get_elapsed()
        debug("Total time:" + str(self.total_time))
        debug("Through time:" + str(elapsed))
        try:
            percent = round((elapsed / self.total_time) * 100)
            if(percent < 100):
                return percent
            return 100
        except:
            PrintException()
            return 0

    def cleanTimer(self):
        self.reset()
