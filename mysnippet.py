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
from curses import textpad
import sqlite3

from base import BaseWindow
from itemlist import ItemList
from dialog import YesNoDialog, ProcessDialog, InputDialog

import editor

class MyItemList(ItemList):
    def __init__(self, begin_x=0, begin_y=0, height=10, width=10, selected=2, normal=1, mainwin=None):
        super(MyItemList, self).__init__(begin_x, begin_y, height, width, selected, normal, mainwin)

        self.addTrigger("q", "quit")
        self.connect("quit", self.quit)

        self.addTrigger("l", "goleft")
        self.connect("goleft", self.goLeft)

        self.addTrigger("n", "new")
        self.connect("new", self.newSnippet)

        self.addTrigger("p", "process")
        self.connect("process", self.processbar)

        self.addTrigger("i", "input")
        self.connect("input", self.inputdia)
        
        self.conn = sqlite3.connect("./snippet.db")

        cursor = self.conn.cursor()
        cursor.execute("select id, title from snippet;")

        titles = cursor.fetchall()
        self.results = [[i[0], i[1]] for i in titles]
        
        testitem = "abcdefghijklmnopqrstuvwxyzabcdefghi"
        #self.setItem([res[1] for res in self.results])

        self.setItem([a for a in testitem])

        cursor.close()
        self.back = False

    def quit(self, *args):
        dialog = YesNoDialog(mainwindow=self.main_WIN)
        a = dialog.promptYesOrNo("sure to quit?")
        dialog.clear()
        self.redraw()
        #print(a)
        return a

    def processbar(self, *args):
        process = ProcessDialog(mainwindow=self.main_WIN)
        a = process.showProcessBar("the process is")
        process.clear()
        self.redraw()
        return True

    def inputdia(self, *args):
        inputdialog = InputDialog(mainwindow=self.main_WIN)
        result = inputdialog.showInput(["name", "age", "gender", "hello", "world"], "fill the info:")
        inputdialog.clear()
        self.redraw()
        return True


    def goLeft(self, win):
        index = self.index
        iid = self.results[index][0]
        cursor = self.conn.cursor()
        cursor.execute("select content from snippet where id = ?;", (iid,))
        
        content = cursor.fetchone()[0]
        cursor.close()

        (x1, y1) = win.leftup
        (x2, y2) = win.rightbottom
        #edit = editor.Editor(win.getWindow(), win_location=(y1, x1), win_size=(y2-y1, x2-x1))
        edit = editor.Editor(win.getWindow(), win_location=(y1, x1), win_size=(y2-y1, x2-x1))
        #pad.stripspaces = 0
        #cursor = self.conn.cursor()
        #sql = "update snippet set content=? where id=?;"
        #cursor.execute(sql, (res, iid))
        #self.conn.commit()
        print(edit)

    def newSnippet(self, whatever):
        win = BaseWindow()
        

def set_win():
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.noecho()
    curses.cbreak()

    #subwin = curses.newwin(1,1,5,5)
    #subwin.box(10)
    #subwin.refresh()
    #display_info("here", 12,12, 0, subwin)

def unset_win():
    curses.nocbreak()
    curses.echo()
    curses.endwin()

def get_param(prompt_string, x=2, y=2, win=None):
    global myscreen
    if win is None:
        win = myscreen
    win.clear()
    win.box()
    win.addstr(y, x, prompt_string)
    win.refresh()
    win.nodelay(0)
    curses.echo()
    input = win.getstr(10, 10, 60)
    curses.noecho()
    win.nodelay(1)
    return input

if __name__ == "__main__":
    try:
        main = BaseWindow(main=True)
        y, x = main.getWindow().getmaxyx()
        set_win()
        width = 20
        edit = BaseWindow(width+1,0, y,x-(width+1))

        itemlist = MyItemList(0, 0, y,width, mainwin = main)
        itemlist.getWindow().box()
        itemlist.redraw()
        itemlist.loop(edit)

    except Exception as e:
        print(type(e))
        print(e)
    finally:
        unset_win()

