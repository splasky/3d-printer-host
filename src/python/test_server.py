#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2017-04-21 14:50:07

from server import Server
import redis
import pytest
import tempfile


class Base:

    def __init__(self):
        self.host = '172.17.135.86'
        self.port = '6379'
        self.master = "control"
        self.sensor = "sensors"


@pytest.fixture
def cleandir():
    new_path = tempfile.mktemp()
    return new_path


@pytest.fixture(scope='module')
def master():
    base = Base()
    return redis.StrictRedis(host=base.host, port=base.port)


@pytest.fixture
def server(cleandir):
    return Server(cleandir)


def test_main(server, master):
    server.run_main()
    assert master.publish('control', 'connect')
    assert master.publish('control', 'home')
    assert master.publish('control', 'send_now G28')
    #  master.publish('control','startprint xxxx')
    assert master.publish('control', 'Helloworld!')
    assert master.publish('control', 'Hello world!')
    assert master.publish('control', 'disconnect')
