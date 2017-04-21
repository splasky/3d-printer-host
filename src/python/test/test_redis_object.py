#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2017-04-20 18:35:41


import pytest
from package.redis_object import redis_handler

host = "172.17.135.86"
port = 6379
master = "control"
slave = "slave"
handler1 = redis_handler(Port=port, Host=host, master=master, slaver=slave)
handler2 = redis_handler(Port=port, Host=host, master=slave, slaver=master)


def test_send():
    assert handler1.send("Loli") is True
    assert handler1.recv()


def test_recv():
    handler2.send("loli")
    assert handler1.recv()["data"].decode("utf-8") == "loli"
