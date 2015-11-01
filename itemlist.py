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

import logging

logging.basicConfig(level=logging.DEBUG,
        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
        datefmt='%a, %d %b %Y %H:%M:%S',
        filename='myapp.log',
        filemode='w')

#logger = logging.getLogger(__name__)

class ItemList(Widget):
    def __init__(self, begin_x=0, begin_y=0, height=10, width=10, selected_colorpair=2, normal_colorpair=1, mainwindow=None):
        super(ItemList, self).__init__(begin_x, begin_y, height, width, mainwindow)
        self.selected = selected_colorpair
        self.normal = normal_colorpair
        self.index = 0;
        self.items = []
        self.trigger = {"j": "down", "k": "up"}
        self.myevent = {"down": self.nextItem, "up": self.prevItem}

        self.first = 1
        _, self.last = self.rightbottom
        self.last -= 2

        self.window.setscrreg(self.first+1, self.last)
        
    def nextItem(self, *args, **kwargs):
        if self.index == len(self.items) - 1:
            return
        self.index += 1
        if self.index >= self.last:
            self.last += 1
            self.first += 1
        self.redraw()

    def prevItem(self, *args, **kwargs):
        if self.index == 0:
            return
        self.index -= 1
        if self.index < self.first - 1:
            self.last  -= 1
            self.first -= 1
        self.redraw()

    def redraw(self):
        print("here")
        self.window.clear()
        self.window.box()
        _, width = self.window.getmaxyx()

        first = self.first - 1
        itemlength = len(self.items)
        last = self.last if itemlength > self.last else itemlength
        logging.info("first is " + str(first))
        logging.info("last is " + str(last))
        #print("here ", first, " and ", last)
        for i in range(first, last):
            region_index = i - first + 1
            content = self.items[i]
            logging.error(str(i) + str(content))
            temp = content + ' ' * (width-3-len(content)-3) + '=>'
            if i == self.index:
                self.display_info(temp, 1,region_index, self.selected)
            else:
                self.display_info(self.items[i], 1,region_index, self.normal)

        logging.info("self.items are "+ str(self.items))

        self.window.refresh()

    def addItem(self, itemStr):
        self.items.append(itemStr)
        self.redraw()

    def setItem(self, itemStrList):
        self.items = itemStrList
        self.redraw()

