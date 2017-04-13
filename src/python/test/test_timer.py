#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2017-01-24 18:12:26

from package.timer import PercentTimer
import time
import logging

timer = PercentTimer(20)


def Timer_start():
    timer.start()


def Timer_setTotal():
    timer.total_time = 100
    assert timer.total_time is not 0


def Timer_getPercent():
    assert timer.getPercent() is not 0


def test_Timer():
    logging.basicConfig(level=logging.DEBUG)
    Timer_setTotal()
    Timer_start()
    Timer_getPercent()

    for i in range(1, 10):
        print((timer.getPercent()))
        time.sleep(2)

    Timer_getPercent()


if __name__ == "__main__":
    test_Timer()
