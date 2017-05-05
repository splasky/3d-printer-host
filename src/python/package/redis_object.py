#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2017-05-05 16:45:10


# master:'control'
# slaver:'sensor'

import redis
import time


class redis_handler(object):

    def __init__(self, Host, Port, master, slaver, password):
        self.redis_handler = redis.StrictRedis(host=Host, port=Port, db=0, password=password)
        self.master = master
        self.slaver = slaver
        self.pubsub = self.redis_handler.pubsub(ignore_subscribe_messages=True)
        self.pubsub.subscribe(self.master)

    def send(self, data):
        self.redis_handler.publish(self.slaver, data)
        return True

    def recv(self):
        while True:
            message = self.pubsub.get_message()
            if message:
                return message
            time.sleep(0.001)

    def __del__(self):
        self.__isStopped = False
