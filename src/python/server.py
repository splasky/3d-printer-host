# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2018-05-31 10:38:04

import os
import sys
import logging
import threading
from package.thread_pool import ThreadPool
from package.debug import PrintException
from package.Switcher import Switcher
from package.redis_object import redis_handler
from package.environment_config import UseConfigs
from package.dht11 import libDHT11


class Server(object):

    def __init__(self, Directory="/home/pi/Rpi3dPrinter"):
        self.directory = os.path.join(Directory)
        self.pool = ThreadPool(6)
        self.stopped = threading.Event()
        self.check_directory()
        self.config_file_path = os.path.join(self.directory, "config_file.json")
        libDHT11.Init_WiringPi()
        self.config = UseConfigs(self.config_file_path)
        self.check_config()
        self.redis_handler = redis_handler(Host=self.config.config["redis_ip"],
                                           Port=self.config.config["redis_port"],
                                           master=self.config.config["redis_master"],
                                           slaver=self.config.config["redis_slaver"],
                                           password=self.config.config["redis_password"])

        self.switcher = Switcher(self.redis_handler, self.directory, self.pool)
        self.isStopped = False

    def Thread_main(self):
        logging.basicConfig(level=logging.DEBUG)
        try:
            print("server listening...")
            # wait for message
            while True:
                #  for message in self.redis_handler.pubsub.listen():
                message = self.redis_handler.pubsub.get_message()
                if message:
                    try:
                        src = message.get('data').decode('utf-8')
                        print(("Client send:" + src))
                        check = self.switcher.getTask(src)
                        #  self.redis_handler.send(check)
                    except:
                        PrintException()
                else:
                    self.switcher.Thread_add_Send_Sensors()
        except KeyboardInterrupt:
            print("KeyboardInterrupt! Stop server")
            self.stopped.set()
            sys.exit(0)
        except:
            PrintException()

    def run_main(self):
        self.pool.add_task(self.Thread_main())

    def __del__(self):
        self.close_main()
        self.pool.wait_completion()

    def check_directory(self):
        # check directory is exists
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    def check_config(self):
        if not self.config.check_config():
            self.config.make_config()
        self.config.load_config()

    def close_main(self):
        self.isStopped = False


if __name__ == "__main__":
    logging.basicConfig(filename='printer3d.log',
                        level=logging.DEBUG
                        )
    try:
        # path to put gcode
        directory = "/home/pi/Rpi3dPrinter"
        server = Server(directory)
        server.run_main()
    except KeyboardInterrupt:
        PrintException()
        sys.exit(0)
    except:
        PrintException()
        sys.exit(0)
