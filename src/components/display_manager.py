from helpers import get_widget_space
from log_format import str_tail_after
from PIL import ImageFile, ImageTk, Image
from typing import Callable
import tkinter as tk


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
