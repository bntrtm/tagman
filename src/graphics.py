from helpers import (
    get_widget_space,
)
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

        # set up master frame
        self._f_master = tk.Frame(self._root, height=gui_height, width=gui_width)
        self._f_master.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        # SET STRICT SIZE:
        self._f_master.pack_propagate(False)
        self._f_master.config(bg="red")

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
        self.__p_info = tk.Frame(self._f_master, height=3, width=gui_width)
        self.__p_info.pack(side=tk.TOP, fill=tk.X, expand=True, padx=5, pady=5)
        self.__l_info = tk.Label(self.__p_info, text="Click YES.")
        self.__l_info.pack(side=tk.LEFT)
        self.__p_options = tk.Frame(self._f_master, height=1, width=gui_width)
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
    and a pane for image display. Child classes may establish overrides for methods
    used to manage a display index, used to track the active element from a list of
    images that ought be displayed. Only one image is rendered at a time.
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
        self.set_display_index(0)
        self.on_update()

    def on_update(self):
        self.on_update_do()

    def max_index(self) -> int:
        """should return the last index usable from an iterable object representing images for display"""
        raise RuntimeError("function not implemented")

    def set_display_index(self, val: int):
        raise RuntimeError("function not implemented")

    def get_display_index(self):
        raise RuntimeError("function not implemented")

    def incr_display(self):
        i = self.get_display_index()
        if i == self.max_index():
            self.set_display_index(0)
        else:
            self.set_display_index(i + 1)
        self.on_update()

    def decr_display(self):
        i = self.get_display_index()
        if i == 0:
            self.set_display_index(self.max_index())
        else:
            self.set_display_index(i - 1)
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


class SuggestBox(tk.Frame):
    def __init__(self, master, color="black"):
        super().__init__(
            master=master,
            height=3,
            width=50,
            highlightbackground="gray",
            highlightthickness=2,
        )
        self.__l_opt1 = tk.Label(
            self, text="Option 1", fg=color, font=("Helvetica", 10, "bold")
        )
        self.__l_opt1.grid(column=0, row=0, sticky="w")
        self.__l_opt2 = tk.Label(
            self, text="Option 2", fg=color, font=("Helvetica", 10, "bold")
        )
        self.lighten_foreground_color(self.__l_opt2, color, 0.165)
        self.__l_opt2.grid(column=0, row=1, sticky="w")
        self.__l_opt3 = tk.Label(
            self, text="Option 3", fg=color, font=("Helvetica", 10, "bold")
        )
        self.lighten_foreground_color(self.__l_opt3, color, 0.33)
        self.__l_opt3.grid(column=0, row=2, sticky="w")
        self.labels = [self.__l_opt1, self.__l_opt2, self.__l_opt3]
        self.selected = None
        self.default_label_bg_color = self.__l_opt1.cget("bg")
        self.clear()

    def navigate(self, dir):
        if self.selected:
            if dir > 0:
                if self.selected == self.labels[1]:
                    self.select(self.labels[0])
                elif self.selected == self.labels[2]:
                    self.select(self.labels[1])
            elif dir < 0:
                if self.selected == self.labels[0]:
                    self.select(self.labels[1])
                elif self.selected == self.labels[1]:
                    self.select(self.labels[2])
        else:
            self.select(self.labels[0])

    def select(self, label):
        self.deselect()
        if label.cget("text"):
            self.selected = label
            label.config(bg="gold")

    def deselect(self):
        if self.selected:
            self.selected.config(bg=self.default_label_bg_color)
            self.selected = None

    def set_label_text(self, label, text):
        label.config(text=text)

    def update(self, options: list[str] = []):
        super().update()
        # if the first option is empty, it means that no text is entered
        if len(options) == 0 or not options[0]:
            self.clear()
            return
        for i in range(0, 3):
            if i > (len(options) - 1):
                self.set_label_text(self.labels[i], "")
                continue
            self.set_label_text(self.labels[i], options[i])

    def clear(self):
        for label in self.labels:
            self.set_label_text(label, "")
        self.deselect()

    def lighten_foreground_color(self, label, color, amount):
        """
        Lightens a hexadecimal color by a given amount and updates the label's background.
        Amount should be between 0 and 1, where 1 means full white.
        """
        rgb_tuple = label.winfo_rgb(color)  # Returns a tuple like (0, 0, 65535)
        hex_color = "#%02x%02x%02x" % (
            rgb_tuple[0] // 256,
            rgb_tuple[1] // 256,
            rgb_tuple[2] // 256,
        )

        if not (0 <= amount <= 1):
            raise ValueError("Amount must be between 0 and 1.")

        # Convert hex to RGB tuple
        hex_color = hex_color.lstrip("#")
        rgb = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

        # Lighten each RGB component
        lightened_rgb = []
        for component in rgb:
            new_component = int(component + (255 - component) * amount)
            lightened_rgb.append(
                min(255, new_component)
            )  # Ensure value doesn't exceed 255

        # Convert back to hex
        lightened_hex = "#%02x%02x%02x" % tuple(lightened_rgb)
        label.config(fg=lightened_hex)


class EditorTab(tk.Frame):
    def __init__(
        self,
        master: tk.Misc | None,
        height: int,
    ):
        super().__init__(
            master=master,
            height=height,
        )

        self.pack(padx=5, pady=5)
