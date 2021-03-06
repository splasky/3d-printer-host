# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2018-05-31 10:39:01

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
from package.dht11 import libDHT11
from package import TMP006
from adxl345 import ADXL345
# import from third party lib
sys.path.append("/usr/lib/python2.7/site-packages/")
from printrun.printcore import printcore
from printrun import gcoder


class CommandSwitchTableProto(object):

    metaclass__ = ABCMeta

    def __init__(self, *args, **kwargs):
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

    def __init__(self, Port=None, Baud=None):
        self.printcoreHandler = printcore()
        self.logl = 0
        self.temp = 0

    def connect(self, Port='/dev/ttyUSB0', Baud=250000):
        try:
            self.printcoreHandler.connect(port=Port, baud=Baud)
            # must wait for printcore connect success
            time.sleep(3)
            setattr(self.printcoreHandler, 'logl', 0)
        except:
            PrintException()

    def disconnect(self):
        try:
            self.printcoreHandler.disconnect()
            return True
        except:
            PrintException()
            return False

    def is_printing(self):
        return self.printcoreHandler.printing

    def reset(self):
        self.printcoreHandler.reset()
        print('py:reset print')
        return True

    def pause(self):
        self.printcoreHandler.pause()
        print('py:pause print')
        return True

    def resume(self):
        self.printcoreHandler.resume()
        print('py:resume print')
        return True

    def cancel(self):
        self.printcoreHandler.cancelprint()
        self.printcoreHandler.send_now("M104 S0")  # cool dowm
        self.printcoreHandler.send_now("G28")  # home
        self.printcoreHandler.send_now("M84")  # stepperoff
        print("py:cancel print")
        return True

    def cooldown(self):
        self.printcoreHandler.send_now("M104 S0")
        print('py:cooldown')
        return True

    def home(self):
        self.printcoreHandler.send_now("G28")
        print('py:home')
        return True

    def send_now(self, command):
        try:
            self.printcoreHandler.send_now(command)
            print("send command success")
            return True
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
            return True
        except:
            self.cancel()
            PrintException()
            return False

    def stepperoff(self):
        self.printcoreHandler.send_now("M84")
        print('py:stepper off')
        return True

    def isPaused(self):
        return self.printcoreHandler.paused

    def printer_status(self):
        """get printer status into json file

        :p: printer object
        :return: return json string

        """
        data = {}
        data["clear"] = self.printcoreHandler.clear
        data["isprinting"] = self.printcoreHandler.printing
        data["online"] = self.printcoreHandler.online
        data["baud"] = self.printcoreHandler.baud
        data["port"] = self.printcoreHandler.port
        try:
            data["IR_temperature"] = self.headtemp()
            data["position"] = self.getPosition()
        except:
            pass
        data["ispause"] = self.isPaused()
        return data

    def gettemp(self):
        self.printcoreHandler.send_now("M105")
        try:
            self.printcoreHandler.logl
            self.temp
        except:
            setattr(self, 'logl', 0)
            setattr(self, 'temp', 0)

        if(self.printcoreHandler.online is False):
            return None
        for n in range(self.printcoreHandler.logl, len(self.printcoreHandler.log)):
            line = self.printcoreHandler.log[n]
            if 'T:' in line:
                te = line.split('T:')[1]
                htemp = float(te.split("/")[0].strip())
                setattr(self, 'temp', htemp)
                self.printcoreHandler.logl = len(self.printcoreHandler.log)
                self.printcoreHandler.send_now("M105")
                return htemp
        return None

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
                if("X:"in line):
                    return line.strip()
        except:
            logging.debug("Printcore:get position error.")
            return ''


def create_json_file(path, data):
    """write a json file to path
    :path: data to be store
    :data: data to be send
    :return: write success return file path else None
    """
    try:
        beSended = json.dumps(data)
        with open(os.path.join(path), 'w') as file:
            file.write(beSended)
    except Exception as e:
        print((e.args))


class sensors(object):

    def __init__(self):
        self.humidity = 0
        self.temperature = 0

    def get_current_time(self):
        return str(datetime.datetime.now())

    def DHT11_temp(self):
        try:
            # have to use libDHT11.Init_WiringPi() first
            checksum = 0
            #  while checksum is not 0:
            humidity, humidityfloat, temperature, temperaturefloat, checksum = libDHT11.read_DHT11()

            while True:
                if checksum is not 0:
                    break
                else:
                    humidity, humidityfloat, temperature, temperaturefloat, checksum = libDHT11.read_DHT11()

            data = {"humidity": humidity, "humidityfloat": humidityfloat,
                    "temperature": temperature, "temperaturefloat": temperaturefloat}

            if(humidity + temperature != checksum):
                data["humidity"] = self.humidity
                data["temperature"] = self.temperature

            self.humidity = data["humidity"]
            self.temperature = data["temperature"]

            return data
        except:
            PrintException()
            return {}

    def get_G_sensor(self):

        try:
            adxl345 = ADXL345()
            axes = adxl345.getAxes(True)

            g_x = (axes['x'])
            g_y = (axes['y'])
            g_z = (axes['z'])

            return g_x, g_y, g_z
        except:
            PrintException()
            return {}

    def IR_temp(self):
        try:
            # IR Temperature:
            sensor = TMP006.TMP006()
            sensor.begin()
            obj_temp = sensor.readObjTempC()
            die_temp = sensor.readDieTempC()
            return obj_temp
        except:
            PrintException()
            return {}

    def get_Sensors_data(self):
        try:
            data = self.DHT11_temp()
            (data["g_x"], data["g_y"], data["g_z"]) = self.get_G_sensor()
            data["time"] = self.get_current_time()

            return data
        except:
            PrintException()
            return {}


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
