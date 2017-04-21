# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2017-04-21 14:45:07

import os
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
        self.switcher = Switcher(redis_handler, self.directory)
        self.config = UseConfigs(self.config_file_path)
        self.check_config()
        self.redis_handler = redis_handler(Host=self.config.config["redis_ip"],
                                           Port=self.config.config["redis_port"],
                                           master=self.config.config["redis_master"],
                                           slaver=self.config.config["redis_slaver"])

    def run_main(self):
        try:
            while True:
                try:
                    # wait for message
                    src = self.redis_handler.listen().get('data').decode('utf-8')
                    print(("Client send:" + src))
                    check = self.switcher.getTask(src)
                    self.redis_handler.send(check)
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
        if self.config.check_config():
            self.config.make_config(self.config_file_path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    # path to put gcode
    directory = "/home/pi/Rpi3dPrinter"
    server = Server(directory)
    server.run_main()
