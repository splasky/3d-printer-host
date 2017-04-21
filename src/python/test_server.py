#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2017-04-21 14:37:09

import server
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


@pytest.fixture(scope='module')
def server(cleandir):
    return Server(cleandir)


def test_main(server, master):
    server.run_main()
    master.publish('control', 'connect')
    master.publish('control', 'home')
    master.publish('control', 'send_now G28')
    #  master.publish('control','startprint xxxx')
    master.publish('control', 'Helloworld!')
    master.publish('control', 'Hello world!')
    master.publish('control', 'disconnect')
