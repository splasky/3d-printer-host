#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2016-09-13 13:47:31

import sys


def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, exc_type, exc_obj))
