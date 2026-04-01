from tkinter import (
    Tk,
    Toplevel,
    BOTH,
    Frame,
    TOP,
    LEFT,
    Label,
    IntVar,
    Checkbutton,
    Button,
    X,
)


class Window:
    def __init__(self, gui_width, gui_height, title="Tagman", is_child=False):
        self.__is_running = False
        if is_child:
            self._root = Toplevel()
        else:
            self._root = Tk()
        self._root.title(title)
        self._root.protocol(name="WM_DELETE_WINDOW", func=self.close)
        self._root.bind("<Configure>", self.on_resize)
        self.active_queue_win = None

        # set up master pane
        self._p_master = Frame(self._root, height=gui_height, width=gui_width)
        self._p_master.pack(fill=BOTH, expand=True, padx=5, pady=5)
        # SET STRICT SIZE:
        self._p_master.pack_propagate(False)

    def redraw(self):
        self._root.update_idletasks()
        self._root.update()

    def wait_for_close(self):
        self.__is_running = True
        while self.__is_running:
            self.redraw()
        print("Window closed.")

    def start_queue(self, queue, func_on_yes=None):
        self.active_queue_win = AddTxtQueueWin(
            300, 125, queue, self, func_on_yes=func_on_yes
        )
        self.active_queue_win.progress()
        # MAINLOOP
        self.active_queue_win.wait_for_close()

    def end_queue(self):
        if self.active_queue_win is not None:
            self.active_queue_win.close()
        self.active_queue_win = None

    def close(self):
        self._is_running = False
        self._root.destroy()

    def on_resize(self, event):
        pass


class AddTxtQueueWin(Window):
    def __init__(self, gui_width, gui_height, queue, caller_win, func_on_yes=None):
        super().__init__(
            gui_width, gui_height, title=".txt Caption Lookup Failure", is_child=True
        )
        self.caller_win = caller_win
        # self._Window__root.attributes('-topmost', True)
        self._root.protocol(name="WM_DELETE_WINDOW", func=self.respond_close_failure)
        self.queue = queue
        self.func_on_yes = func_on_yes
        self.current = None
        # set up pane to display information and prompt user for action
        self.__p_info = Frame(self._p_master, height=3, width=gui_width)
        self.__p_info.pack(side=TOP, fill=X, expand=True, padx=5, pady=5)
        self.__l_info = Label(self.__p_info, text="Click YES.")
        self.__l_info.pack(side=LEFT)
        self.__p_options = Frame(self._p_master, height=1, width=gui_width)
        self.__p_options.pack()
        self.checkbox_var = IntVar()
        self.checkbox_var.set(0)
        self.checkbox = Checkbutton(
            self.__p_options,
            text="Apply for all in queue",
            variable=self.checkbox_var,
            onvalue=1,
            offvalue=0,
        )
        self.checkbox.pack(side=LEFT)
        self.__bt_yes = Button(self.__p_options, text="Yes", command=self.confirm_yes)
        self.__bt_yes.pack(side=LEFT)
        self.__bt_no = Button(self.__p_options, text="No", command=self.confirm_no)
        self.__bt_no.pack(side=LEFT)

    def respond_close_failure(self):
        print("User attempted to close window, but option for queue item not chosen.")
        print(f"Choose 'Yes' or 'No' for the current queue item: {self.current}")

    def confirm_yes(self):
        if self.current is None:
            print("Error: no file selected to confirm.")
            return
        with open(f"{self.current.replace('.png', '.txt')}", "x"):
            pass
        if self.func_on_yes is not None:
            self.func_on_yes(self.current)
        self.progress()

    def confirm_no(self):
        if self.checkbox_var.get() == 1:
            self.queue = None
            self.caller_win.end_queue()
        else:
            self.progress()

    def progress(self):
        if self.queue is not None:
            self.current = self.queue.pop()
        if self.current is None:
            self.queue = None
            self.caller_win.end_queue()
            return
        if self.checkbox_var.get() == 1:
            self.confirm_yes()
            return
        self.__l_info.config(
            text=f"No corresponding .txt file exists for image: \n'{self.current}'. \nWould you like to create one?"
        )
