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


def rectangle(win, begin_y, begin_x, height, width, attr=curses.A_BOLD, focused=False, string=None):
    if focused:
        attr = curses.A_BOLD | curses.A_STANDOUT
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

class YesNoDialog(Dialog):
    def __init__(self, width=50, height=20, mainwindow=None):
        super(YesNoDialog, self).__init__(width, height, mainwindow)

    def promptYesOrNo(self, text):
        self.setChoices({"Yes": False, "No": True, "not sure": True})
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
