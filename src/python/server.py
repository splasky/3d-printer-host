# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2017-04-21 16:21:04

import os
import sys
import logging
from package.debug import PrintException
from package.Switcher import Switcher
from package.redis_object import redis_handler
from package.environment_config import UseConfigs
from package import DHT11


class Server(object):

    def __init__(self, Directory="/home/pi/Rpi3dPrinter"):
        self.directory = os.path.join(Directory)
        self.check_directory()
        self.config_file_path = os.path.join(self.directory, "config_file.json")
        DHT11.Init_WiringPi()
        self.config = UseConfigs(self.config_file_path)
        self.check_config()
        self.redis_handler = redis_handler(Host=self.config.config["redis_ip"],
                                           Port=self.config.config["redis_port"],
                                           master=self.config.config["redis_master"],
                                           slaver=self.config.config["redis_slaver"])
        self.switcher = Switcher(self.redis_handler, self.directory)
        self.isStopped = False

    def run_main(self):
        self.isStopped = True
        listener = self.redis_handler.listen()
        try:
            while self.isStopped:
                try:
                    # wait for message
                    src = listener.next().get('data').decode('utf-8')
                    print(("Client send:" + src))
                    check = self.switcher.getTask(src)
                    self.redis_handler.send(check)
                except StopIteration:
                    pass
                except:
                    PrintException()
        except KeyboardInterrupt:
            print("KeyboardInterrupt! Stop server")
            sys.exit(0)
        except:
            PrintException()

    def check_directory(self):
        # check directory is exists
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    def check_config(self):
        if not self.config.check_config():
            self.config.make_config()
        self.config.load_config()

    def close_main():
        self.isStopped = False


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    # path to put gcode
    directory = "/home/pi/Rpi3dPrinter"
    server = Server(directory)
    server.run_main()
