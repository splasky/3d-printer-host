#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2017-04-21 11:48:52


# master:'control'
# slaver:'sensor'

import redis
import time


class redis_handler(object):

    def __init__(self, Host, Port, master, slaver):
        self.redis_handler = redis.StrictRedis(host=Host, port=Port, db=0)
        self.master = master
        self.slaver = slaver
        self.pubsub = self.redis_handler.pubsub(ignore_subscribe_messages=True)
        self.pubsub.subscribe(self.master)
        self.__isStopped = False

    def send(self, data):
        self.redis_handler.publish(self.slaver, data)
        return True

    def recv(self):
        while True:
            message = self.pubsub.get_message()
            if message:
                return message
            time.sleep(0.001)

    def listen(self):
        while not self.__isStopped:
            message = self.pubsub.get_message()
            if message:
                yield message
            time.sleep(0.001)

    def close_listen(self):
        self.__isStopped = True

    def __del__(self):
        self.__isStopped = False
