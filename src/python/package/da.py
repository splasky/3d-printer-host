# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2017-04-13 18:07:22

import sys
import time
import json
import os
from . import send
import math
import subprocess
import re
import datetime
import logging

from abc import ABCMeta, abstractmethod
from package.debug import PrintException


# Third party
import MySQLdb
import DHT11
from package import TMP006
from adxl345 import ADXL345
# import from 3trd party lib
sys.path.append("/usr/lib/python2.7/site-packages/")
from printrun.printcore import printcore
from printrun import gcoder


class CommandSwitchTableProto(object):

    metaclass__ = ABCMeta

    def __init__(self):
        self.task = {
            "connect": self.connect,
            "disconnect": self.disconnect,
            "reset": self.reset,
            "pause": self.pause,
            "resume": self.resume,
            "cancel": self.cancel,
            "cooldown": self.cooldown,
            "home": self.home,
            "startprint": self.startprint,
            "stepperoff": self.stepperoff,
            "send_now": self.send_now,
            "printer_status": self.printer_status,
            "headtemp": self.headtemp,
            "Default": self.Default
        }

    @abstractmethod
    def getTask(self, command):
        pass

    def getcommands(self):
        return self.task.keys

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def resume(self):
        pass

    @abstractmethod
    def cancel(self):
        pass

    @abstractmethod
    def cooldown(self):
        pass

    @abstractmethod
    def home(self):
        pass

    @abstractmethod
    def startprint(self):
        pass

    @abstractmethod
    def stepperoff(self):
        pass

    @abstractmethod
    def send_now(self):
        pass

    @abstractmethod
    def printer_status(self):
        pass

    @abstractmethod
    def headtemp(self):
        pass

    def Default(self):
        print("No command")


class PrintCore(object):
    Port = '/dev/ttyUSB0'
    Baud = 250000

    def __init__(self, port='/dev/ttyUSB0', baud=250000):
        self.printcoreHandler = printcore(port=port, baud=baud)
        try:
            self.printcoreHandler.logl
        except:
            setattr(self.printcoreHandler, 'logl', 0)

    def disconnect(self):
        self.printcoreHandler.disconnect()
        print("py:disconnect...")

    def is_printing(self):
        return self.printcoreHandler.printing

    def reset(self):
        self.printcoreHandler.reset()
        print('py:reset print')

    def pause(self):
        self.printcoreHandler.pause()
        print('py:pause print')

    def resume(self):
        self.printcoreHandler.resume()
        print('py:resume print')

    def cancel(self):
        self.printcoreHandler.cancelprint()
        self.printcoreHandler.send_now("M104 S0")  # cool dowm
        self.printcoreHandler.send_now("G28")  # home
        self.printcoreHandler.send_now("M84")  # stepperoff
        print("py:cancel print")
        time.sleep(3)

    def cooldown(self):
        self.printcoreHandler.send_now("M104 S0")
        print('py:cooldown')

    def home(self):
        self.printcoreHandler.send_now("G28")
        print('py:home')

    def send_now(self, command):
        try:
            self.printcoreHandler.send_now(command)
            print("send command success")
        except:
            print("py:send command failed")
            return False

    def startprint(self, file):
        try:
            print('start print...')
            gcode = [i.strip() for i in open(file)]
            gcode = gcoder.LightGCode(gcode)
            self.printcoreHandler.startprint(gcode)
            print("py:print")
        except:
            self.printcoreHandler.cancelprint()
            self.printcoreHandler.send_now("M104 S0")  # cool dowm
            self.printcoreHandler.send_now("G28")  # home
            self.printcoreHandler.send_now("M84")  # stepperoff
            PrintException()
            return False

    def stepperoff(self):
        self.printcoreHandler.send_now("M84")
        print('py:stepper off')

    def printer_status(self):
        """get printer status into json file

        :p: printer object
        :return: return json string

        """
        data = dict()
        data["clear"] = self.printcoreHandler.clear
        data["isprinting"] = self.printcoreHandler.printing
        data["online"] = self.printcoreHandler.online
        data["baud"] = self.printcoreHandler.baud
        data["port"] = self.printcoreHandler.port
        data["position"] = self.getPosition()
        return data

    def gettemp(self):
        self.printcoreHandler.send_now("M105")
        try:
            self.printcoreHandler.logl
            self.temp
        except:
            setattr(self, 'logl', 0)
            setattr(self, 'temp', 0)

        htemp = None

        while htemp is None:
            if(self.printcoreHandler.online is False):
                break
            for n in range(self.printcoreHandler.logl, len(self.printcoreHandler.log)):
                line = self.printcoreHandler.log[n]
                if 'T:' in line:
                    te = line.split('T:')[1]
                    htemp = float(te.split("/")[0].strip())
                    setattr(self, 'temp', htemp)
                    self.printcoreHandler.logl = len(self.printcoreHandler.log)
                    break
            self.printcoreHandler.send_now("M105")
            time.sleep(1)
            #  logging.debug("deque:{0}".format(str(self.printcoreHandler.log)))

        return htemp

    def headtemp(self):
        try:
            return self.gettemp()
        except:
            logging.error("py:get headtemp error occure")
            PrintException()
            return 0

    def getPosition(self):
        try:
            self.printcoreHandler.send_now("M114")
            time.sleep(1)
            for n in range(self.printcoreHandler.logl, len(self.printcoreHandler.log)):
                line = self.printcoreHandler.log[n]
                if("X:"in line):  # may be mistake
                    logging.debug("Position:{0}".format(line))
                    self.printcoreHandler.logl = len(self.printcoreHandler.log)
                    return line.strip()
        except:
            PrintException()
            logging.debug("in GetPosition {0}".format(line))
            return ''


