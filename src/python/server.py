<<<<<<< HEAD
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2016-11-30 20:59:13

import socket
import da
import sys
import logging
import os
import subprocess
import shlex
import multiprocessing
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
from package.printtime import check_print_time
import threading


# path to put gcode
filepath = "/home/pi/temp/"


class Switcher(CommandSwitchTableProto):

    class SendData(object):

        def __init__(self, printercore):
            self.printcore = printercore
            self.fileName = ""
            self.lock = True

        def stopRunning(self):
            self.lock = False

        def stopped(self):
            return self.lock

        def set_file_name(self, filename):
            self.fileName = filename

        def __st_Sensors(self):
            sensors_data = da.get_Sensors_data()
            if sensors_data is not None:
                sensors_data["IR_temperature"] = self.printcore.headtemp()
                da.Send_Sensors(data=sensors_data)

        def __createJsonData(self):
            # get printer status data
            data = self.printcore.printer_status()

            # get filename if startprint is start
            data["File_Name"] = self.fileName
            if self.fileName is not "":
                # TODO:printtime
                #  data["PrintTime"] = self.__printtimeHandler.end_time()
                pass
            logging.debug(data)
            return data

        def Thread_InsertSensors(self):
            while self.stopped():
                # inset sensors data into database
                self.__st_Sensors()
                sleep(1)

        def SendJsonToRemote(self):
            S_printer_status(self.__createJsonData())

        def Thread_SendJsonData(self):
            while self.stopped():
                # start json file
                self.SendJsonToRemote()
                logging.debug("run st_thread success!")

    def __init__(self):
        super(Switcher, self).__init__()
        # handlers
        self.printcore = None
        self.__rtmpprocess = None
        self.sendData = None
        self.pool = ThreadPool(6)

        # TODO:check print time
        #  self.__printtimeHandler = check_print_time()

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
            self.pool.add_task(self.sendData.Thread_InsertSensors)
            self.pool.add_task(self.sendData.Thread_SendJsonData)
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
        self.sendData.set_file_name(filename)

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
=======
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2017-05-10 21:01:08

import os
import sys
import logging
import threading
from package.thread_pool import ThreadPool
from package.debug import PrintException
from package.Switcher import Switcher
from package.redis_object import redis_handler
from package.environment_config import UseConfigs
from package.dht11 import libDHT11


class Server(object):

    def __init__(self, Directory="/home/pi/Rpi3dPrinter"):
        self.directory = os.path.join(Directory)
        self.pool = ThreadPool(6)
        self.stopped = threading.Event()
        self.check_directory()
        self.config_file_path = os.path.join(self.directory, "config_file.json")
        libDHT11.Init_WiringPi()
        self.config = UseConfigs(self.config_file_path)
        self.check_config()
        self.redis_handler = redis_handler(Host=self.config.config["redis_ip"],
                                           Port=self.config.config["redis_port"],
                                           master=self.config.config["redis_master"],
                                           slaver=self.config.config["redis_slaver"],
                                           password=self.config.config["redis_password"])

        self.switcher = Switcher(self.redis_handler, self.directory, self.pool)
        self.isStopped = False

    def Thread_main(self):
        logging.basicConfig(level=logging.DEBUG)
        try:
            print("server listening...")
            # wait for message
            while True:
                #  for message in self.redis_handler.pubsub.listen():
                message = self.redis_handler.pubsub.get_message()
                if message:
                    try:
                        src = message.get('data').decode('utf-8')
                        print(("Client send:" + src))
                        check = self.switcher.getTask(src)
                        #  self.redis_handler.send(check)
                    except:
                        PrintException()
                else:
                    self.switcher.Thread_add_Send_Sensors()
        except KeyboardInterrupt:
            print("KeyboardInterrupt! Stop server")
            self.stopped.set()
            sys.exit(0)
        except:
            PrintException()

    def run_main(self):
        self.pool.add_task(self.Thread_main())

    def __del__(self):
        self.close_main()
        self.pool.wait_completion()

    def check_directory(self):
        # check directory is exists
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    def check_config(self):
        if not self.config.check_config():
            self.config.make_config()
        self.config.load_config()

    def close_main(self):
        self.isStopped = False


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    try:
        # path to put gcode
        directory = "/home/pi/Rpi3dPrinter"
        server = Server(directory)
        server.run_main()
    except KeyboardInterrupt:
        PrintException()
        sys.exit(0)
    except:
        PrintException()
        sys.exit(0)
>>>>>>> dev
