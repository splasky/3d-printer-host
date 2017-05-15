#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2016-09-19 16:16:12

import socket
import sys
import logging
import os
import signal
import time
from package.send import send_file
from package.da import create_json_file
from package.debug import PrintException
from package.s_printer_status import S_printer_status


def main(p, Host, Port):
    S_printer_status(p, Host, Port)
    return True


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main(None, '', 6666)