def create_json_file(data):
    """write a json file to path
    :data: data to be send
    :return: write success return file path else None
    """
    try:
        beSended = json.dumps(data)
        fp = '/tmp/printer.json'
        with open(os.path.abspath(fp), 'w') as file:
            file.write(beSended)
            return fp
    except Exception as e:
        print((e.args))
        return None


def DHT11_temp():
    # have to use DHT11.Init_WiringPi() first
    checksum = 0
    while(checksum is 0):
        humidity, humidityfloat, temperature, temperaturefloat, checksum = DHT11.read_DHT11()

    logging.debug("checksum :{0}".format(checksum))
    if checksum == 0:
        return None
    else:
        dict = {"humidity": humidity, "humidityfloat": humidityfloat,
                "temperature": temperature, "temperaturefloat": temperaturefloat}
        return dict


def get_G_sensor():

    try:

        adxl345 = ADXL345()
        axes = adxl345.getAxes(True)

        g_x = (axes['x'])
        g_y = (axes['y'])
        g_z = (axes['z'])

        return g_x, g_y, g_z
    except:
        PrintException()
        return None


def IR_temp():
    try:
        # IR Temperature:
        sensor = TMP006.TMP006()
        sensor.begin()
        obj_temp = sensor.readObjTempC()
        die_temp = sensor.readDieTempC()
        return obj_temp
    except:
        PrintException()
        return None


def get_Sensors_data(data={}):
    try:
        dict = DHT11_temp()
        if dict is not None:
            data["humidity"] = dict["humidity"]
            data["temp"] = dict["temperature"]
        else:
            return None
        (data["g_x"], data["g_y"], data["g_z"]) = get_G_sensor()
        logging.debug("Temperature: {0} C".format(data["temp"]))
        logging.debug("Humidity:    {0}%%".format(data["humidity"]))
        logging.debug("G sensors: {0},{1},{2}".format(
            data["g_x"], data["g_y"], data["g_z"]))
        return data
    except:
        PrintException()
        return None


class SqlManager(object):

    def __init__(self, host, user, password, database, port):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.db_hander = MySQLdb.connect(host, user, password, database, port)
        self.cursor = self.db_hander.cursor()

    def __del__(self):
        self.cursor.close()
        self.db_hander.close()
        logging.debug("close SqlManager success")

    def SQLOperate(self, sqlcommand):
        try:
            # Execute the SQL command
            self.cursor.execute(sqlcommand)
            self.db_hander.commit()
        except:
            PrintException()

    def Send_Sensors(self, data={}):
        try:
            # Prepare SQL query to INSERT a record into the database.
            sql = "Insert into env_data(humidity,temperature,x_axis,y_axis,z_axis,IR_temperature) values({},{},{},{},{},{})".format(
                data["humidity"],
                data["temp"],
                data["g_x"],
                data["g_y"],
                data["g_z"],
                float(data["IR_temperature"])
            )

            self.SQLOperate(sql)
            logging.debug('Insert sensors_data success')
        except:
            # Rollback in case there is any error
            self.db_hander.rollback()
            logging.error("Insert error,database rollback.")
            logging.debug(sql)
            PrintException()

    def Insert_logs(self, event):
        try:
            sql = "insert into logs(event) values('{}');".format(event)
            self.SQLOperate(sql)
            logging.debug("Insert log success")
        except:
            self.db_hander.rollback()
            logging.error("Insert log error")
            PrintException()
