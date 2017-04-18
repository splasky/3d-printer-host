#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2017-04-18 15:49:54

import json
from package.debug import PrintException
import getpass
import getpass
DEFAULTPATH = "/tmp/3dprinter_config"


class config_data(object):

    def __init__(self):
        self.DataBase_IP = ""
        self.DataBase_User = ""
        self.DataBase_Password = ""
        self.DataBase_Name = ""
        self.DataBase_Name = ""
        self.DataBase_Port = 0


class UseConfigs(object):

    def __init__(self):
        self.config = dict()

    def make_input(self):
        config = dict()
        config["DataBase_IP"] = raw_input("data base ip:")
        config["DataBase_Name"] = getpass.getpass("data base name:")
        config["DataBase_User"] = raw_input("data base login name:")
        config["DataBase_Password"] = getpass.getpass("data base password:")
        config["DataBase_Port"] = int(raw_input("data base port:"))
        return config

    def make_config(self, path=DEFAULTPATH):
        try:
            self.config = self.make_input()
            with open(path, 'w') as f:
                f.write(json.dumps(
                    self.config, separators=(',', ':'), sort_keys=True,
                ).encode('utf-8'))
        except:
            PrintException()

    def load_config(self, path=DEFAULTPATH):
        try:
            if path is "":
                raise RuntimeError("path is not correct!")

            with open(path, "r") as f:
                data = f.read()
                config = json.loads(data)
                self.config = dict((key, value) for key, value in config.items())

        except:
            PrintException()

    def print_config(self):
        print(self.config)

    def modify_config(self, path=DEFAULTPATH):
        try:
            self.make_config(path)
            print("Change config file success.")
        except:
            PrintException()
