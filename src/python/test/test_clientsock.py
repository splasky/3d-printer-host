#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2016-09-24 16:37:04


from package.sock_proto import Get_File_Client
from package.sock_proto import Send_File_Server
from threading import Thread

clientsock = None


def main():
    global clientsock
    clientsock = Get_File_Client()

    clientthread = Thread(target=testReceiveData())
    clientthread.start()
    clientthread.join()
    print("test finish!")


def testReceiveData():
    global clientsock
    clientsock.connect('127.0.0.1', 6000)
    clientsock.ReceiveFile("/tmp")


if __name__ == "__main__":
    main()
