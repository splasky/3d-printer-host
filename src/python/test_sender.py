#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2016-09-02 17:10:57

import socket
import logging
import os
from package import send


try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except:
    logging.debug("socket error")
    sys.exit(1)

port = 8888
host = ''  # Symbolic name meaning all available interfaces
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # reuse tcp
sock.bind((host, port))
sock.listen(5)
#  sock.settimeout(10)

p = None
(csock, adr) = sock.accept()
# send file name
csock.send("loli.txt")
# start send file
send.sender(os.path.abspath("./test.txt"), 5000)
csock.close()
