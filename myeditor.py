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
import math
import curses.ascii
import pyperclip

if sys.version_info.major < 3:
    def CTRL(key):
        return ord(curses.ascii.ctrl(byte(key)))
    def ASCII(key):
        return curses.ascii.ascii(byte(key))
else:
    def CTRL(key):
        return ord(curses.ascii.ctrl(key))
    def ASCII(key):
        return curses.ascii.ascii(ord(key))

#logger = log.Logger("texteditor").getlogger()
logger = log.Logger("texteditor")
logger.setLevel("info")
logger = logger.getlogger()

_COLOR_RED = 2
_COLOR_GREEN = 1
_COLOR_YELLOW = 3
_COLOR_WHITE = 4

def mywrap(text, width):
    res = []
    length = int(len(text) / width)
    for i in range(length):
        res.append(text[i*width: (i+1)*width])
    res.append(text[length*width:])
    return res

_NORMAL_MODE = 0
_INSERT_MODE = 1
_TAB_WIDTH = 400

_MODE = {_NORMAL_MODE: "normal", _INSERT_MODE: "insert"}

class Editor(BaseWindow):

    ## insert the unPrintable char under _INSERT_MODE
    def insertUnPrintableChar(self, ch):
        pass

    ## insert str under current cursor
    def insertstr(self, s=" " * _TAB_WIDTH, length=None):
        self.clear = False
        length = length if length is not None else len(s)
        line, position = self.getLogicLineFromCursor()
        before = self.text[line][:position]
        after = self.text[line][position:]
        self.text[line] = before + s + after
        self.moveRight(length)

    ## insert a "\n" char
    def nextLine(self):
        self.clear = False
        line, position = self.getLogicLineFromCursor()
        if position == len(self.text[line]):
            self.text.insert(line+1, "")
        else:
            before = self.text[line][:position]
            after = self.text[line][position:]
            self.text[line] = before
            self.text.insert(line+1, after)

        if self.cursor[0] == self.textbottom:
            self.scrollDown()
            #self.cursor = (self.cursor[0], 0)
        y, _ = self.cursor
        self.cursor = (y + 1, 0)
        self.getLineLength()



