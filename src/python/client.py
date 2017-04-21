#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2017-04-18 16:40:21

import socket
import sys
import logging
import os
import time
import json
import fcntl
import threading
import subprocess
from subprocess import Popen
from package.send import upload_client
from package.c_printer_status import C_printer_status
from package.debug import PrintException
from package.sock_proto import TCP_Client
from package.sock_proto import TCP_Server


printer_status_path = os.path.join("/var/www/3dprint/php/json/")
printer_status_file = path = printer_status_path + "printer.json"
mjpg_path = "/home/pi/mjpg-streamer/mjpg-streamer.sh"


class PrinterJson(object):

    def __init__(self):
        self.online = False
        self.baud = 0
        self.PrintPercent = 0
        self.isprinting = False
        self.clear = True
        self.File_Name = None
        self.online = False
        self.position = None
        self.port = None

    def generate(self):
        data = dict()
        data["baud"] = self.baud
        data["PrintPercent"] = self.PrintPercent
        data["isprinting"] = self.isprinting
        data["clear"] = self.clear
        data["File_Name"] = self.File_Name
        data["online"] = self.position
        data["port"] = self.port
        return data


def offline():
    try:
        with open(printer_status_file, 'w') as file:
            fcntl.lockf(file, fcntl.LOCK_EX)
            data = PrinterJson()
            file.write(data)
        subprocess.call([mjpg_path, "stop"])
    except:
        logging.debug("error when write to printer.json")


class PrinterStatusDaemon(threading.Thread):

    def __init__(self, host, port=0):
        """PrinterStatusDaemon
        """
        super(PrinterStatusDaemon, self).__init__()
        #  self._lock = threading.Lock()
        self.port = port
        self.host = host
        self.lock = True

    def run(self):
        while self.lock:
            C_printer_status(printer_status_path, self.host,)

    def stopRun(self):
        self.lock = False


def main():
    localServer = TCP_Server(address='127.0.0.1', port=1025)

    PrinterStatusThread = None

    while True:
        try:
            localServer.WaitForConnecting()
            command = localServer.Client.recv(1024)
            command = command.split(" ", 2)
            if len(command) < 2:
                print("error: must enter ip and port")
                logging.debug(command)
                continue

            # parse receive
            logging.debug(command)
            host = command[0].strip()
            port = int(command[1].strip())
            comm = command[2].strip()
            logging.debug("commands:{0}".format(comm))

            Client = socket.create_connection((host, port), 20)

            print("client :connect success!")
            # send all command
            Client.send(str(comm))

            li = comm.split(" ", 1)
            print(li)

            if len(li) > 1:
                if li[0].strip() == "startprint":
                    # send file (absolute file name)
                    upload_client(li[1].strip(), host,)
            else:
                if li[0].strip() == "disconnect":
                    time.sleep(5)  # wait for server stop and get last status
                    PrinterStatusThread.stopRun()
                    PrinterStatusThread.join(20)
                    offline()

                if li[0].strip() == "connect":
                    PrinterStatusThread = PrinterStatusDaemon(host, 6666)
                    PrinterStatusThread.daemon = True
                    PrinterStatusThread.start()

            # recv from server
            redata = Client.recv(1024)
            print(("recv data:", redata))
            Client.close()
            del Client
        except KeyboardInterrupt:
            print("KeyboardInterrupt!")
            exit(0)
        except:
            PrintException()
            time.sleep(20)
        finally:
            pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
