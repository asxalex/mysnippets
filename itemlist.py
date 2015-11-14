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
from log import Logger

logger = Logger("itemlist")
logger.setLevel("debug")
logger = logger.getlogger()


class ItemList(Widget):
    def __init__(self, begin_x=0, begin_y=0, height=10, width=10, selected_colorpair=2, normal_colorpair=1, mainwindow=None):
        logger.debug("f")
        super(ItemList, self).__init__(begin_x, begin_y, height, width, mainwindow)
        logger.debug("e")
        self.selected = selected_colorpair
        self.normal = normal_colorpair
        self.index = 0;
        self.items = []
        self.trigger = {"j": "down", "k": "up", "q": "quit"}
        self.myevent = {"down": self.nextItem, "up": self.prevItem, "quit": self.quit}
        logger.debug("d")

        self.first = 1
        _, self.last = self.rightbottom
        self.last -= 2

        self.prompt = "=>"

        logger.debug("c")

        self.window.setscrreg(self.first+1, self.last)

    def quit(self, *args, **kwargs):
        return False
        
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
        self.window.clear()
        self.window.box()
        _, width = self.window.getmaxyx()

        first = self.first - 1
        itemlength = len(self.items)
        last = self.last if itemlength > self.last else itemlength
        logger.debug("first is " + str(first))
        logger.debug("last is " + str(last))
        for i in range(first, last):
            region_index = i - first + 1
            content = self.items[i]
            logger.debug(str(i) + str(content))
            if i == self.index:
                content = content[:width-3-len(self.prompt) - 1]
                temp = content + ' ' * (width-3-len(content)-3) + self.prompt
                self.display_info(temp, 1,region_index, self.selected)
            else:
                content = content[:width-3]
                self.display_info(content, 1,region_index, self.normal)

        logger.debug("self.items are "+ str(self.items))

        self.window.refresh()

    def addItem(self, itemStr):
        self.items.append(itemStr)
        self.redraw()

    def delItem(self):
        index = self.index
        if self.index == len(self.items) - 1:
            self.index -= 1
        self.items.pop(index)
        self.redraw()

    def setItem(self, itemStrList):
        self.items = itemStrList
        self.redraw()

if __name__ == "__main__":
    from misc import set_win, unset_win
    from base import BaseWindow

    try:
        main = BaseWindow(main=True)
        y, x = main.getWindow().getmaxyx()
        set_win()
        width = 20
        logger.debug("a")
        itemlist = ItemList(0,0, mainwindow=main)
        logger.debug("b")
        itemlist.getWindow().box()
        itemlist.setItem([a for a in "abcdefghijklmno"])
        itemlist.addItem("abcdefghijklmnopqrstuvwxyz")
        itemlist.loop()
    except Exception as e:
        print(type(e), e)
    finally:
        unset_win()
