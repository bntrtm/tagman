from graphics import TagManagerWin


def main():
    win = TagManagerWin(900, 600)
    win.redraw()

    win.wait_for_close()


main()

