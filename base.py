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

class BaseWindow(object):
    def __init__(self, begin_x=0, begin_y=0, height=10, width=10, mainWindow=None, main=False):
        if main:
            self.window = curses.initscr()
        else:
            self.window = curses.newwin(height, width, begin_y, begin_x)

        self.leftup = (begin_x, begin_y)
        self.rightbottom = (begin_x+width, begin_y+height)
        self.main_WIN = mainWindow

        self.window.nodelay(1)
        self.window.keypad(1)
        #print(self.window.attr())

    def display_raw(self, string, x, y, colorpair=1):
        self.window.addstr(y, x, string, curses.color_pair(colorpair))
        self.window.refresh()

    def display_info(self, string, x=-1, y=-1, colorpair=1, padding=0):
        if x != -1 or y != -1:
            self.window.addstr(y, x, string, curses.color_pair(colorpair))
            self.window.refresh()
            return
        (x1, y1) = self.leftup
        (x2, y2) = self.rightbottom
        width = x2 - x1 - 2
        height = y2 - y1 - 1
        height -= padding
        length = len(string)
        if length > width * height:
            x = y = 0
            self.window.addstr(y, x, string, curses.color_pair(colorpair))
        elif length < width:
            y = int(height / 2)
            x = int((width-length)/2)
            self.window.addstr(y, x, string, curses.color_pair(colorpair))
        else:
            lines = int(length / width) + 1
            x = 1
            y = int((height-lines)/2)
            for i in range(lines):
                self.window.addstr(y, x, string[i*width: (i+1)*width], curses.color_pair(colorpair))
                y += 1

        self.window.refresh()

    def get_param(self, y=2, x=2, prompt_string=None, prompt=True, length=20):
        l = 0
        if prompt_string is not None:
            self.window.addstr(y, x, prompt_string)
            self.window.move(y, x)
            self.window.refresh()
            l = len(prompt_string)
        self.window.nodelay(0)
        if prompt:
            curses.echo()
        input = self.window.getstr(y, x+l, length)
        curses.noecho()
        self.window.nodelay(1)
        return input

    def get_ch(self):
        self.window.nodelay(0)
        ch = self.window.getch()
        self.window.nodelay(1)
        return ch

    def getWindow(self):
        return self.window

    def clear(self):
        self.window.clear()
        self.window.refresh()

