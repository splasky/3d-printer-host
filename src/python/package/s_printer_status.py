#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2016-10-04 19:10:32

import socket
import sys
import logging
import os
import time
from package.da import create_json_file
from debug import PrintException
from package.sock_proto import Send_File_Server


def S_printer_status(data):

    sendServer = Send_File_Server('', 6666)
    try:
        print("printer status waiting accept...")
        sendServer.WaitForConnecting()

        fpath = create_json_file(data)

        if fpath is not None:
            if sendServer.SendFile(fpath):
                print("send success")
            else:
                print("send printer status failed")
    except Exception, ex:
        PrintException()
        time.sleep(10)
    finally:
        del sendServer


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    data = {"Hello": 123, "loli": "prprp"}
    S_printer_status(data)
