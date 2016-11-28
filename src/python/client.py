#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2016-11-28 20:35:26

import socket
import sys
import logging
import os
import time
import json
import fcntl
import threading
from package.send import upload_client
from package.c_printer_status import C_printer_status
from package.debug import PrintException
from package.sock_proto import TCP_Client
from package.sock_proto import TCP_Server


printer_status_path = "/var/www/3dprint/php/json/"
FIFO = "/tmp/3dprinter.fifo"


class PrinterStatusDaemon(threading.Thread):

    def __init__(self, host, port=0, lock=False):
        """PrinterStatusDaemon
        """
        super(PrinterStatusDaemon, self).__init__()
        self._lock = threading.Lock()
        self.port = port
        self.host = host
        self.lock = lock

    def run(self):
        while self.lock:
            C_printer_status(printer_status_path, self.host,)


def main():
    localServer = TCP_Server(address='127.0.0.1', port=1025)
    lock = True

    PrinterStatusThread = None

    while True:
        try:
            localServer.WaitForConnecting()
            command = localServer.Client.recv(1024)

            #  command = raw_input("input:")
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
                    lock = False
                    PrinterStatusThread.join(10)
                    C_printer_status(printer_status_path, host,)

                if li[0].strip() == "connect":
                    lock = True
                    PrinterStatusThread = PrinterStatusDaemon(host, 6666, lock)
                    PrinterStatusThread.setDaemon(True)

            # recv from server
            redata = Client.recv(1024)
            print("recv data:", redata)
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
