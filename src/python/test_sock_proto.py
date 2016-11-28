#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2016-09-24 16:27:28


from package.sock_proto import Send_File_Server
from threading import Thread

serversock = None


def main():
    global serversock
    serversock = Send_File_Server('', 6000)

    serverthread = Thread(target=testSendData())
    serverthread.start()
    serverthread.join()
    print("test finish!")


def testSendData():
    global serversock, clientsock
    serversock.WaitForConnecting()
    serversock.SendFile("/home/splasky/test.gcode")


if __name__ == "__main__":
    main()
