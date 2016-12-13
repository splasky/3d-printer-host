#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2016-12-13 15:29:03

from __future__ import print_function
import time
import sys


class PercentTimer(object):

    def __init__(self):
        self.starttime = int(0)
        self.throughtime = int(0)
        self.totaltime = 0

    def setTotalTime(self, time):
        self.totaltime = time

    def getTotalTime(self):
        return self.totaltime

    def startTimer(self):
        self.starttime = time.time()

    def stopTimer(self):
        self.throughtime = self.starttime - time.time()

    def getPercent(self):
        if(self.totaltime != 0):
            return int((time.time() - self.starttime + self.throughtime) / self.totaltime)
        print("set total time first!", file=sys.stderr)
        return 0

    def cleanTimer(self):
        self.starttime = int(0)
        self.throughtime = int(0)
        self.totaltime = 0
