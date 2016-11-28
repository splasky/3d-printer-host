#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Copyright © splasky
# Last modified: 2016-09-02 16:52:24

from package.send import receive_file
import socket
import logging
import os


try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except:
    logging.debug("socket error")
    sys.exit(1)
logging.basicConfig(level=logging.DEBUG)
port = 8888
host = "127.0.0.1"  # Symbolic name meaning all available interfaces
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # reuse tcp
sock.connect((host, port))

# send file name
file_name = sock.recv(1024)
# start send file
receive_file(os.path.join("./", file_name), "127.0.0.1", 5000)

sock.close()
