from helpers import get_widget_space
from PIL import ImageFile, ImageTk, Image
from log_format import str_tail_after
from typing import Callable
import tkinter as tk


class Window:
    def __init__(self, gui_width, gui_height, title="Tagman", is_child=False):
        self.__is_running = False
        if is_child:
            self._root = tk.Toplevel()
        else:
            self._root = tk.Tk()
        self._root.title(title)
        self._root.protocol(name="WM_DELETE_WINDOW", func=self.close)
        self._root.bind("<Configure>", self.on_resize)
        self.active_queue_win = None

        # set up master pane
        self._p_master = tk.Frame(self._root, height=gui_height, width=gui_width)
        self._p_master.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
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
        self._root.protocol(name="WM_DELETE_WINDOW", func=self.respond_close_failure)
        self.queue = queue
        self.func_on_yes = func_on_yes
        self.current = None
        # set up pane to display information and prompt user for action
        self.__p_info = tk.Frame(self._p_master, height=3, width=gui_width)
        self.__p_info.pack(side=tk.TOP, fill=tk.X, expand=True, padx=5, pady=5)
        self.__l_info = tk.Label(self.__p_info, text="Click YES.")
        self.__l_info.pack(side=tk.LEFT)
        self.__p_options = tk.Frame(self._p_master, height=1, width=gui_width)
        self.__p_options.pack()
        self.checkbox_var = tk.IntVar()
        self.checkbox_var.set(0)
        self.checkbox = tk.Checkbutton(
            self.__p_options,
            text="Apply for all in queue",
            variable=self.checkbox_var,
            onvalue=1,
            offvalue=0,
        )
        self.checkbox.pack(side=tk.LEFT)
        self.__bt_yes = tk.Button(
            self.__p_options, text="Yes", command=self.confirm_yes
        )
        self.__bt_yes.pack(side=tk.LEFT)
        self.__bt_no = tk.Button(self.__p_options, text="No", command=self.confirm_no)
        self.__bt_no.pack(side=tk.LEFT)

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


class DisplayManager(tk.Frame):
    """
    DisplayManager is a frame consisting of navigation buttons, a refresh button,
    and a pane for image display. An internal index is used to track the index of
    a list of images that ought be displayed. Only one image is rendered at a time.
    """

    def __init__(
        self,
        master: tk.Misc | None,
        height: int,
        cmd_on_update: Callable,
    ):
        super().__init__(
            master=master,
            height=height,
            highlightbackground="gray",
            highlightthickness=2,
        )
        self.pack(anchor="e", side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.pack_propagate(False)

        self.on_update_do: Callable = cmd_on_update
        self.display_index = 0
        self.display_image: Image.Image | None = None

        self._l_status = tk.Label(self, text="No image loaded.")
        self._l_status.pack(anchor="w")

        self._f_nav_buttons = tk.Frame(self)
        self._f_nav_buttons.pack(side=tk.TOP, anchor="center")

        # decr button
        tk.Button(self._f_nav_buttons, text=" <- ", command=self.decr_display).grid(
            column=0, row=0
        )
        # refresh button
        tk.Button(self._f_nav_buttons, text="Refresh", command=self.on_update).grid(
            column=1, row=0, columnspan=2
        )
        # incr button
        tk.Button(self._f_nav_buttons, text=" -> ", command=self.incr_display).grid(
            column=3, row=0
        )

        self._l_image = tk.Label(self)
        self._l_image.pack(fill=tk.BOTH, expand=True, side=tk.TOP)

    def reset(self):
        self.display_index = 0
        self.on_update()

    def on_update(self):
        self.on_update_do()

    def max_index(self) -> int:
        return 0

    def incr_display(self):
        if self.display_index == self.max_index():
            self.display_index = 0
        else:
            self.display_index += 1
        self.on_update()

    def decr_display(self):
        if self.display_index == 0:
            self.display_index = self.max_index()
        else:
            self.display_index -= 1
        self.on_update()

    def display_from_path(self, png_path, dir=""):
        if png_path and png_path.endswith(".png"):
            self._load_image(png_path)
            self._render_image()
            if self._l_status:
                if dir:
                    self._l_status.config(
                        text=f"Current: {str_tail_after(dir, '/')}...{str_tail_after(png_path, '/')}"
                    )
                self._l_status.config(
                    text=f"Current: ...{str_tail_after(png_path, '/')}"
                )
        else:
            raise Exception("only images with .png extensions may be opened")

    def _load_image(self, file_path):
        if not file_path:
            raise ValueError("could not load image; filepath was empty")

        try:
            img = Image.open(file_path)

            manager_space = get_widget_space(self)
            status_h = get_widget_space(self._l_status)[1]
            nav_h = get_widget_space(self._f_nav_buttons)[1]
            display_space = (manager_space[0], manager_space[1] - status_h - nav_h)
            self.display_image = self.fit_image_to_size(img, display_space)
        except Exception as e:
            raise e

    def _render_image(self):
        """
        render_image converts a valid display_image for rendering within
        the Tk DisplayManager's label used for image rendering.
        """
        if not self.display_image:
            raise ValueError("No image has been loaded for display.")

        self.update_idletasks()
        tk_image = ImageTk.PhotoImage(
            self.display_image
        )  # convert for tkinter compatibility
        self._l_image.config(image=tk_image)
        self._l_image.image = tk_image  # type: ignore

    def fit_image_to_size(
        self, image: ImageFile.ImageFile, available_size: tuple[int, int]
    ) -> Image.Image | None:
        """
        fit_image_to_size calculates the new aspect ratio required for
        resizing image represented by the given ImageFile to fit within
        as much of the available space of the display pane as possible.

        It returns an Image with this ratio applied.
        """
        if not image:
            return None

        # get original aspect ratio as width/height
        ratio_w = available_size[0] / image.width
        ratio_h = available_size[1] / image.height

        scale_factor = min(ratio_w, ratio_h)

        target_width = int(image.width * scale_factor)
        target_height = int(image.height * scale_factor)

        return image.resize((target_width, target_height), Image.Resampling.LANCZOS)
