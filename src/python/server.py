# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2017-02-14 19:10:33

import socket
import sys
import logging
import os
import subprocess
import shlex
import multiprocessing
import threading

from package.thread_pool import ThreadPool
from threading import Thread
from time import sleep
from package.send import upload_server
from package.s_printer_status import S_printer_status
from package.debug import PrintException
from package.sock_proto import TCP_Server
from package.da import PrintCore
from package.da import CommandSwitchTableProto
from package import da
from package import DHT11
from package.est_time import es_time
from package.timer import PercentTimer


# path to put gcode
filepath = "/home/pi/temp/"


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
            self.lock = True
            # print time object,store print time
            self.print_time = Print_time()
            # percent timer object
            self.Timer = PercentTimer()

        def stopRunning(self):
            self.lock = False

        def isstopped(self):
            return self.lock

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

        def __st_Sensors(self):
            sensors_data = da.get_Sensors_data()
            if sensors_data is not None:
                if self.printcore.is_printing():
                    sensors_data["IR_temperature"] = 200.0
                else:
                    sensors_data["IR_temperature"] = self.printcore.headtemp()

                da.Send_Sensors(data=sensors_data)

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
                return None

        def SendJsonToRemote(self):
            data = self.__createJsonData()
            if data is not None:
                S_printer_status(data)

        # thread put into threadpool
        # insert for sensors data
        def Thread_InsertSensors(self):
            while self.isstopped():
                # inset sensors data into database
                try:
                    self.__st_Sensors()
                    logging.debug("Sensors insert success")
                except:
                    PrintException()
                    logging.debug("Sensors send failed")
                sleep(1)

        # thread put into threadpool
        def Thread_SendJsonData(self):
            while self.isstopped():
                try:
                    self.SendJsonToRemote()
                    logging.debug("Send json data success")
                except:
                    PrintException()
                    logging.debug("Send json data failed")
                sleep(1)

    def __init__(self):
        super(Switcher, self).__init__()
        # handlers
        # printcore handler
        self.printcore = None
        # handler for send json file and insert environment data
        self.sendData = None
        # thread pool handler
        self.pool = ThreadPool(6)

    def getTask(self, command):
        try:
            listcommand = command.split(" ", 1)
            print(("command list:", listcommand))
            if listcommand[0].strip() not in self.task:
                self.Default()
                return "No Command!"

            da.Insert_logs(listcommand[0])
            if len(listcommand) > 1:
                self.task.get(listcommand[0].strip())(listcommand[1].strip())
            else:
                self.task.get(listcommand[0].strip())()
            return "Command Send Success"
        except:
            PrintException()
            return "Server failed"

    def __check_gcode(self, filename):
        if filename.split(".")[-1] == "gcode":
            return True
        else:
            return False

    def connect(self):
        # TODO:bad connect method
        self.printcore = PrintCore(Port='/dev/ttyUSB0', Baud=250000)
        self.sendData = self.SendData(self.printcore)
        if self.printcore is not None:
            self.pool.add_task(self.sendData.Thread_SendJsonData)
            self.pool.add_task(self.sendData.Thread_InsertSensors)
        else:
            logging.error("Connect printer error!")

    def disconnect(self):
        self.printcore.disconnect()
        self.sendData.stopRunning()
        self.pool.wait_completion()
        self.sendData.SendJsonToRemote()

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

    def startprint(self, ClientFilePath):

        try:
            filename = ClientFilePath.split("/")[-1]
            print(("receive file name", filename))
            self.sendData.set_file_name(filename)
            newfilepath = os.path.join(filepath, filename)
            self.sendData.CleanTimer()

            if self.__check_gcode(filename):
                upload_server(newfilepath)

                # set print time!
                est_time = es_time(newfilepath)
                (hours, miniutes) = est_time.estime()
                self.sendData.Set_Print_Time(hours, miniutes)
                self.sendData.StartTimer()

                self.pool.add_task(
                    self.printcore.startprint(newfilepath)
                )
            else:
                print("not gcode file")
        except:
            PrintException()

    def Default(self):
        print("no command")


def main():
    try:
        sock = TCP_Server()
        DHT11.Init_WiringPi()
        switcher = Switcher()

        # prepare for file directory
        if not os.path.exists(filepath):
            os.makedirs(filepath)

        while True:
            logging.debug("server accept")
            sock.WaitForConnecting()
            src = sock.Client.recv(1024)
            if not src:
                logging.debug("command failed")
                continue
            else:
                print(("Client send:" + src))
                check = switcher.getTask(src)
                sock.Client.send(check)
            sock.Client.close()
    except KeyboardInterrupt:
        print("KeyboardInterrupt! Stop server")
        sys.exit(0)
    except socket.timeout:
        print("Time out")
        PrintException()
    except:
        PrintException()
        main()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    try:
        main()
    except KeyboardInterrupt:
        print("KeyboardInterrupt! Stop server")
        sys.exit(0)
    except:
        PrintException()
