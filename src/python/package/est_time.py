#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2016-12-02 18:15:04

import math
import os.path
import io
import time


class es_time():

    def __init__(self, file):

        self.homingspeed = 1500
        self.fiveDaccel = True
        self.caruklip = False
        self.Absolutecoord = True
        self.full_velocity_units = 10.0
        self.min_units_per_second = 35.0
        self.file = file
        # BufferedReader in;
        self.line = ''
        self.splitline = []
        self.oldxcords = 0
        self.oldycords = 0
        self.oldzcords = 0
        self.oldecords = 0
        self.oldfrate = 0
        self.xcords = 0
        self.ycords = 0
        self.zcords = 0
        self.ecords = 0
        self.frate = 0
        self.deltax = 0
        self.deltay = 0
        self.deltaz = 0
        self.deltaf = 0
        self.deltae = 0
        self.deltadist = 0
        self.accel = 0
        self.deltatime = 0
        self.time = 0

    def cord(self, line):

        # print (int(line[1:].find('.'))+3)
        c = float(line[1:(int(line[1:].find('.')) + 3)])  # --------------------------

        return c

    def estime(self):
        try:
            f = open(self.file, 'r')
            # in = new BufferedReader(new FileReader(filelocation));

            for line in f:  # ((line = in.readLine()) != null)
                # print 'abc'
                if(line.startswith("G1")):

                    splitline = line.split(" ")

                    for i in range(0, len(splitline)):

                        if(splitline[i].startswith("X")):

                            self.xcords = self.cord(splitline[i])
                            # print self.xcords
                        if(splitline[i].startswith("Y")):

                            self.ycords = self.cord(splitline[i])

                        if(splitline[i].startswith("Z")):

                            self.zcords = self.cord(splitline[i])

                        if(splitline[i].startswith("E")):

                            self.ecords = self.cord(splitline[i])

                        if(splitline[i].startswith("F")):

                            self.frate = (self.cord(splitline[i])) / 60

                    if self.Absolutecoord is True:

                        self.deltax = self.xcords - self.oldxcords
                        self.deltay = self.ycords - self.oldycords
                        self.deltaz = self.zcords - self.oldzcords
                        self.deltae = self.ecords - self.oldecords

                    else:

                        self.deltax = self.xcords
                        self.deltay = self.ycords
                        self.deltaz = self.zcords
                        self.deltae = self.ecords

                        self.deltadist = math.sqrt((self.deltax * self.deltax) +
                                                   (self.deltay * self.deltay) + (self.deltaz * self.deltaz))

                    if(self.deltadist == 0):
                        # print self.deltae,self.frate
                        self.deltatime = (abs(self.deltae)) / self.frate
                        # print self.deltatime
                    else:
                        if self.fiveDaccel is True:

                            if (self.frate == self.oldfrate):

                                self.deltatime = self.deltadist / self.frate

                            else:

                                self.accel = ((self.frate * self.frate) -
                                              (self.oldfrate * self.oldfrate)) / (2 * self.deltadist)
                                self.deltatime = (self.frate - self.oldfrate) / self.accel

                        else:

                            if (self.caruklip is True):

                                self.accel = ((self.frate * self.frate) - (self.min_units_per_second *
                                                                           self.min_units_per_second)) / (2 * self.full_velocity_units)

                                if (self.frate <= self.min_units_per_second):

                                    self.deltatime = self.deltadist / self.frate

                                else:

                                    if (2 * self.deltadist >= self.full_velocity_units):

                                        acceltime = (self.frate - self.min_units_per_second) / self.accel
                                        acceldistance = (acceltime * self.min_units_per_second) + \
                                            (0.5 * self.accel * acceltime * acceltime)
                                        constveldist = self.deltadist - (2 * acceldistance)
                                        constveltime = constveldist / self.frate
                                        self.deltatime = (2 * acceltime) + constveltime

                                    else:

                                        self.frate = math.sqrt(
                                            (self.min_units_per_second * self.min_units_per_second) + (self.accel * self.deltadist))
                                        self.deltatime = 2 * (self.frate - min_units_per_second) / self.accel

                if(self.line.startswith("G28")):

                    self.xcords = 0
                    self.ycords = 0
                    self.frate = self.homingspeed / 60
                    self.deltax = self.xcords - self.oldxcords
                    self.deltay = self.ycords - self.oldycords
                    self.deltadist = math.sqrt(self.deltax * self.deltax + self.deltay * self.deltay)
                    self.deltatime = self.deltadist / self.frate
                # if self.time==True:

                self.time = self.time + self.deltatime
                self.oldxcords = self.xcords
                self.oldycords = self.ycords
                self.oldzcords = self.zcords
                self.oldecords = self.ecords
                self.oldfrate = self.frate
            x = (round(60 * ((self.time / 3600) - (round(math.floor(self.time / 3600))))))
            y = (round(math.floor(self.time / 3600)))

            print("Estimated print time: {} hours {} minutes".format(x, y))
            # ------------------------------------------------------------------------------------------------------

        except:
            print 'something wrong'

        finally:
            print 'finished'
