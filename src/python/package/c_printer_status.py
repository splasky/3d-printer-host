#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2016-10-03 20:34:57

import socket
import sys
import logging
import os
import signal
import time
from .debug import PrintException
from package.sock_proto import Get_File_Client


def C_printer_status(ReceivePath='/tmp/', Host='127.0.0.1', Port=6666):
    try:
        fileClient = Get_File_Client()
        print(("connect to :", Host))
        print("client printer status connecting...")
        fileClient.connect(Host, Port)

        if fileClient.ReceiveFile(ReceivePath):
            print("receive success!")
            time.sleep(5)
        else:
            print("receive error")
    except socket.error:
        print("printer status server connect error")
        time.sleep(10)
    except Exception as e:
        PrintException()
    finally:
        del fileClient


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    C_printer_status("localhost", 6666)
