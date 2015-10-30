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


class ItemList(Widget):
    def __init__(self, begin_x=0, begin_y=0, height=10, width=10, selected_colorpair=2, normal_colorpair=1, mainwindow=None):
        super(ItemList, self).__init__(begin_x, begin_y, height, width, mainwindow)
        self.selected = selected_colorpair
        self.normal = normal_colorpair
        self.index = 0;
        self.items = []
        self.trigger = {"j": "down", "k": "up"}
        self.myevent = {"down": self.nextItem, "up": self.prevItem}
        
    def nextItem(self, *args, **kwargs):
        if self.index == len(self.items) - 1:
            return
        self.index += 1
        self.redraw()

    def prevItem(self, *args, **kwargs):
        if self.index == 0:
            return
        self.index -= 1
        self.redraw()

    def redraw(self):
        self.window.clear()
        self.window.box()
        _, width = self.window.getmaxyx()
        for i in range(len(self.items)):
            content = self.items[i]
            temp = content + ' ' * (width-3-len(content)-3) + '=>'
            if i == self.index:
                self.display_info(temp, 1,i+1, self.selected)
            else:
                self.display_info(self.items[i], 1,i+1, self.normal)

        self.window.refresh()

    def addItem(self, itemStr):
        self.items.append(itemStr)
        self.redraw()

    def setItem(self, itemStrList):
        self.items = itemStrList
        self.redraw()

