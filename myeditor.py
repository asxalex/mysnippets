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
import os

def mywrap(text, width):
    res = []
    length = int(len(text) / width)
    for i in range(length):
        res.append(text[i*width: (i+1)*width])
    res.append(text[length*width:])
    return res

#logger = log.Logger("texteditor").getlogger()
logger = log.Logger("texteditor")
logger.setLevel("debug")
logger = logger.getlogger()

_NORMAL_MODE = 0
_INSERT_MODE = 1

_MODE = {_NORMAL_MODE: "normal", _INSERT_MODE: "insert"}

class Editor(BaseWindow):

## insert the Printable char under _INSERT_MODE    
    def insertPrintableChar(self, ch):
        ch = chr(ch)
        line, position = self.getLogicLineFromCursor()
        before = self.text[line][:position]
        after = self.text[line][position:]
        self.text[line] = before + ch + after
        #self.moveRight()
        if after == '':
            y, x = self.cursor
            if y == self.textbottom:
                self.first += 1
                self.last += 1
            self.moveRight(newline=True)
        else:
            self.moveRight()

## insert the unPrintable char under _INSERT_MODE
    def insertUnPrintableChar(self, ch):
        line, position = self.getLogicLineFromCursor()
        ## the ESC
        if ch == 27:
            self.mode = _NORMAL_MODE
            self.moveLeft()
            return
        ## the enter char
        elif ch == 10:
            if position == len(self.text[line]):
                self.text.insert(line+1, "")
            else:
                before = self.text[line][:position]
                after = self.text[line][position:]
                self.text[line] = before
                self.text.insert(line+1, after)

            if self.cursor[0] == self.textbottom:
                self.first += 1
                self.last += 1
                self.cursor = (self.cursor[0], 0)
            else:
                self.cursor = (self.cursor[0] + 1, 0)
        ## the DEL(backspace) key
        elif ch == 127:
            if position == 0:
                if line == 0:
                    return

                y, x = self.cursor
                if self.cursor[0] == self.box:
                    self.first -= 1
                    self.last -= 1
                    y += 1

                temp = self.text.pop(line)
                y = y-1
                x = len(self.text[line-1])
                self.cursor = (y, x)
                self.text[line-1] += temp
                return
            before = self.text[line][:position-1]
            after = self.text[line][position:]
            self.text[line] = before + after
            self.moveLeft()

    def __init__(self, begin_x, begin_y, height, width, mainwindow=None, main=False, box=False):
        self.width = width
        self.height = height
        
        super(Editor, self).__init__(begin_x, begin_y, height, width, mainwindow, main)

        ## filename and box
        self.filename = None
        self.box = 1 if box else 0

        #line width
        self.linenowidth = 3
        ## indicating if the changes of the texts are saved
        self.clear = True

        # for line no and the space
        # and create the subwindow
        self.subwidth = self.width-self.linenowidth - 1 - self.box
        self.subwin = self.window.subwin(self.height-1, self.subwidth, begin_y, begin_x+4+self.box)

        # status line
        self.statusLine = self.height- 1 - self.box

        #mode
        self.mode = _NORMAL_MODE
        #replace
        self.replace = True

        self.text = [""]
        self.textLines = [0 for i in self.text]

        ## textup and textbottom is used to show the upper bound
        ## and bottom bound of the text area
        self.textup = self.box
        self.textbottom = self.height - 2 - 2 * self.box

        # first is used to indicating the first line no during the self.text
        self.first = 0
        self.last = min([self.height-1, len(self.text)])
        self.cursor = (self.box,0)

        # determine if the editor is exiting...
        self.exit = False

        logger.debug("__init__ ends")

    def openFile(self, filename):
        self.filename = filename
        if os.path.isfile(filename):
            fp = open(filename)
            temp = fp.read()
            self.text = temp.splitlines() or [""]
        else:
            fp = open(filename, "w")
            self.text = [""]
        self.textLines = [0 for i in self.text]
        fp.close()

        #try:
        #    fp = open(filename)
        #    temp = fp.read()
        #    self.text = temp.splitlines()
        #    fp.close()
        #    self.filename = filename
        #except:
        #    pass

    def loop(self):
        self.redraw()
        while True:
            a = self.subwin.getch()
            logger.error("a is %s" % a)
            if self.mode == _NORMAL_MODE:
                self.normalCommand(a)
            elif self.mode == _INSERT_MODE:
                self.insertCommand(a)
            if self.exit is True:
                break
        return '\n'.join(self.text)

    def save(self):
        if self.filename is None:
            return False
        fp = open(self.filename, "w")
        fp.write('\n'.join(self.text))
        fp.close()
        return True

