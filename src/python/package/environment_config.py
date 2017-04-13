#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2017-02-14 19:36:46

import json
from package.debug import PrintException

DEFAULTPATH = "/tmp/3dprinter_config"


class config_data(object):

    def __init__(self):
        self.DataBase_IP = ""
        self.DataBase_User = ""
        self.DataBase_Password = ""
        self.DataBase_Name = ""
        self.port = 0

    def make_config(self, path=DEFAULTPATH):
        self.DataBase_IP = raw_input("data base ip:")
        self.DataBase_User = raw_input("data base user:")
        self.DataBase_Password = raw_input("data base password:")
        self.DataBase_Name = raw_input("data base name:")
        self.port = int(raw_input("data base port:"))

        try:
            with open(path, 'w') as f:
                f.write(json.dumps(
                    {
                        "DataBase_IP": self.DataBase_IP,
                        "DataBase_User": self.DataBase_User,
                        "DataBase_Password": self.DataBase_Password,
                        "DataBase_Name": self.DataBase_Name,
                        "DataBase_port": self.port
                    }
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
                self.DataBase_Name = config["DataBase_Name"]
                self.port = config["DataBase_port"]
        except:
            PrintException()
