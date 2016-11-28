#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2016-09-19 16:03:49

import socket
import sys
import logging
import os
import signal
import time
from package.debug import PrintException
from package.send import receive_file
from package.c_printer_status import C_printer_status


def main(Host):
    C_printer_status(Host)
    return True


if __name__ == "__main__":
    main("172.17.135.190")
