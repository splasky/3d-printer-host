# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2016-11-29 13:37:14

import socket
import da
import sys
import logging
import os
import subprocess
import shlex
from threading import Thread
from package.send import upload_server
from package.s_printer_status import S_printer_status
from package.debug import PrintException
from package.sock_proto import TCP_Server
from package.da import PrintCore
from package.da import CommandSwitchTableProto
from package import da
from package import DHT11
from package.printtime import check_print_time
import threading


# path to put gcode
filepath = "/home/pi/temp/"


class Switcher(CommandSwitchTableProto):

    def __init__(self):
        super(Switcher, self).__init__()
        # handlers
        self.printcore = None
        self.__Th_printer_st = None
        self.__rtmpprocess = None
        self.__fileName = ""
        self.__printtimeHandler = check_print_time()

    class StoppableThread(Thread):

        def __init__(self, target='', name=''):
            super(StoppableThread, self).__init__(target=target, name=name)
            self.__lock = True

        def stopRun(self):
            self.__lock = False

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

    def __createJsonData(self):
        # get printer status data
        data = self.printcore.printer_status()
        # get filename if startprint is start
        data["File_Name"] = self.__fileName
        if self.__fileName is not "":
            data["PrintTime"] = self.__printtimeHandler.end_time()
        logging.debug(data)
        return data

    def __st_thread(self):
        while self.__Th_printer_st.stopped():
            self.__st_Sensors()
            S_printer_status(self.__createJsonData())
            logging.debug("run st_thread success!")

    def __st_Sensors(self):
        sensors_data = da.get_Sensors_data()
        if sensors_data is not None:
            sensors_data["IR_temperature"] = self.printcore.headtemp()
            da.Send_Sensors(data=sensors_data)

    def __check_gcode(self, filename):
        if filename.split(".")[-1] == "gcode":
            return True
        else:
            return False

    def connect(self):
        self.printcore = PrintCore(Port='/dev/ttyUSB0', Baud=250000)
        if self.printcore is not None:
            # the lock for start or stop the S_printer_status
            self.__Th_printer_st = StoppableThread(
                target=self.__st_thread,
                name="printer_status_server")
            self.__Th_printer_st.setDaemon(True)

    def disconnect(self):
        self.printcore.disconnect()
        if self.__Th_printer_st.isAlive is True:
            self.__Th_printer_st.join()

    def reset(self):
        self.printcore.reset()

    def pause(self):
        self.printcore.pause()

    def resume(self):
        self.printcore.resume()

    def cancel(self):
        self.printcore.cancel()

    def home(self):
        self.printcore.home()

    def send_now(self, command):
        self.printcore.send_now(command.strip("\n"))

    def startprint(self, ClientFilePath):

        filename = ClientFilePath.split("/")[-1]
        print("receive file name", filename)
        self.__fileName = filename

        newfilepath = os.path.join(filepath, filename)
        self.__printtimeHandler.print_time(newfilepath)

        if self.__check_gcode(filename):
            upload_server(newfilepath)
            self.printcore.startprint(newfilepath)
        else:
            print("not gcode file")

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
