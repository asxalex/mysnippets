curses widgets
===
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

```
     ┌────────────────────────────────────────────────┐
     │                                                │
     │            Are you sure to quit?               │
     │                                                │
     │                                                │
     │    ┌────┐                             ┌────┐   │
     │    │ No │                             │ Yes│   │
     │    └────┘                             └────┘   │
     │                                                │
     └────────────────────────────────────────────────┘
```

and after an "Enter" is entered, a form is shown to gather your info :)

```
    ┌────────────────────────────────────────────────┐
    │                                                │
    │                                                │
    │                                                │
    │                                                │
    │            Input your information              │
    │                                                │
    │                                                │
    │                                                │
    │                                                │
    │                                                │
    │                                                │
    │     name:                                      │
    │                                                │
    │                                                │
    │     age:                                       │
    │                                                │
    │                                                │
    │     gender:                                    │
    └────────────────────────────────────────────────┘
```

## Editor
The editor is still at construction and it supports basic operations at present.
