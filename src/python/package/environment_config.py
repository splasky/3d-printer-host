#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2017-05-05 16:36:27

import json
from package.debug import PrintException
import getpass
import getpass
import os


class config_data(object):

    def __init__(self):
        self.redis_ip = ""
        self.redis_master = ""
        self.redis_slaver = ""
        self.redis_port = 0
        self.redis_password


class UseConfigs(object):

    def __init__(self, path):
        self.config = dict()
        self.config_file_path = path

    def check_config(self):
        if not os.path.exists(self.config_file_path) or not os.path.isfile(self.config_file_path):
            return False
        return True

    def make_input(self):
        config = dict()
        config["redis_ip"] = raw_input("redis ip:")
        config["redis_port"] = int(raw_input("redis port:"))
        config["redis_password"] = raw_input("redis password:")
        config["redis_master"] = raw_input("redis master:")
        config["redis_slaver"] = raw_input("redis slaver:")
        return config

    def make_config(self):
        try:
            self.config = self.make_input()
            with open(self.config_file_path, 'w') as f:
                f.write(json.dumps(
                    self.config, separators=(',', ':'), sort_keys=True,
                ).encode('utf-8'))
            return True
        except:
            PrintException()
            return False

    def load_config(self):
        try:
            with open(self.config_file_path, "r") as f:
                data = f.read()
                config = json.loads(data)
                self.config = dict((key, value) for key, value in config.items())

            return True
        except:
            PrintException()
            return False

    def print_config(self):
        print(self.config)

    def get_configs(self):
        return self.config

    def get_config_file_path(self):
        return self.config_file_path

    def modify_config(self):
        try:
            self.make_config(self.config_file_path)
            print("Change config file success.")
            return True
        except:
            PrintException()
            return False
