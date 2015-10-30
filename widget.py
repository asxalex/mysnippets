#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 alex <alex@alex>
#
# Distributed under terms of the MIT license.

"""

"""

import curses
from base import BaseWindow

class Widget(BaseWindow):
    def __init__(self, begin_x=0, begin_y=0, height=10, width=10, mainwindow=None):
        super(Widget, self).__init__(begin_x, begin_y, height, width, mainwindow)
        self.myevent = {}     # myevent stands for the actionName and actionFunc
        self.trigger = {}   # trigger stands for the keystroke and actionName
        self.initTrigger()

    def initTrigger(self, triggerMap={}):
        self.trigger = triggerMap

    def addTrigger(self, keyStroke, actionName):
        self.trigger[keyStroke] = actionName
        
    def defaultAction(self, *argc, **argv):
        return

    ## same as addEvent
    def connect(self, actionName, actionFunc):
        self.myevent[actionName] = actionFunc

    def loop(self, *argc, **argv):
        while 1:
            try:
                a = chr(self.get_ch())
                #print("char is", a==chr(9))
                b = self.trigger.get(a, None)
                c = self.myevent.get(b, self.defaultAction)
                res = c(*argc, **argv)
                if res is False:
                    break
            except Exception as e:
                print(e)