## put the cursor to Left, Right, Up, Down, etc.
## and put the cursor accordingly, not to exceed the EOL
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

    def moveRight(self, step=1, newline=False):
        y, x = self.cursor
        if x < self.subwidth-1 or newline is True:
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

    ## called while get the user input
    ## under the normal mode
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

    ## execute the NORMAL MODE command after the ":"
    def handleCommand(self):
        self.display_raw(" "*self.subwidth, 0,self.statusLine)
        a = self.get_param(self.statusLine,0, ":").decode()
        if a == "wq":
            if self.save():
                self.clear = True
            else:
                self.displayStatusCommand("not in a file")
                return
            self.exit = True
        elif a == "w":
            if self.save():
                self.clear = True
            else:
                self.displayStatusCommand("not in a file")
        elif a == "q!":
            self.exit = True
        elif a == "q":
            if self.clear:
                self.exit = True
            else:
                self.displayStatusCommand("file changed but not saved")
        elif a.startswith("!"):
            pass
        elif a.startswith("open"):
            temp = a.split(" ")
            if len(temp) == 2 and temp[1] != '':
                filename = temp[1]
                self.openFile(filename)
            else:
                self.displayStatusCommand("filename is not specified")
        else:
            self.displayStatusCommand("unknown command, press <enter> to return")

    ## called while get the user input
    ## under the insert mode
    def insertCommand(self, key):
        logger.debug("[insert mode]" + str(chr(key)))
        self.clear = False
        if key > 31 and key < 127:
            self.insertPrintableChar(key)
        else:
            self.insertUnPrintableChar(key)
        self.redraw()


    ## convert the cursor into the text index,
    ## including the line and position
    def getLogicLineFromCursor(self):
        y, x = self.cursor
        accu = 0; l = 0;
        line = self.first
        tempy = y + (1-self.box)
        for i in range(self.first, len(self.textLines)):
            line = i
            l = self.textLines[i]
            accu += l
            if accu >= tempy:
                break
        position = (l - (accu - tempy) - 1) * self.subwidth + x
        logger.debug("convert cursor(y=%d, x=%d) to Logic cursor(y=%d, x=%d)" % (y, x, line, position))
        return line, position
        
    ## convert the Logic Cursor(line , position)
    ## to the cursor in the screen (y, x)
    def getCursorFromLogicCursor(self, line, width):
        y = self.box
        for i in range(self.first, line):
            y += self.textLines[i]
        x = width % self.subwidth
        y += int(width / self.subwidth)
        logger.debug("convert Logic cursor(y=%d, x=%d) to cursor(y=%d, x=%d)" % (line, width, y, x))
        return y, x

    ####### draw lines
    def drawStatusLine(self, line, startx):
        logger.debug("draw Status Line starts")
        self.window.addstr(self.statusLine,startx, line)

    def drawLineNo(self, lineno, starty):
        self.window.addstr(starty, self.box, (("%%%ds"%self.linenowidth)%str(lineno)))

    def drawOneLine(self, lineno, line, startx, starty):
        width = self.subwidth - startx
        #text = textwrap.wrap(line, width) or [""]
        text = mywrap(line, width) or [""]
        
        endless = False
        self.drawLineNo(lineno, starty)
        for i in range(len(text)):
            if starty+i <= self.textbottom:
                self.subwin.addstr(starty+i,startx, text[i])
            else:
                endless = True
        self.textLines[lineno-1] = len(text)
        return starty + len(text), endless

    def redraw(self):
        self.window.clear()

        startx = 0
        starty = self.textup
        end = False
        ## get textLines every time redrawed
        ## in case of the line change
        self.textLines = [0 for i in self.text]

        i = self.first
        ## draw line by line
        while starty <= self.textbottom:
            if i >= len(self.text):
                self.drawLineNo("~", starty)
                starty += 1
                continue
            starty, endless = self.drawOneLine(i+1, self.text[i], startx, starty)
            i += 1
            end = end or endless
        y, x = self.getLogicLineFromCursor()

        ## draw status line
        self.drawStatusLine("--%s--  %d %d" % (_MODE[self.mode], y+1, x+1), 3)

        ## put cursor
        self.window.refresh()
        self.subwin.move(*self.cursor)

        self.last = i-1
        if end:
            self.last -= 1

    ## put cursor in the end of the line
    def putCursor(self):
        y, x = self.cursor
        line, pos = self.getLogicLineFromCursor()

        if pos > len(self.text[line])-1:
            if self.mode == _NORMAL_MODE and len(self.text[line]) != 0:
                pos = len(self.text[line]) - 1
            else:
                pos = len(self.text[line])
            self.cursor = self.getCursorFromLogicCursor(line, pos)


if __name__ == "__main__":
    def set_win():
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.noecho()
        curses.cbreak()

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
