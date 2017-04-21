#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2017-04-21 17:39:53

import logging
import os

from time import sleep
from package.thread_pool import ThreadPool
from package.debug import PrintException
from package.da import PrintCore
from package.da import CommandSwitchTableProto
from package.est_time import es_time
from package.timer import PercentTimer
from package.dat import sensors


class Print_time(object):

    def __init__(self):
        self.hour = 0
        self.miniute = 0

    @property
    def getHour(self):
        return self.hour

    @property
    def getMiniute(self):
        return self.miniute

    def getTime(self):
        return self.hour * 60 + self.miniute


class Switcher(CommandSwitchTableProto):

    class SendData(object):
        '''
        class for control send json data and environment data.
        '''

        def __init__(self, printercore):
            # printcore object to get printcore information
            self.printcore = printercore
            # get gcode file name
            self.fileName = ""
            # thread condition
            self.stopped = False
            # print time object,store print time
            self.print_time = Print_time()
            # percent timer object
            self.Timer = PercentTimer()
            # sensors
            self.sensors = sensors()

        def stopRunning(self):
            self.stopped = False

        def isStopped(self):
            return self.stopped

        def set_file_name(self, filename):
            self.fileName = filename

        def Set_Print_Time(self, hour=0, miniute=0):
            self.print_time.hour = hour
            self.print_time.miniute = miniute
            self.Timer.set_total_time((hour * 60 + miniute) * 60)

        def StopTimer(self):
            self.Timer.stop()

        def StartTimer(self):
            self.Timer.start()

        def CleanTimer(self):
            self.Timer.cleanTimer()

        # data for sending in SendJsonToRemote()
        def __createJsonData(self):
            try:

                # get printer status data
                data = self.printcore.printer_status()

                # get filename if startprint is start
                data["PrintPercent"] = 0
                data["File_Name"] = ""
                if self.fileName is not "":
                    # add print time into data
                    data["PrintPercent"] = self.Timer.getPercent()
                    data["File_Name"] = self.fileName
                logging.debug(data)
                return data
            except:
                PrintException()
                return {}

        def json_double_data(self):
            self.stopped = True
            while self.isstopped():
                try:
                    data = self.__createJsonData()
                    sensors_data = self.sensors.get_Sensors_data()
                    if self.printcore.is_printing():
                        sensors_data["IR_temperature"] = 200.0
                    else:
                        sensors_data["IR_temperature"] = self.printcore.headtemp()

                    all_data = {}
                    all_data.update(data)
                    all_data.update(sensors_data)

                    return all_data
                except:
                    PrintException()

    def __init__(self, redis, directory):
        super(Switcher, self).__init__()
        # handlers
        # printcore handler
        self.printcore = None
        # handler for send json file and insert environment data
        self.sendData = None
        # thread pool handler
        self.pool = ThreadPool(6)
        self.redis_handler = redis
        self.directory = directory

    def getTask(self, command):
        try:
            listcommand = command.split(" ", 1)
            print(("command list:", listcommand))
            if listcommand[0].strip() not in self.task:
                self.Default()
                return False

            if len(listcommand) > 1:
                self.task.get(listcommand[0].strip())(listcommand[1].strip())
            else:
                self.task.get(listcommand[0].strip())()
            return True
        except:
            PrintException()
            return False

    def connect(self):
        # TODO:bad connect method
        try:
            self.printcore = PrintCore(Port='/dev/ttyUSB0', Baud=250000)
            self.sendData = self.SendData(self.printcore)
            # TODO:yield json data here
        except:
            logging.error("Connect printer error!")

    def disconnect(self):
        self.printcore.disconnect()
        self.sendData.stopRunning()
        self.pool.wait_completion()

    def reset(self):
        self.printcore.reset()

    def pause(self):
        self.printcore.pause()
        self.sendData.StopTimer()

    def resume(self):
        self.printcore.resume()
        self.sendData.StartTimer()

    def cancel(self):
        self.printcore.cancel()
        self.sendData.CleanTimer()

    def home(self):
        self.printcore.home()

    def send_now(self, command):
        self.printcore.send_now(command.strip("\n"))

    def startprint(self, file_name):

        try:
            gcode = self.redis_handler.redis_handler.get(file_name)
            self.sendData.set_file_name(file_name)
            gcode_path = os.path.join(self.directory, file_name)
            self.sendData.CleanTimer()
            # create file
            with open(gcode_path, 'w') as f:
                f.write(gcode)

            # set print time!
            est_time = es_time(gcode_path)
            (hours, miniutes) = est_time.estime()
            self.sendData.Set_Print_Time(hours, miniutes)
            self.sendData.StartTimer()

            self.pool.add_task(
                self.printcore.startprint(gcode_path)
            )

        except:
            PrintException()

    def Default(self):
        logging.debug("no command")
