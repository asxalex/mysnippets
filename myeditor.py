#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 alex <alex@alex>
#
# Distributed under terms of the MIT license.

"""

"""

from base import BaseWindow
import textwrap
import curses
import log
import sys

def mywrap(text, width):
    res = []
    length = int(len(text) / width)
    for i in range(length):
        res.append(text[i*width: (i+1)*width])
    res.append(text[length*width:])
    return res

logger = log.Logger("texteditor").getlogger()

_NORMAL_MODE = 0
_INSERT_MODE = 1

_MODE = {_NORMAL_MODE: "normal", _INSERT_MODE: "insert"}

class Editor(BaseWindow):

    
    def insertPrintableChar(self, ch):
        ch = chr(ch)

        line, position = self.getLogicLineFromCursor()
        #logger.debug("line is %d and position is %d" % (line, position))
        
        before = self.text[line][:position]
        after = self.text[line][position:]
        self.text[line] = before + ch + after
        self.moveRight()

    def insertUnPrintableChar(self, ch):
        line, position = self.getLogicLineFromCursor()
        if ch == 27:
            self.mode = _NORMAL_MODE
            self.moveLeft()
            return
        elif ch == 10:
            before = self.text[line][:position]
            after = self.text[line][position:]
            self.text[line] = before
            self.text.insert(line+1, after)
            #self.cursor = self.getCursorFromLogicCursor(line+1, 0)
            #self.moveDown()
            self.cursor = (self.cursor[0] + 1, 0)
            #self.cursor = self.getCursorFromLogicCursor(line+1, 0)
            #logger.error("(%d, %d)" % (self.cursor[0], self.cursor[1]))
        elif ch == 127:
            if position == 0:
                return
            before = self.text[line][:position-1]
            after = self.text[line][position:]
            self.text[line] = before + after
            self.moveLeft()
            

    def __init__(self, begin_x, begin_y, height, width, mainwindow=None, main=False, box=False):
        self.width = width
        self.height = height
        
        super(Editor, self).__init__(begin_x, begin_y, height, width, mainwindow, main)

        logger.debug("2")
        self.filename = None
        self.box = 1 if box else 0

        #line width
        self.linenowidth = 3
        self.clear = True

        # for line no and the space
        self.subwidth = self.width-self.linenowidth - 1 - self.box

        self.subwin = self.window.subwin(self.height-1, self.subwidth, begin_y, begin_x+4+self.box)
        self.subwin.box()

        self.statusLine = self.height- 1 - self.box

        logger.debug("3")
        self.first = 0


        self.cursor = (self.box,0)

        #mode
        self.mode = _NORMAL_MODE
        
        #replace
        self.replace = True

        self.text = [""]
        self.textLines = [0 for i in self.text]

        self.textup = self.box
        self.textbottom = self.height - 2 - 2 * self.box

        self.last = min([self.height-1, len(self.text)])

    def openFile(self, filename):
        self.filename = filename
        fp = open(filename)
        self.text = fp.readlines()

    def loop(self):
        self.redraw()
        while True:
            a = self.subwin.getch()
            logger.error("a is %s" % a)
            if self.mode == _NORMAL_MODE:
                self.normalCommand(a)
            elif self.mode == _INSERT_MODE:
                self.insertCommand(a)

    def save(self):
        if self.filename is None:
            return False
        fp = open(self.filename, "w")
        fp.write('\n'.join(self.text))
        fp.close()
        return True

    def moveDown(self, step=1):
        y, x = self.cursor
        y += 1
        if y >= self.textbottom:
            if self.last < len(self.text) - 1:
                self.first += 1
            y -= 1
        self.cursor = (y, x)
        self.putCursor()

    def moveUp(self, step=1):
        y, x = self.cursor
        y -= 1
        if y < self.textup:
            if self.first > 0:
                self.first -= 1
            y += 1
        self.cursor = (y, x)
        self.putCursor()

    def moveLeft(self, step=1):
        y, x = self.cursor
        x -= 1
        if x < 0:
            tempy = y + (1-self.box)
            accu = 0
            l = 0
            for i in range(self.first, len(self.textLines)):
                l = self.textLines[i]
                accu += l
                if accu >= tempy:
                    accu -= l
                    break
            if accu+1 != tempy:
                y = y - 1
                x = self.subwidth - 1
            else:
                x = 0

        self.cursor = (y, x)
        self.putCursor()

    def moveTop(self, step=1):
        y, x = self.getLogicLineFromCursor()
        x = 0
        self.cursor = self.getCursorFromLogicCursor(y, x)
        self.putCursor()

    def moveEnd(self, step=1):
        y, x = self.getLogicLineFromCursor()
        x = len(self.text[y])
        self.cursor = self.getCursorFromLogicCursor(y, x)
        self.putCursor()

    def moveRight(self, step=1):
        y, x = self.cursor
        if x < self.subwidth-1:
            x += 1
        else:
            accu = 0
            l = 0
            tempy = y + (1-self.box)
            for i in range(self.first, len(self.textLines)):
                l = self.textLines[i]
                accu += l
                if accu >= tempy:
                    break
            if accu != tempy:
                y = y+1
                x = 0
        self.cursor = (y, x)
        self.putCursor()

    def normalCommand(self, key):
        logger.critical("key is %s, KEY_DOWN is %s" % (key, curses.KEY_DOWN))
        y, x = self.cursor
        bottom = self.first + self.height - 1 - self.box
        if key == ord('l') or key == curses.KEY_RIGHT:
            self.moveRight()
        elif key == ord('h') or key == curses.KEY_LEFT:
            self.moveLeft()
        elif key == ord('j') or key == curses.KEY_DOWN:
            self.moveDown()
        elif key == ord('k') or key == curses.KEY_UP:
            self.moveUp()
        elif key == ord("i"):
            self.mode = _INSERT_MODE
        elif key == ord("a"):
            self.mode = _INSERT_MODE
            self.moveRight()
        elif key == ord("A"):
            self.mode = _INSERT_MODE
            self.moveEnd()
        elif key == ord("I"):
            self.mode = _INSERT_MODE
            self.moveTop()
        elif key == ord(":"):
            self.handleCommand()
        self.redraw()

    def displayStatusCommand(self, msg):
        self.display_raw(" "*self.subwidth, 0, self.statusLine)
        self.display_raw(msg, 0, self.statusLine)
        self.get_ch()

    def handleCommand(self):
        self.display_raw(" "*self.subwidth, 0,self.statusLine)
        a = self.get_param(self.statusLine,0, ":").decode()
        logger.error("++++in command line, a=%s" % a)
        if a == "wq":
            if self.save():
                self.clear = True
            else:
                self.displayStatusCommand("not in a file")
                return
            sys.exit(0)
        elif a == "w":
            if self.save():
                self.clear = True
            else:
                self.displayStatusCommand("not in a file")
        elif a == "q!":
            sys.exit(0)
        elif a == "q":
            if self.clear:
                sys.exit(0)
            else:
                self.displayStatusCommand("file changed but not saved")
        else:
            self.displayStatusCommand("unknown command, press <enter> to return")

    def insertCommand(self, key):
        logger.debug("[insert mode]" + str(chr(key)))
        self.clear = False
        if key > 31 and key < 127:
            self.insertPrintableChar(key)
        else:
            self.insertUnPrintableChar(key)
        self.redraw()

    def drawLineNo(self, lineno, starty):
        self.window.addstr(starty, self.box, (("%%%ds"%self.linenowidth)%str(lineno)))

    def drawStatusLine(self, line, startx):
        logger.debug("draw Status Line")
        self.window.addstr(self.statusLine,startx, line)
        #pass

    def drawOneLine(self, lineno, line, startx, starty):
        width = self.subwidth - startx
        #text = textwrap.wrap(line, width) or [""]
        text = mywrap(line, width) or [""]
        
        endless = False
        self.drawLineNo(lineno, starty)
        for i in range(len(text)):
            if starty+i < self.textbottom:
                self.subwin.addstr(starty+i,startx, text[i])
            else:
                endless = True
        self.textLines[lineno-1] = len(text)
        return starty + len(text), endless

    def getLogicLineFromCursor(self):
        y, x = self.cursor

        accu = 0; l = 0;
        line = self.first
        tempy = y + (1-self.box)
        for i in range(self.first, len(self.textLines)):
            line = i
            l = self.textLines[i]
            accu += l
            logger.debug("l = %d and accu = %d" % (l, accu))
            logger.debug("line = %d" % (line,))
            if accu >= tempy:
                break
        position = (l - (accu - tempy) - 1) * self.subwidth + x
        #logger.error("l=%d, accu=%d, tempy=%d, subwidth=%d, line=%d, position=%d" % (l, accu, tempy, self.subwidth, line, position))
        #logger.error("line=%d, position=%d" % (line, position))
        return line, position
        


    def redraw(self):
        self.subwin.clear()
        self.window.clear()

        startx = 0
        starty = self.textup
        i = self.first
        end = False
        logger.debug("4")
        self.textLines = [0 for i in self.text]
        while starty <= self.textbottom:
            if i >= len(self.text):
                self.drawLineNo("~", starty)
                starty += 1
                continue
            starty, endless = self.drawOneLine(i+1, self.text[i], startx, starty)
            i += 1
            end = end or endless
        y, x = self.getLogicLineFromCursor()
        self.drawStatusLine("--%s--  %d %d" % (_MODE[self.mode], y+1, x), 3)
        logger.debug("5")
        self.window.refresh()
        self.subwin.move(*self.cursor)
        self.subwin.refresh()

        self.last = i-1
        if end:
            self.last -= 1
        #logger.debug("redraw finished")

    def getCursorFromLogicCursor(self, line, width):
        y = self.box
        for i in range(self.first, line):
            y += self.textLines[i]
        x = width % self.subwidth
        y += int(width / self.subwidth)
        logger.debug("x=%d, y=%d" % (x,y))
        return y, x

    def putCursor(self):
        y, x = self.cursor
        line, pos = self.getLogicLineFromCursor()
        logger.debug("11")

        #logger.error("+++++++ line=%d, pos=%d" %(line, pos))

        if pos > len(self.text[line])-1:
            logger.debug("12")
            if self.mode == _NORMAL_MODE and len(self.text[line]) != 0:
                pos = len(self.text[line]) - 1
            else:
                pos = len(self.text[line])
            self.cursor = self.getCursorFromLogicCursor(line, pos)
        logger.debug("13")


if __name__ == "__main__":
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

    try:
        main = BaseWindow(main=True)
        y, x = main.getWindow().getmaxyx()
        set_win()
        width = 4
        edit = Editor(0,0, y,x-(width+1), box=False)
        logger.debug("in main")
        edit.loop()

    except Exception as e:
        print(type(e))
        print(e)
    finally:
        unset_win()