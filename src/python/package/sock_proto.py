#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2016-10-07 14:47:00

import socket
import os
import logging
from .debug import PrintException


class TCP_Server(object):

    def __init__(self, address='', port=8888, MaxClient=5):
        self.s = socket.socket()
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.address = address
        self.port = port
        self.s.bind((self.address, self.port))
        self.s.listen(MaxClient)

    def WaitForConnecting(self):
        print("Waiting for connecting")
        self.Client, self.Addr = self.s.accept()
        logging.debug("get connect from Client:{0},Address:{1}".format(self.Client, self.Addr))


class Send_File_Server(TCP_Server):

    def __init__(self, address, port):
        #  self.address = address
        #  self.port = port
        super(Send_File_Server, self).__init__(address, port)
        self.s.settimeout(20)

    def __check_send(self):
        try:
            # recv check message
            check = self.Client.recv(1024)
            print(("Check:", check))
            del check
            return True
        except socket.timeout:
            print("check time out")
            return False
        except:
            PrintException()
            return False

    def SendData(self, filepath, filesize):
        try:
            # send file size
            self.Client.send(str(filesize))
            if not self.__check_send():
                raise Exception("Check send failed on filesize")

            print("check ok start sending data...")
            # send data
            with open(os.path.abspath(filepath), 'r') as f:
                data = f.read(1024)
                remain_data = filesize
                while(data):
                    self.Client.send(data)
                    data = f.read(1024)
                    remain_data -= len(data)
                    print(("send {0} bytes string,remaining {1} bytes".format(
                        len(data), remain_data)))
            print("Sender Done sending")
            return True
        except socket.timeout:
            print("send data time out")
            return False
        except Exception:
            PrintException()
            return False

    def SendFile(self, filepath):
        try:
            filesize = os.path.getsize(filepath)
            filename = filepath.split("/")[-1]
            print(("start send file:", filename, "file size:", filesize))

            # send file name
            print(("send file name", filename))
            self.Client.send(filename)
            if not self.__check_send():
                raise Exception("Check send failed on file name")

            if not self.SendData(filepath, filesize):
                raise Exception("send data failed")

            return True
        except:
            PrintException()
            return False
        finally:
            if hasattr(self, 'self.Client'):
                self.Client.close()


class TCP_Client(object):

    def __init__(self):
        self.sock = socket.socket()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def connect(self, address, port):
        print("Connect to server...")
        self.sock.connect((address, int(port)))


class Get_File_Client(TCP_Client):

    """get send file server's data"""

    def __init__(self):
        """initialized """
        TCP_Client.__init__(self)
        self.sock.settimeout(20)

    def __check_send(self):
        try:
            # recv check message
            check = self.sock.send("ok")
        except socket.timeout:
            print("check time out")
        except:
            PrintException()

    def ReceiveData(self, filepath, filename=''):
        try:
            print("start Receving data...")
            # receive file size
            filesize = self.sock.recv(1024)
            print(("file size:", filesize))
            self.__check_send()

            # receive data
            with open(os.path.abspath
                      (os.path.join(filepath, filename)), 'w') as f:
                data = self.sock.recv(1024)
                while(data):
                    f.write(data)
                    data = self.sock.recv(1024)
            print("Receiver done receiving")
            return True
        except:
            PrintException()
            return False

    def ReceiveFile(self, filepath):
        try:
            print("start receiving file...")
            print("Receive file name...")
            filename = self.sock.recv(1024)
            if filename is None:
                raise Exception("Receive file name failed")

            print(("file name:{0}".format(filename)))
            self.__check_send()

            if not self.ReceiveData(filepath, filename):
                raise Exception("Receive data failed")

            return True
        except:
            PrintException()
            return False
        finally:
            self.sock.close()
