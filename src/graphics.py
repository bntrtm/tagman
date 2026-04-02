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


class DisplayManager:
    """
    DisplayManager is a window consisting of navigation buttons, a refresh button,
    and a pane for image display. An internal index is used to track the index of
    a list of images that ought be displayed. Only one image is rendered at a time.
    """

    def __init__(
        self,
        master: tk.Misc | None,
        height: int,
        cmd_on_update: Callable,
    ):
        self.on_update_do: Callable = cmd_on_update
        self.display_index = 0
        self.display_image: Image.Image | None = None

        self.__p_viewer = tk.Frame(
            master,
            height=height,
            highlightbackground="gray",
            highlightthickness=2,
        )
        self.__p_viewer.pack(
            anchor="e", side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5
        )
        self.__p_viewer.pack_propagate(False)
        self.__l_viewer = tk.Label(self.__p_viewer, text="No image loaded.")
        self.__l_viewer.pack(anchor="w")

        self.__p_display_nav = tk.Frame(self.__p_viewer)
        self.__p_display_nav.pack(side=tk.TOP, anchor="center")
        self.__bt_decrdisplay = tk.Button(
            self.__p_display_nav, text=" <- ", command=self.decr_display
        )
        self.__bt_decrdisplay.grid(column=0, row=0)
        self.__bt_refresh = tk.Button(
            self.__p_display_nav, text="Refresh", command=self.on_update
        )
        self.__bt_refresh.grid(column=1, row=0, columnspan=2)
        self.__bt_incrdisplay = tk.Button(
            self.__p_display_nav, text=" -> ", command=self.incr_display
        )
        self.__bt_incrdisplay.grid(column=3, row=0)

        self.__l_image = tk.Label(self.__p_viewer)
        self.__l_image.pack(fill=tk.BOTH, expand=True, side=tk.TOP)

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
            if self.__l_viewer:
                if dir:
                    self.__l_viewer.config(
                        text=f"Current: {str_tail_after(dir, '/')}...{str_tail_after(png_path, '/')}"
                    )
                self.__l_viewer.config(
                    text=f"Current: ...{str_tail_after(png_path, '/')}"
                )
        else:
            raise Exception("only images with .png extensions may be opened")

    def _load_image(self, file_path):
        if not file_path:
            raise ValueError("could not load image; filepath was empty")

        try:
            self.__p_viewer.update_idletasks()
            inner_master_h, inner_master_w = get_widget_inner_canvas_size(
                self.__p_viewer
            )
            inner_viewer_h = get_widget_inner_canvas_size(self.__l_viewer)[0]
            inner_nav_h = get_widget_inner_canvas_size(self.__p_display_nav)[0]
            available_height, available_width = (
                inner_master_h - inner_viewer_h - inner_nav_h,
                inner_master_w,
            )

            img = Image.open(file_path)
            self.display_image = self.fit_image_to_height(
                img, (available_height, available_width)
            )
        except Exception as e:
            raise e

    def _render_image(self):
        """
        render_image converts a valid display_image for rendering within
        the Tk DisplayManager's label used for image rendering.
        """
        if not self.display_image:
            raise ValueError("No image has been loaded for display.")

        self.__l_image.update_idletasks()
        self.__l_image.update()
        tk_image = ImageTk.PhotoImage(
            self.display_image
        )  # convert for tkinter compatibility
        self.__l_image.config(image=tk_image)
        self.__l_image.image = tk_image  # type: ignore

    def fit_image_to_height(
        self, image: ImageFile.ImageFile, available_size: tuple[int, int]
    ) -> Image.Image | None:
        """
        fit_image_to_height calculates the new aspect ratio required for
        resizing the ImageFile image to fit within as much space of the
        display pane as possible, and returns an Image with this ratio
        applied.
        """
        if not image:
            return None

        # get original aspect ratio as width/height
        ratio_h = available_size[0] / image.height
        ratio_w = available_size[1] / image.width

        scale_factor = min(ratio_w, ratio_h)

        target_height = int(image.height * scale_factor)
        target_width = int(image.width * scale_factor)

        return image.resize((target_width, target_height), Image.Resampling.LANCZOS)


def get_widget_inner_canvas_size(widget: tk.Misc):
    height = widget.winfo_height()
    width = widget.winfo_width()
    bd = int(widget.cget("borderwidth"))
    ht = int(widget.cget("highlightthickness"))
    pady = int(widget.cget("pady"))
    padx = int(widget.cget("padx"))
    height_loss = (bd + ht + pady) * 2
    width_loss = (bd + ht + padx) * 2
    return height - height_loss, width - width_loss
