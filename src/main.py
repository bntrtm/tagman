from gui import TagManagerWin


def main():
    win = TagManagerWin(900, 600)
    win.redraw()

    win.wait_for_close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        raise e
        # print(f"Unexpected error: {e}")
