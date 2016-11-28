#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2016-09-02 17:10:56

import socket
#  import da
import sys
import send
import logging
import os


def string_parser(sockfd, src, p):
    if src == "connect":
        logging.debug("connect")
    elif src == "disconnect":
        logging.debug("dissconnect")
    elif src == "reset":
        logging.debug("reset")
    elif src == "pause":
        logging.debug("pause")
    elif src == "resume":
        logging.debug("resume")
    elif src == "cancel":
        logging.debug("cancel")
    elif src == "home":
        logging.debug("home")
    elif src == "send_now":
        logging.debug("send_now")
    elif src == "startprint":
        logging.debug("startprint")
    else:
        logging.warning("no commend")
    return p


def main():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        logging.debug("socket error")
        sys.exit(1)

    port = 8888
    host = ''  # Symbolic name meaning all available interfaces
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # reuse tcp
    sock.bind((host, port))
    sock.listen(5)
    #  sock.settimeout(10)

    p = None
    try:
        while True:
            logging.debug("server accept")
            (csock, adr) = sock.accept()
            print ("Client Info: ", csock, adr)
            src = csock.recv(1024)
            if not src:
                pass
            else:
                p = string_parser(csock, src, p)
                print ("Client send: " + src)
                csock.send("Hello I'm Server.\r\n")
    except KeyboardInterrupt:
        print("KeyboardInterrupt! Stop server")
        csock.close()
        sys.exit(0)
    finally:
        csock.close()

if __name__ == "__main__":
    main()
