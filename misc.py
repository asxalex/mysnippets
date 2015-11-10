import curses

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