## insert the Printable char under _INSERT_MODE    
    def insertPrintableChar(self, ch, length=1):
        ch = chr(ch)
        self.insertstr(ch)

    def __init__(self, begin_x, begin_y, height, width, 
            mainwindow=None, main=False, box=False):
        self.width = width
        self.height = height
        
        super(Editor, self).__init__(begin_x, begin_y, height, width, 
                mainwindow, main)

        ## filename and box
        self.filename = None
        self.box = 1 if box else 0

        #line width
        self.linenowidth = 3
        ## indicating if the changes of the texts are saved
        self.clear = True

        # for line no and the space
        # and create the subwindow
        self.subwidth = self.width-self.linenowidth - 1 - self.box - 1
        self.subwin = self.window.subwin(self.height-1, self.subwidth+1, begin_y, begin_x+4+self.box)

        # status line
        self.statusLine = self.height- 1 - self.box
        self.needRedraw = True

        #mode
        self.mode = _NORMAL_MODE
        #replace
        self.replace = True

        self.text = [""]
        self.getLineLength()

        ## textup and textbottom is used to show the upper bound
        ## and bottom bound of the text area
        self.textup = self.box
        self.textbottom = self.height - 2 - 1 * self.box

        # first is used to indicating the first line no during the self.text
        self.last = min([self.height-1, len(self.text)])
        self.cursor = (self.box,0)

        # physical line
        self.pline = 0

        # determine if the editor is exiting...
        self.exit = False

        self.insertModeKeys = {
                CTRL("f"): self.moveRight,
                CTRL("b"): self.moveLeft,
                CTRL("n"): self.moveDown,
                CTRL("p"): self.moveUp,
                CTRL("a"): self.moveTop,
                CTRL("e"): self.moveEnd,
                CTRL("v"): self.paste,
                ASCII("\n"): self.nextLine,
                curses.ascii.DEL: self.deleteChar,
                curses.ascii.ESC: self.NormalMode,
                curses.ascii.TAB: self.insertstr,
                }

        self.normalModeKeys = {
                ASCII("h"): self.moveLeft,
                ASCII("j"): self.moveDown,
                ASCII("k"): self.moveUp,
                ASCII("l"): self.moveRight,
                ASCII("x"): self.deleteChar,
                ASCII("i"): self.InsertMode,
                ASCII("G"): self.scrollBottom,
                ASCII("B"): self.scrollBeginning,
                ASCII("D"): self.deleteLine,
                CTRL("b"): self.scrollUpScreen,
                CTRL("f"): self.scrollDownScreen,
                CTRL("u"): self.useThis,
                }

        logger.debug("__init__ ends")

    ## copy the text in the editor to clipboard
    def useThis(self):
        pyperclip.copy('\n'.join(self.text))
        self.drawStatusLine("text copied to clipboard!", 1 + self.box, _COLOR_GREEN)
        self.needRedraw = False

    ## paste the text in the clipboard to the editor
    def paste(self):
        clip = pyperclip.paste().splitlines()
        for line in clip:
            self.insertstr(line)
            self.nextLine()
        
    ## save the text to the file
    def save(self):
        if self.filename is None:
            return False
        fp = open(self.filename, "w")
        fp.write('\n'.join(self.text))
        fp.close()
        return True

    def openFile(self, filename):
        self.filename = filename
        if os.path.isfile(filename):
            fp = open(filename)
            temp = fp.read()
            self.text = temp.splitlines() or [""]
        else:
            fp = open(filename, "w")
            self.text = [""]
        self.pline = 0
        self.getLineLength()
        fp.close()

    ## convert the cursor into the text index,
    ## including the line and position
    def getLogicLineFromCursor(self):
        y, x = self.cursor
        line, index = self.getLineFromPline()
        accu = -index; l = 0;
        templine = line
        tempy = y + (1-self.box)
        for i in range(templine, len(self.textLines)):
            line = i
            l = self.textLines[i]
            accu += l
            if accu >= tempy:
                break
        position = (l - (accu - tempy) - 1) * self.subwidth + x
        logger.debug("convert cursor(y=%d, x=%d) to Logic cursor(y=%d, x=%d)" 
                % (y, x, line, position))
        return line, position
    
    ## convert the Logic Cursor(line , position)
    ## to the cursor in the screen (y, x)
    def getCursorFromLogicCursor(self, line, width):
        l, index = self.getLineFromPline()
        y = self.box - index
        for i in range(l, line):
            y += self.textLines[i]
        x = width % self.subwidth
        y += int(width / self.subwidth)
        logger.debug("convert Logic cursor(y=%d, x=%d) to cursor(y=%d, x=%d)"
                % (line, width, y, x))
        return y, x

    ## scrollDown step plines
    def scrollDown(self, step=1):
        y, x = self.cursor
        temp = self.pline
        ystep = 0
        scrolled = True
        if temp + step >= sum(self.textLines):
            self.pline = sum(self.textLines) - 1
            ystep = sum(self.textLines)-temp - 1
            scrolled = False
        else:
            self.pline += step
            ystep = step
        
        if y - ystep < self.box:
            y = self.box
        else:
            y -= ystep
        self.cursor = (y, x)
        logger.info("+++++the cursor is (%d, %d)" % self.cursor)
        return scrolled

    def scrollUpScreen(self):
        step = self.textbottom - self.textup
        self.scrollUp(step)

    def scrollDownScreen(self):
        step = self.textbottom - self.textup
        self.scrollDown(step)

    def scrollBottom(self):
        y, x = self.cursor
        step = sum(self.textLines) - self.pline
        self.scrollDown(step)

    def scrollBeginning(self):
        y, x = self.cursor
        step = self.pline + y
        self.scrollUp(step)

    def scrollUp(self, step=1):
        y, x = self.cursor
        temp = self.pline
        ystep = 0
        scrolled = True
        if temp - step < 0:
            self.pline = 0
            ystep = temp
            scrolled = False
        else:
            self.pline -= step
            ystep = step

        if y + ystep > self.textbottom:
            y = self.textbottom
        else:
            y += ystep
        self.cursor = (y, x)
        return scrolled

    def moveLeft(self, step=1):
        y, x = self.cursor
        line, pos = self.getLogicLineFromCursor()
        pos = 0 if pos-step <= 0 else pos-step
        if y > self.box:
            y, x = self.getCursorFromLogicCursor(line, pos)
        else:
            if y == self.box and x == 0:
                self.scrollUp()
            y, x = self.getCursorFromLogicCursor(line, pos)
        self.cursor = (y, x)
        self.putCursor()

    def moveRight(self, step=1, newline=False):
        y, x = self.cursor
        line, pos = self.getLogicLineFromCursor()
        pos = len(self.text[line]) if pos+step > len(self.text[line]) else pos+step
        temp = math.ceil((step - (self.subwidth - x)) / self.subwidth)
        if y + temp <= self.textbottom:
            y, x = self.getCursorFromLogicCursor(line, pos)
        else:
            #if y == self.textbottom and x + step > self.subwidth-1:
            #    self.scrollDown(step % self.subwidth)
            logger.info("scroll down %d lines" % (y +temp-self.textbottom))
            self.scrollDown(y + temp - self.textbottom)
            y, x = self.getCursorFromLogicCursor(line, pos)
        self.cursor = (y, x)
        self.putCursor()

    def moveTop(self):
        y, x = self.cursor
        p = self.pline + (y - self.box)
        line, index = self.getLineFromPline(p)
        uptime = index
        if y - index < self.box:
            self.scrollUp(self.box - y + index)
        l, _ = self.getLogicLineFromCursor()
        y, x = self.getCursorFromLogicCursor(l, 0)
        self.cursor = (y, x)
        self.putCursor()

    def InsertMode(self):
        self.mode = _INSERT_MODE
        self.putCursor()

    def NormalMode(self):
        mode = self.mode
        self.mode = _NORMAL_MODE
        if mode == _INSERT_MODE:
            self.moveLeft()
        self.putCursor()


    def moveEnd(self):
        y, x = self.cursor
        p = self.pline + (y-self.box)
        line, index = self.getLineFromPline(p)
        downtime = self.textLines[line] - index - 1

        if y + downtime > self.textbottom:
            down = y + downtime - self.textbottom
            self.scrollDown(down)
        y, x = self.cursor
        y += downtime
        x = self.subwidth
        self.cursor = (y, x)
        self.putCursor()

    def moveUp(self, step=1):
        y, x = self.cursor
        if y == self.box:
            scrolled = self.scrollUp()
            if not scrolled:
                return
        y, x = self.cursor
        y -= 1
        self.cursor = (y, x)
        self.putCursor()
        
    def moveDown(self):
        y, x = self.cursor
        if y == self.textbottom:
            scrolled = self.scrollDown()
            if not scrolled:
                return
        else:
            p = self.pline + (y-self.box)
            line, index = self.getLineFromPline(p)
            if line == len(self.text) -1 and self.textLines[line]-1 == index:
                return

        y, x = self.cursor
        y += 1
        logger.info("line is now %d" % y)
        self.cursor = (y, x)
        self.putCursor()

    ## update textLine
    def getLineLength(self):
        self.textLines = [math.ceil(len(i)/self.subwidth) or 1 for i in self.text]

    ## returns the line and index of the text from pline
    def getLineFromPline(self, pline=None):
        if pline is None:
            pline = self.pline
        accu = 0
        temp = 0
        for i in range(len(self.textLines)):
            accu += self.textLines[i]
            temp = i
            if accu == pline:
                return temp+1, 0
            if accu > pline:
                break
        index = self.textLines[temp] - (accu - pline)
        return temp, index

    def drawLineNo(self, lineno, line, colorpair=3):
        self.window.addstr(line,self.box, 
                (("%%%ds" % self.linenowidth) % str(lineno)), 
                curses.color_pair(colorpair))

    def drawOneLine(self, lineno, text, starty, startx, fromindex, colorpair=1):
        tempText = mywrap(text, self.subwidth) or [""]
        accu = 0
        if fromindex == 0:
            self.drawLineNo(lineno, starty)
        for i in range(len(tempText)):
            if starty + i <= self.textbottom and fromindex+i < len(tempText):
                content = tempText[fromindex + i]
                self.subwin.addstr(starty+i,startx, content, 
                        curses.color_pair(colorpair))
                accu += 1
            else:
                break
        self.textLines[lineno-1] = len(tempText)
        return starty + accu
            

    def redraw(self):
        pline = self.pline
        line, index = self.getLineFromPline()
        first = self.textup
        linebais = 0
        startx = 0
        self.window.clear()
        while first <= self.textbottom:
            if line + linebais >= len(self.text):
                self.drawLineNo("~", first)
                first += 1
                continue
            first = self.drawOneLine(line+linebais+1, 
                    self.text[line+linebais], first, startx, index)
            index = 0
            linebais += 1
        self.subwin.move(*self.cursor)
        if self.box:
            self.window.box()
        ## draw status line
        line, pos = self.getLogicLineFromCursor()
        self.drawStatusLine("--%s--  %d %d" % (_MODE[self.mode], line+1, pos+1), 
                3, _COLOR_WHITE)

    def drawStatusLine(self, line, startx=None, colorpair=_COLOR_RED):
        startx = self.box if startx is None else startx
        self.window.addstr(self.statusLine, self.box, 
                ' ' * (self.subwidth-1-startx))
        self.window.addstr(self.statusLine,startx, line, curses.color_pair(colorpair))
        self.window.refresh()
            
    ## put cursor in the end of the line
    def putCursor(self):
        y, x = self.cursor
        line, pos = self.getLogicLineFromCursor()

        logger.info("len is %d, pos=%d" %(line, pos))
        if pos > len(self.text[line])-1:
            logger.info("in putCursor")
            temp = len(self.text[line]) + self.mode - 1
            pos = temp if temp > 0 else 0
            self.cursor = self.getCursorFromLogicCursor(line, pos)

    def noAction(self):
        pass

    ## called while get the user input
    ## under the normal mode
    def normalCommand(self, key):
        logger.debug("key is %s" % key)
        if key in self.normalModeKeys.keys():
            a = self.normalModeKeys.get(key, self.noAction)()
        else:
            #key = ord(key)
            if key == ord("a"):
                self.mode = _INSERT_MODE
                self.moveRight()
            elif key == ord("A"):
                self.mode = _INSERT_MODE
                self.moveEnd()
            elif key == ord("d"):
                self.deleteLine()
            elif key == ord("I"):
                self.mode = _INSERT_MODE
                self.moveTop()
            elif key == ord(":"):
                self.handleCommand()
        if not self.needRedraw:
            self.needRedraw = True
            logger.info("need not redraw")
            return
        self.redraw()

    ## execute the NORMAL MODE command after the ":"
    def handleCommand(self):
        self.needRedraw = False
        self.display_raw(" "*self.subwidth, self.box,self.statusLine)
        a = self.get_param(self.statusLine,self.box, ":").decode()
        if a == "wq":
            if self.save():
                self.clear = True
            else:
                self.drawStatusLine("not in a file")
                return
            self.exit = True
        elif a == "w":
            if self.save():
                self.clear = True
                self.drawStatusLine("file saved!", colorpair=_COLOR_GREEN)
            else:
                self.drawStatusLine("not in a file")
        elif a == "q!":
            self.exit = True
        elif a == "q":
            if self.clear:
                self.exit = True
            else:
                self.drawStatusLine("file changed but not saved")
        elif a.startswith("!"):
            pass
        elif a.startswith("open"):
            temp = a.split(" ")
            if len(temp) == 2 and temp[1] != '':
                filename = temp[1]
                self.openFile(filename)
                self.needRedraw = True
            else:
                self.drawStatusLine("filename is not specified")
        else:
            self.drawStatusLine("unknown command")

    ## called while get the user input
    ## under the insert mode
    def insertCommand(self, key):
        logger.info("[insert mode] %s" % (str(key)))
        self.clear = False
        if key in self.insertModeKeys.keys():
            self.insertModeKeys[key]()
        elif key > 31 and key < 127:
            self.insertPrintableChar(key)
        else:
            self.insertUnPrintableChar(key)
        self.redraw()

    def selfScrollUp(self, step=1):
        y, x = self.cursor
        p = self.pline + (y - self.box)
        line, index = self.getLineFromPline(p)

    def deleteLine(self):
        self.scrollDown()
        self.clear = False
        y, x = self.cursor
        p = self.pline + (y - self.box)
        line, index = self.getLineFromPline(p)
        # delete not the last line
        logger.info("in delete Line1, line=%d" % line)
        if line == 0 and len(self.text) == 1:
            self.pline = 0
            self.cursor = (self.box, 0)
            self.text = [""]
            self.textLines = [1]
            return

        border = 1 if len(self.text) - 1 == line else 0
        logger.info("in delete Line2")
        tempy = y - self.box - index 
        if tempy < self.textup:
            self.scrollUp(self.textup - tempy)
            y, x = self.cursor
            y += self.textup - tempy 
            y -= border
            self.cursor = (y, x)
        y, x = self.cursor
        y -= index + border
        logger.info("the cursor is now (%d, %d)" % self.cursor)
        self.text.pop(line)
        self.cursor = (y, 0)
        self.getLineLength()

    def deleteChar(self, backward=False):
        backward = True if self.mode else False
        y, x = self.cursor
        if backward:
            logger.info("move left in delete char")
            self.moveLeft()

        line, pos = self.getLogicLineFromCursor()
        ## at the start of line
        if x == 0 and pos == 0 and line > 0 and backward:
            logger.info("in delete1")
            temp = self.text[line-1]
            after = self.text[line]
            self.text[line-1] = temp+after
            self.text.pop(line)
            self.cursor = self.getCursorFromLogicCursor(line-1, 
                    len(self.text[line-1]))
        else:
            logger.info("in delete2, pos=%d" % pos)
            temp = self.text[line]
            before = temp[:pos]
            after = temp[pos+1:]
            self.text[line] = before+after

        self.putCursor()

    def loop(self):
        self.redraw()
        while True:
            a = self.subwin.getch()
            logger.debug("a is %s" % a)
            if self.mode == _NORMAL_MODE:
                self.normalCommand(a)
            elif self.mode == _INSERT_MODE:
                self.insertCommand(a)
            if self.exit is True:
                break
        return '\n'.join(self.text)


if __name__ == "__main__":
    from misc import set_win, unset_win
    import traceback
    from io import StringIO

    try:
        main = BaseWindow(main=True)
        y, x = main.getWindow().getmaxyx()
        set_win()
        width = 4
        edit = Editor(0,0, y,x-(width+1), box=True)
        logger.debug("in main")
        edit.loop()

    except Exception as e:
        fp = StringIO()
        traceback.print_exc(file=fp)
        message = fp.getvalue()
        logger.critical(message)
    finally:
        unset_win()
