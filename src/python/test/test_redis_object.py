#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2017-04-21 14:27:23


import pytest
import time
from package.redis_object import redis_handler
from multiprocessing import Process

host = "172.17.135.86"
port = 6379
master = "control"
slave = "slave"


@pytest.fixture(scope='module')
def h1():
    return redis_handler(Port=port, Host=host, master=master, slaver=slave)


@pytest.fixture(scope='module')
def h2():
    return redis_handler(Port=port, Host=host, master=slave, slaver=master)


def test_send(h1, h2):
    assert h1.send("Loli") is True


def test_recv(h1, h2):
    h2.send("Loli")
    assert h1.recv().get("data").decode("utf-8") == "Loli"


def handler2_send(sender):
    for i in range(10):
        sender.send("loli")
        time.sleep(0.1)


def test_listen(h1, h2):
    p = Process(target=handler2_send, args=(h2,))
    p.start()
    p.join()
    generator = h1.listen()
    for i in range(10):
        data = generator.next()
        assert data.get("data").decode("utf-8") == "loli"
