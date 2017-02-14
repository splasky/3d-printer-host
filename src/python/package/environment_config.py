#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2017-02-14 18:52:12

import json
from package.debug import PrintException

DEFAULTPATH = "/tmp/3dprinter_config"


class config_data(object):

    def __init__(self):
        self.DataBase_IP = ""
        self.DataBase_User = ""
        self.DataBase_Password = ""

    def make_config(self, path=DEFAULTPATH):
        self.DataBase_IP = raw_input("data base ip:")
        self.DataBase_User = raw_input("data base user:")
        self.DataBase_Password = raw_input("data base password:")

        try:
            with open(path, 'w') as f:
                f.write(json.dumps(
                    {"DataBase_IP": self.DataBase_IP, "DataBase_User": self.DataBase_User,
                        "DataBase_Password": self.DataBase_Password}
                ).encode('utf-8'))
        except:
            PrintException()

    def load_config(self, path=DEFAULTPATH):
        if path is "":
            raise RuntimeError("path is not correct!")
        try:
            with open(path, "r") as f:
                data = f.read()
                config = json.loads(data)
                self.DataBase_IP = config["DataBase_IP"]
                self.DataBase_User = config["DataBase_User"]
                self.DataBase_Password = config["DataBase_Password"]
        except:
            PrintException()
