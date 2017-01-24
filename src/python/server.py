# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2017-01-20 16:31:40

import socket
import da
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


class Switcher(CommandSwitchTableProto):

    class SendData(object):

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

        def __init__(self, printercore):
            self.printcore = printercore
            self.fileName = ""
            self.lock = True
            self.print_time = self.Print_time()
            self.Timer = PercentTimer()

        def stopRunning(self):
            self.lock = False

        def stopped(self):
            return self.lock

        def set_file_name(self, filename):
            self.fileName = filename

        def Set_Print_Time(self, hour=0, miniute=0):
            self.print_time.hour = hour
            self.print_time.miniute = miniute
            self.Timer.TotalTime = (hour * 60 + miniute) * 60

        def StopTimer(self):
            self.Timer.stopTimer()

        def StartTimer(self):
            self.Timer.startTimer()

        def CleanTimer(self):
            self.Timer.cleanTimer()

        def __st_Sensors(self):
            sensors_data = da.get_Sensors_data()
            if sensors_data is not None:
                if self.printcore.is_printing():
                    sensors_data["IR_temperature"] = 200.0
                sensors_data["IR_temperature"] = self.printcore.headtemp()
                da.Send_Sensors(data=sensors_data)

        def __createJsonData(self):
            try:

                # get printer status data
                data = self.printcore.printer_status()

                # get filename if startprint is start
                data["File_Name"] = self.fileName
                data["PrintPercent"] = 0
                if self.fileName is not "":
                    # add print time into data
                    data["PrintPercent"] = self.Timer.getPercent()
                logging.debug(data)
                return data
            except:
                PrintException()

        def Thread_InsertSensors(self):
            while self.stopped():
                # inset sensors data into database
                try:
                    self.__st_Sensors()
                    logging.debug("Sensors insert success")
                except:
                    PrintException()
                    logging.debug("Sensors send failed")
                sleep(1)

        def SendJsonToRemote(self):
            S_printer_status(self.__createJsonData())

        def Thread_SendJsonData(self):
            while self.stopped():
                self.SendJsonToRemote()
                logging.debug("Send json data success")

    def __init__(self):
        super(Switcher, self).__init__()
        # handlers
        self.printcore = None
        self.sendData = None
        self.pool = ThreadPool(6)

    def getTask(self, command):
        listcommand = command.split(" ", 1)
        print("command list:", listcommand)
        if listcommand[0].strip() not in self.task:
            self.Default()
            return "No Command!"

        da.Insert_logs(listcommand[0])
        if len(listcommand) > 1:
            self.task.get(listcommand[0].strip())(listcommand[1].strip())
        else:
            self.task.get(listcommand[0].strip())()
        return "Command Send Success"

    def __check_gcode(self, filename):
        if filename.split(".")[-1] == "gcode":
            return True
        else:
            return False

    def connect(self):
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
            print("receive file name", filename)
            self.sendData.set_file_name(filename)
            newfilepath = os.path.join(filepath, filename)
            self.sendData.CleanTimer()

            if self.__check_gcode(filename):
                upload_server(newfilepath)

                # set print time!
                est_time = es_time(newfilepath)
                (x, y) = est_time.estime()
                self.sendData.Set_Print_Time(x, y)
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
    DHT11.Init_WiringPi()
    sock = TCP_Server()
    switcher = Switcher()

    # prepare for file directory
    if not os.path.exists(filepath):
        os.makedirs(filepath)

    while True:
        try:
            logging.debug("server accept")
            sock.WaitForConnecting()
            src = sock.Client.recv(1024)
            if not src:
                logging.debug("command failed")
                continue
            else:
                print("Client send:" + src)
                check = switcher.getTask(src)
                sock.Client.send(check)
        except KeyboardInterrupt:
            print("KeyboardInterrupt! Stop server")
            sys.exit(0)
            break
        except socket.timeout:
            print("Time out")
            PrintException()
        except Exception, ex:
            PrintException()
        finally:
            sock.Client.close()


if __name__ == "__main__":
    try:
        logging.basicConfig(level=logging.DEBUG)
        main()
    except KeyboardInterrupt:
        print("KeyboardInterrupt! Stop server")
        sys.exit(0)
    except:
        PrintException()
