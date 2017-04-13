#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2017-02-13 17:37:10

import socket
import sys
import logging
import os
import signal
import time
from package.debug import PrintException
from package.send import receive_file
from package.c_printer_status import C_printer_status


def test_main(Host):
    C_printer_status(Host)
    return True


if __name__ == "__main__":
    test_main("172.17.135.190")
