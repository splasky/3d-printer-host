#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2017-05-05 19:29:00

import logging
import os
import better_exceptions
import time
import threading
import json

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
        self.fileName = ""
        # percent timer object
        self.Timer = PercentTimer()
        # sensors
        self.sensors = sensors()

    def __del__(self):
        self.stopRunning()

    def clean_ALL_Data(self):
        self.fileName = ""
        self.CleanTimer()

    def set_file_name(self, filename):
        self.fileName = filename

    def Set_Print_Time(self, hour=0, miniute=0):
        self.Timer.set_total_time((hour * 60 + miniute) * 60)

    def StopTimer(self):
        self.Timer.stop()

    def StartTimer(self, gcode_path):
        # set print time!
        est_time = es_time(gcode_path)
        (hours, miniutes) = est_time.estime()
        assert hours != 0 or miniutes != 0
        self.Set_Print_Time(hours, miniutes)
        self.Timer.start()

    def CleanTimer(self):
        self.Timer.cleanTimer()

    # data for sending in SendJsonToRemote()
    def createJsonData(self):
        try:

            # get printer status data
            data = self.printcore.printer_status()
            # get filename if startprint is start
            if self.printcore.is_printing():
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
                sensors_data["IR_temperature"] = self.printcore.headtemp()
                all_data = {}
                all_data.update(data)
                all_data.update(sensors_data)
                logging.debug("json_double_data success.")
                all_data = json.dumps(all_data, separators=(',', ':')).encode('utf-8')
                yield all_data
            except:
                PrintException()
                return


class Switcher(CommandSwitchTableProto, SendData):

    def __init__(self, redis, directory, pool):
        self.printcore = PrintCore()
        CommandSwitchTableProto.__init__(self)
        SendData.__init__(self, printcore=self.printcore)

        # handlers
        self.pool = pool
        self.redis_handler = redis
        self.directory = directory
        self.generator = self.json_double_data()
        self.Lock = threading.Lock()
        self.connected = False
        self.printed = False

    def __del__(self):
        self.disconnect()
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

    def Send_Sensors(self):
        try:
            with self.Lock:
                data = next(self.generator, None)
                if data is not None:
                    print("all datas:", data)
                    self.redis_handler.send(data)
                    time.sleep(0.001)
        except:
            PrintException()

    def Thread_add_Send_Sensors(self):
        self.pool.add_task(self.Send_Sensors)

    def connect(self, port='/dev/ttyUSB0', baud=250000):
        # TODO:bad connect method
        if self.connected is not True:
            self.printcore.connect(Port=port, Baud=baud)
            assert isinstance(self.printcore, PrintCore)
            self.pool.add_task(self.Send_Sensors())
            self.connected = True

    def disconnect(self):
        self.printcore.disconnect()
        self.connected = False
        self.pool.wait_completion()

    def reset(self):
        self.printcore.reset()
        self.clean_ALL_Data()

    def pause(self):
        self.printcore.pause()
        self.StopTimer()

    def resume(self):
        self.printcore.resume()
        self.StartTimer()

    def cancel(self):
        self.printcore.cancel()
        self.pool.wait_completion()
        self.clean_ALL_Data()

    def home(self):
        self.printcore.home()

    def send_now(self, command):
        self.printcore.send_now(command.strip("\n"))

    def status_checker(self):
        if printed and not self.printcore.printcoreHandler.pause and
        not self.printcore.is_printing:
            # clean data when finish printing
            self.clean_ALL_Data()
            self.pool.wait_completion()
            self.printed = False

    def startprint(self, file_name):

        try:
            gcode = self.redis_handler.redis_handler.get(file_name)
            self.set_file_name(file_name)
            gcode_path = os.path.join(self.directory, file_name)
            self.CleanTimer()
            # create file
            with open(gcode_path, 'w') as f:
                f.write(gcode)

            self.pool.add_task(self.StartTimer(gcode_path))
            self.pool.add_task(
                self.printcore.startprint(gcode_path)
            )

            self.printed = True

        except:
            PrintException()
            self.clean_ALL_Data()

    def Default(self):
        logging.debug("no command")
