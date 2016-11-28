#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2016-10-06 20:48:23

import shlex
import logging
import subprocess
import threading
import time


def rtmp():
    """run rtmp server.
    :returns: status

    """
    # args = shlex.split('/home/pi/mjpg_streamer/mjpg_streamer - i
    # "./input_uvc.so -y -n -f 30 " - o ". /output_http.so - w ./www - p
    # 8081"')

    args = '/home/pi/shell'
    logging.debug(args)
    rtmpprocess = subprocess.Popen(["/home/pi/mjpg-streamer/mjpg-streamer.sh start"], shell=True)
    return rtmpprocess


class RunCmd(threading.Thread):

    def __init__(self, cmd, timeout):
        threading.Thread.__init__(self)
        self.cmd = cmd
        self.timeout = timeout

    def run(self):
        self.p = subprocess.Popen(self.cmd)
        self.p.wait()

    def Run(self):
        self.start()
        self.join(self.timeout)

    def stop(self):
        if self.is_alive():
            self.p.terminate()  # use self.p.kill() if process needs a kill -9
            self.join()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    #  rtmp()
    RunCmd(["/home/pi/mjpg-streamer/mjpg-streamer.sh start"], 60).Run()
    time.sleep(60)
    RunCmd(["/home/pi/mjpg-streamer/mjpg-streamer.sh stop"], 60).Run()
    RunCmd.stop()
