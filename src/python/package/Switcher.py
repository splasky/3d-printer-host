#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2017-04-25 20:20:12

import logging
import os
import better_exceptions
import time
import threading

from package.thread_pool import ThreadPool
from package.debug import PrintException
from package.da import PrintCore
from package.da import CommandSwitchTableProto
from package.est_time import es_time
from package.timer import PercentTimer
from package.da import sensors


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


class SendData(object):
    '''
    class for control send json data and environment data.
    '''

    def __init__(self, printcore):
        # printcore object to get printcore information
        self.printcore = printcore
        # get gcode file name
        self.fileName = ""
        # print time object,store print time
        self.print_time = Print_time()
        # percent timer object
        self.Timer = PercentTimer()
        # sensors
        self.sensors = sensors()

    def __del__(self):
        self.stopRunning()

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
    def createJsonData(self):
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
            logging.debug("Create Json data success.")
            return data
        except:
            PrintException()
            return {}

    def json_double_data(self):
        while True:
            try:
                data = self.createJsonData()
                sensors_data = self.sensors.get_Sensors_data()
                if self.printcore.is_printing():
                    sensors_data["IR_temperature"] = 200.0
                else:
                    sensors_data["IR_temperature"] = self.printcore.headtemp()
                all_data = {}
                all_data.update(data)
                all_data.update(sensors_data)
                logging.debug("json_double_data success.")
                yield all_data
            except:
                PrintException()
                return


class Switcher(CommandSwitchTableProto, SendData):

    def __init__(self, redis, directory, pool):
        self.printcore = None
        CommandSwitchTableProto.__init__(self)
        SendData.__init__(self, printcore=self.printcore)

        # handlers
        self.pool = pool
        self.redis_handler = redis
        self.directory = directory
        self.generator = self.json_double_data()
        self.Lock = threading.Lock()

    def __del__(self):
        del self.printcore

    def getTask(self, command):
        try:
            listcommand = command.split(" ", 1)
            print(("command list:", listcommand))
            command = listcommand[0].strip()
            if command not in self.task:
                self.Default()
                return False

            if len(listcommand) > 1:
                self.task.get(command)(listcommand[1].strip())
            else:
                self.task.get(command)()
            return True
        except:
            PrintException()
            return False

    def Thread_Send_Sensors(self):
        try:
            with self.Lock:
                data = self.generator.next()
                self.redis_handler.send(data)
                time.sleep(0.001)
            self.pool.add_task(self.Thread_Send_Sensors())
        except:
            PrintException()

    def connect(self):
        # TODO:bad connect method
        self.printcore = PrintCore(Port='/dev/ttyUSB0', Baud=250000)
        assert isinstance(self.printcore, PrintCore)
        self.pool.add_task(self.Thread_Send_Sensors())

    def disconnect(self):
        self.printcore.disconnect()
        self.pool.wait_completion()

    def reset(self):
        self.printcore.reset()

    def pause(self):
        self.printcore.pause()
        self.StopTimer()

    def resume(self):
        self.printcore.resume()
        self.StartTimer()

    def cancel(self):
        self.printcore.cancel()
        self.CleanTimer()

    def home(self):
        self.printcore.home()

    def send_now(self, command):
        self.printcore.send_now(command.strip("\n"))

    def startprint(self, file_name):

        try:
            gcode = self.redis_handler.redis_handler.get(file_name)
            self.set_file_name(file_name)
            gcode_path = os.path.join(self.directory, file_name)
            self.CleanTimer()
            # create file
            with open(gcode_path, 'w') as f:
                f.write(gcode)

            # set print time!
            est_time = es_time(gcode_path)
            (hours, miniutes) = est_time.estime()
            self.Set_Print_Time(hours, miniutes)
            self.StartTimer()

            self.pool.add_task(
                self.printcore.startprint(gcode_path)
            )

        except:
            PrintException()

    def Default(self):
        logging.debug("no command")
