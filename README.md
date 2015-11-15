mysnippet
===
mysnippet is used to collect personal code snippets in command line.

create a new snippet:

![img](http://i12.tietuku.com/87dd3f4f0b5ae137.png)

It uses sqlite to store necessary information, including snippet name, alias, filename, etc. The real file is stored in the txtFiles folder.

keystrokes for the application:

|Key|Action|
|---|---|
|n|create a new snippet, a dialog will pop up for necessary information|
|j|move to next snippet|
|k|move to previous snippet|
|l|open the current snippet in the editor|
|d|delete current snippet, a dialog will pop up for ensurement|

When a certain snippet is opened, we can edit it, save it, and copy it to the clipboard. Refer to the editor section below for greater details.

![img](http://i12.tietuku.com/2f072b54c806e841.png)

# Related curses widgets
The widgets written are as follows:

## itemlist
Itemlist displays the items as a list. use it as follows:

```python
if __name__ == "__main__":
    from misc import set_win, unset_win
    from base import BaseWindow
    try:
        # make a main window first
        main = BaseWindow(main=True)
        set_win()

        # create an Itemlist
        itemlist = ItemList(0,0, mainwindow=main)

        # set or add items to it
        itemlist.setItem([a for a in "abcdefghijklmno"])
        itemlist.addItem("abcdefghijklmnopqrstuvwxyz")

        # loop over it
        itemlist.loop()

    except Exception as e:
        print(type(e), e)

    finally:
        unset_win()
```
where

```python
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
```

and it runs like this:

![img](http://i12.tietuku.com/0e97635b462b2922s.png)

The ItemList uses vim-like keystroke to move between the items(k for up and j for down), and q for quitting.

## dialogs
The InputDialog(prompt for user input), ProcessDialog(show the process of a certain process) and YesNoDialog(prompt for your choices, default for "yes" and "no") are supported at present.

```python
# a dialog example for YesOrNo

if __name__ == "__main__":
    from misc import set_win, unset_win
    from base import BaseWindow
    try:
        main = BaseWindow(main=True)

        set_win()
        dialog1 = YesNoDialog(mainwindow=main)
        dialog1.promptYesOrNo("Are you sure to quit?")
        dialog1.clear()
        
        dialog2 = InputDialog(mainwindow=main)
        dialog2.showInput(["name", "age", "gender"], text="Input your infomation:")
    except Exception as e:
        print(type(e), e)
    finally:
        unset_win()

```

Run it and it first prompts like this (use h for left and l for right):

![img](http://i12.tietuku.com/37e49158cd5bf189s.png)

and after an "Enter" is entered, a form is shown to gather your info :)

![img](http://i12.tietuku.com/907c4752f0ad45c6s.png)


## Editor
The editor is still in construction and it supports basic operations at present.

the editor has two modes(normal mode and insert mode :>)

the keybindings for normal mode:

|Key|Description|
|----|----|
|h|move left|
|j|move down|
|k|move up|
|l|move right|
|x|delete char under cursor|
|i|go to the insert mode at current position|
|a|go to the insert mode after the current position|
|A|go to the insert mode at the end of the line|
|I|go to the insert mode at the beginning of the line|
|G|move to bottom|
|B|scroll to beginning|
|D|delete current line|
|ctrl+b|scroll up a screen|
|ctrl+f|scroll down a screen|
|ctrl+u|copy the text to the clipboard|
|:w|write the text into file|
|:open filename|open file|
|:wq|save and quit|
|:q|quit|
|:q!|quit without save|

and the keybindings for insert mode:

|Key|Description|
|---|---|
|ctrl+f|move right|
|ctrl+b|move left|
|ctrl+n|move down|
|ctrl+p|move up|
|ctrl+a|move to the beginning of line|
|ctrl+e|move to the end of line|
|ctrl+v|paste the content in the clipboard into the editor|

![img](http://i12.tietuku.com/b3f45c8867f3b135.png)
