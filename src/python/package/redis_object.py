#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2017-04-21 09:45:06


# master:'control'
# slaver:'sensor'

import redis


class redis_handler(object):

    def __init__(self, Host, Port, master, slaver):
        self.redis_handler = redis.StrictRedis(host=Host, port=Port, db=0)
        self.master = master
        self.slaver = slaver
        self.pubsub = self.redis_handler.pubsub()
        self.pubsub.subscribe(self.master)

    def send(self, data):
        self.redis_handler.publish(self.slaver, data)
        return True

    def recv(self):
        message = self.pubsub.get_message()
        return message

    def listen(self):
