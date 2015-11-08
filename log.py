#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 alex <alex@alex>
#
# Distributed under terms of the MIT license.

"""

"""
import logging

_LOGGERS = []

_LEVEL_MAP = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
        }
class Logger(object):
    def __init__(self, name, filename=None):
        logger = logging.getLogger(name)
        self.logger = logger
        if logger in _LOGGERS:
            return
        
        _LOGGERS.append(logger)
        if filename is None:
            filename = name + ".log"
        formatter = logging.Formatter('%(name)-12s %(funcName)s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',) 
        filehandler = logging.FileHandler(filename)
        filehandler.setFormatter(formatter)
        self.logger.addHandler(filehandler)
        self.logger.setLevel(logging.INFO)

    def setLevel(self, level):
        a = _LEVEL_MAP.get(level, logging.DEBUG)
        self.logger.setLevel(a)
        
    def getlogger(self):
        return self.logger

if __name__ == "__main__":
    log = Logger("test")
    log.getlogger().error("error1")

    log2 = Logger("test")
    log2.getlogger().error("error2")
