#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2017-02-06 11:23:35


import time
import sys
from logging import debug
from .debug import PrintException


class Timer(object):

    def __init__(self, func=time.time):
        self.elapsed = 0.0
        self._func = func
        self._start = None

    def __add__(self, other):
        return int.__add__(self.elapsed + other.elapsed)

    def start(self):
        if self._start is not None:
            raise RuntimeError('Already started')
        self._start = self._func()

    def stop(self):
        if self._start is None:
            raise RuntimeError('Not started')
        end = self._func()
        self.elapsed += round(end - self._start)
        self._start = None

    def get_elapsed(self):
        self.stop()
        time = self.elapsed
        self.start()
        return time

    def reset(self):
        self.elapsed = 0.0

    @propetrty
    def isrunning(self):
        return self._start is not None

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

        self.__CONST_HEATTIME = 120
        self.total_time = round(value + self.__CONST_HEATTIME)

    def set_total_time(self, value):
        if value <= 0:
            raise ValueError('Total Time must more than 0!')
        self.total_time = round(value + self.__CONST_HEATTIME)

    # get timer elapsed percent
    def getPercent(self):
        if self.total_time <= 0:
            raise ValueError('Total Time must more than 0!')
        elapsed = self.get_elapsed()
        debug("Total time:" + str(self.total_time))
        debug("Through time:" + str(elapsed))
        try:
            if(self.total_time > 0):
                percent = round((elapsed / self.total_time) * 100)
                if(percent < 100):
                    return percent
                else:
                    return 100
            else:
                raise ValueError('set total time first!')
                return 0
        except:
            PrintException()

    def cleanTimer(self):
        self.reset()
