#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2016-10-05 17:21:40

import socket
import os
import logging
import sys
import time
from .debug import PrintException


def sender(file_name, port_num=5000):
    try:
        port = port_num
        s = socket.socket()
        host = ''
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # reuse tcp
        s.settimeout(30)
        s.bind((host, port))
        s.listen(5)

        filesize = os.path.getsize(file_name)
        print(("start send file:", file_name, "file size:", filesize))
        conn, addr = s.accept()

        print("start sending file...")
        print(("Got connection from", addr))
        with open(os.path.abspath(file_name), 'r') as f:
            # send file size
            conn.send(str(os.fstat(f.fileno()).st_size))
            time.sleep(1)

            # send data
            data = f.read(1024)
            remain_data = filesize
            while(data):
                conn.send(data)
                data = f.read(1024)
                remain_data -= len(data)
                print(("send %s bytes string,remaining %s bytes",
                      len(data), remain_data))
        print("Sender Done sending")
        return True
    except:
        PrintException()
        return False
    finally:
        conn.close()


def receiver(file_name, host, port_num=5000):
    try:
        port = port_num
        sock = socket.socket()
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # reuse tcp
        sock.settimeout(30)
        time.sleep(1)
        sock.connect((host, port))

        print("start Receving file...")
        # receive file size
        filesize = sock.recv(1024)
        print(("file size:", filesize))

        # receive data
        with open(os.path.abspath(file_name), 'w') as f:
            data = sock.recv(1024)
            while(data):
                f.write(data)
                data = sock.recv(1024)
        print("Receiver done receiving")
        return True
    except:
        PrintException()
        return False
    finally:
        sock.close()


def upload_client(filepath, Host, Port=6000):
    try:
        port = Port
        s = socket.socket()
        host = Host
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # reuse tcp
        s.settimeout(20)

        time.sleep(1)
        s.connect((host, port))

        filesize = os.path.getsize(filepath)
        print(("start send file:", filepath, "file size:", filesize))
        filename = filepath.split("/")[-1]
        s.send(filename)

        # get feedback
        check = s.recv(1024)
        print(("check:", check))

        print("start sending file...")
        with open(os.path.abspath(filepath), 'r') as f:
            # send file size
            s.send(str(os.fstat(f.fileno()).st_size))

            # recv check message
            check = s.recv(1024)
            print(("get check message:", check))
            del check

            # start send data
            data = f.read(1024)
            remain_data = filesize
            while(data):
                s.send(data)
                data = f.read(1024)
                remain_data -= len(data)
                print(("send {0} bytes string,remaining {1} bytes".format(
                    len(data), remain_data)))
        print("Send file done sending")
        return True
        s.close()
    except socket.timeout:
        logging.error("time out of sending file")
        return False
    except:
        PrintException()
        return False


def upload_server(filepath, Port=6000):
    try:
        port = Port
        sock = socket.socket()
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # reuse tcp
        #  time.sleep(1)
        sock.settimeout(20)
        sock.bind(('', port))
        sock.listen(5)
        (conn, addr) = sock.accept()

        filename = conn.recv(1024)
        print(("Receive file name:", filename))
        conn.send("check")

        print("start Receving file...")
        # receive file size
        filesize = conn.recv(1024)
        print(("file size:", filesize))

        # ok recv success
        conn.send("ok")

        # receive data
        with open(os.path.abspath(filepath), 'w') as f:
            data = conn.recv(1024)
            while(data):
                f.write(data)
                data = conn.recv(1024)
        print("Receive file done receiving")
        conn.close()
        return True
    except socket.error:
        print("connect refused error!")
        time.sleep(0.5)
        return False
    except socket.timeout:
        print("time out of receive")
        return False
    except Exception as ex:
        PrintException()
        return False
