#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2017-04-13 17:20:48


from package.environment_config import UseConfigs


def test_main():
    controller = UseConfigs()
    controller.make_config()
    controller.load_config()
    controller.print_config()
    controller.modify_config()
