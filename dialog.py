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
from widget import Widget
import random
import time
from collections import OrderedDict

import logging


def rectangle(win, begin_y, begin_x, height, width, attr=curses.A_BOLD, focused=False, string=None, withline=True):
    if focused:
        attr = curses.A_BOLD | curses.A_STANDOUT
    if withline:
        win.vline(begin_y,    begin_x,       curses.ACS_VLINE, height, attr)
        win.hline(begin_y,        begin_x,   curses.ACS_HLINE, width , attr)
        win.hline(height+begin_y, begin_x,   curses.ACS_HLINE, width , attr)
        win.vline(begin_y,    begin_x+width, curses.ACS_VLINE, height, attr)
        win.addch(begin_y,        begin_x,       curses.ACS_ULCORNER,  attr)
        win.addch(begin_y,        begin_x+width, curses.ACS_URCORNER,  attr)
        win.addch(height+begin_y, begin_x,       curses.ACS_LLCORNER,  attr)
        win.addch(begin_y+height, begin_x+width, curses.ACS_LRCORNER,  attr)
    if string is not None:
        temp = int((width - len(string))/2) * ' ' + string
        temp += (width - len(temp) - 1) * ' '
        win.addstr(begin_y+int(height/2), begin_x+1, temp, attr)
    win.refresh( )

class Dialog(Widget):
    def __init__(self, width, height, mainwindow=None):
        self.height = height
        self.width = width
        if mainwindow is not None:
            y, x = mainwindow.getWindow().getmaxyx()
            y = int(y/2 - height/2)
            x = int(x/2 - width/2)
        else:
            x = y = 0
        super(Dialog, self).__init__(x, y, height, width, mainwindow)
        self.window.box()
        self.choices = {}
        self.focus = 0
        self.sure = False

    def setChoices(self, choices = {"Yes": True, "No": False}):
        self.choices = choices

    def left_or_right(self):
        self.window.refresh()
        while True:
            key = chr(self.get_ch())
            if key == 'h' and self.focus != 0: # left
                self.focus -= 1
                break
            elif key == 'l' and self.focus != len(self.choices)-1: # right
                self.focus += 1
                break
            elif key == '\n':
                self.sure = True
                break
            else:
                continue

    def downward(self, y, x):
        self.window.refresh()
        res = self.get_param(y, x)
        if type(self.sure) == int:
            self.sure += 1
        self.focus += 1
        return res.decode()

class ProcessDialog(Dialog):
    def __init__(self, width=50, height=20, mainwindow=None):
        super(ProcessDialog, self).__init__(width, height, mainwindow)

    def showProcessBar(self, text, length = 40):
        (x1, y1) = self.leftup
        (x2, y2) = self.rightbottom

        self.display_info(text, padding=5)
        self.choices = ' ' * length
        while self.sure is not True:
            rectangle(self.window, y2-y1-5, 5, 2, length+2, string='▋'*self.focus+ ' '*(40-self.focus))
            #self.left_or_right()
            self.processing()

    def processing(self):
        a = random.randint(100,1000)
        time.sleep(a/1000)
        if self.focus <= len(self.choices) - 1:
            self.focus += 1
        else:
            self.sure = True

class InputDialog(Dialog):
    def __init__(self, width=50, height=20, mainwindow=None):
        super(InputDialog, self).__init__(width, height, mainwindow)

    def showInput(self, items, text=None):
        # the items param is a map
        # the key of the map is shown
        # and the value of the map is the result's key

        # the items param can also be a list
        # which means that the key and value are the same
        if type(items) == type([]):
            item = OrderedDict()
            for i in items:
                item[i] = i
            items = item

        self.setChoices(items)
        length = len(self.choices)
        padding = length * 3
        if text is not None:
            self.display_info(text, padding = padding)
        self.keys = list(self.choices.keys())

        results = {k: "" for k in list(self.choices.values())}

        (x1, y1) = self.leftup
        (x2, y2) = self.rightbottom

        self.sure = 0
        while(self.sure != len(self.choices)):
            for i in range(len(self.keys)):
                if i == self.focus:
                    focused = True
                else:
                    focused = False
                key = self.keys[i]
                w = x2 - x1 - 10
                content = key + ": " + str(results[key])
                content += ' ' * (w - len(content))
                rectangle(self.window, y2-y1-padding+3*i, 5, 2, w, focused=focused, string=content, withline=False)
            f = self.focus
            results[self.keys[f]] = self.downward(y2-y1-padding+3*f+1, 5+len(self.keys[f])+2)
        return results
        
class YesNoDialog(Dialog):
    def __init__(self, width=50, height=10, mainwindow=None):
        if mainwindow is not None:
            maxy, maxx = mainwindow.getWindow().getmaxyx()
            if width > maxx:
                width = maxx
            if height > maxy:
                height = maxy
        super(YesNoDialog, self).__init__(width, height, mainwindow)

    def promptYesOrNo(self, text, choices=None):
        if choices is None:
            choices = OrderedDict()
            choices["No"] = True
            choices["Yes"] = False
        self.setChoices(choices)
        self.display_info(text, padding=5)

        (x1, y1) = self.leftup
        (x2, y2) = self.rightbottom

        self.keys = list(self.choices.keys())
        length = max([len(i) for i in self.keys]) + 2
        itemNumbers = len(self.keys) - 1
        leftspace = int(((x2 - x1) - 10 - length * len(self.keys)) / itemNumbers)
        self.window.refresh()

        while self.sure is not True:
            for i in range(len(self.keys)):
                if i == self.focus:
                    focused = True
                else:
                    focused = False
                rectangle(self.window, y2-y1-5, i*(length+leftspace)+5, 2, length, focused=focused, string=self.keys[i])

            self.left_or_right()

        return self.choices[self.keys[self.focus]]
