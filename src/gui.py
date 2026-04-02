import tkinter.filedialog
import tkinter.ttk as ttk
from typing import Callable
from warnings import deprecated
from graphics import Window, DisplayManager
import tkinter as tk
from tags import TagBox
from dataset import Dataset
import os


@deprecated("Dataset may be empty; should never be None")
def require_Dataset(func):
    def wrapper(*args, **kwargs):
        if args[0].dataset is None:
            raise Exception(
                "no Dataset object exists for the current session; load a directory to create one"
            )
        result = func(*args, **kwargs)
        return result

    return wrapper


class PNGDisplayManager(DisplayManager):
    def __init__(
        self,
        master: tk.Misc | None,
        height: int,
        cmd_on_update: Callable,
        dataset: Dataset,
    ):
        super().__init__(master, height, cmd_on_update)
        self.dataset: Dataset = dataset

    def reset(self, dataset: Dataset | None = None):
        if dataset:
            self.dataset = dataset
        super().reset()

    def on_update(self):
        self.display_from_path(self.get_display_path(), self.dataset.directory)
        super().on_update()

    def max_index(self) -> int:
        return len(self.dataset) - 1

    def get_display_path(self) -> str:
        if not self.dataset:
            return ""
        return self.dataset.get_png_path(self.display_index)

    def display_from_path(self, png_path, dir=""):
        if not self.dataset:
            return
        super().display_from_path(png_path, dir)


class TagManagerWin(Window):
    def __init__(self, gui_width, gui_height, title="Tagman"):
        super().__init__(gui_width, gui_height, title=title)

        self.dataset = Dataset("", self, make_empty=True)

        self.tag_btlist = []

        self.__p_info = None
        self.__bt_load_dir = None
        self.__l_info = None
        self.__l_index_counter = None
        self.__p_hrzbox = None
        self.__p_editor = None
        self.__l_editor = None
        self.__nbk_tagmodes = None
        self.__nbk_tagmodes_tab1 = None
        self.__nbk_tagmodes_tab2 = None
        self.__nbk_tagmodes_tab3 = None
        self.__bt_savedataset = None
        self.__caption_txt_field = None
        self.__p_tag_radio_bts = None
        self.tag_click_mode: tk.StringVar = tk.StringVar()

        self.__p_tagger = None
        self.__p_tag_container = None
        self.tag_entry_text = None
        self.__txt_tag_entry = None
        self.__p_radio_bts = None
        self.application_mode = None
        self.__autofill_box = None
        self.__l_viewer = None

        def build_info_pane():
            self.__p_info = tk.Frame(
                self._p_master,
                height=1,
                width=gui_width,
                highlightbackground="gray",
                highlightthickness=2,
            )
            self.__p_info.pack(side=tk.TOP, fill=tk.X, expand=True, padx=5, pady=5)
            self.__bt_load_dir = tk.Button(
                self.__p_info, text="Load", command=self.load_directory
            )
            self.__bt_load_dir.pack(side=tk.LEFT)
            self.__l_info = tk.Label(
                self.__p_info, text=f"Working under directory: {self.dataset.directory}"
            )
            self.__l_info.pack(side=tk.LEFT)
            self.__l_index_counter = tk.Label(self.__p_info, text="N/A")
            self.__l_index_counter.pack(side=tk.RIGHT, padx=5)

        def build_dataset_pane():
            self.__p_hrzbox = tk.Frame(self._p_master)
            self.__p_hrzbox.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        def build_editor_pane():
            self.__p_editor = tk.Frame(
                self.__p_hrzbox,
                height=gui_height,
                highlightbackground="gray",
                highlightthickness=2,
            )
            self.__p_editor.pack(
                anchor="w", side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5
            )
            self.__l_editor = tk.Label(self.__p_editor, text="Tag Text Editor")
            self.__l_editor.pack()

            # build editor in tab layout
            self.__nbk_tagmodes = ttk.Notebook(self.__p_editor, height=18)
            self.__nbk_tagmodes.pack(fill=tk.BOTH, expand=True)
            self.__nbk_tagmodes_tab1 = ttk.Frame(self.__nbk_tagmodes)
            self.__nbk_tagmodes_tab1.pack(padx=5, pady=5)
            self.__nbk_tagmodes_tab2 = ttk.Frame(self.__nbk_tagmodes)
            self.__nbk_tagmodes_tab2.pack(padx=5, pady=5)
            self.__nbk_tagmodes_tab3 = ttk.Frame(self.__nbk_tagmodes)
            self.__nbk_tagmodes_tab3.pack(padx=5, pady=5)
            self.__nbk_tagmodes.add(self.__nbk_tagmodes_tab1, text="Tag Editor")
            self.__nbk_tagmodes.add(self.__nbk_tagmodes_tab2, text="Caption")
            self.__nbk_tagmodes.add(self.__nbk_tagmodes_tab3, text="Options")
            self.__bt_savedataset = tk.Button(
                self.__nbk_tagmodes_tab3, text="Save Dataset", command=self.save_dataset
            )
            self.__bt_savedataset.pack(padx=5, pady=5)
            self.__caption_txt_field = tk.Text(
                self.__nbk_tagmodes_tab2, wrap=tk.WORD, state="disabled"
            )
            self.__caption_txt_field.pack(padx=5, pady=5)

            # allow users to set preferred tag button action
            self.__p_tag_radio_bts = tk.Frame(self.__nbk_tagmodes_tab1, width=25)
            self.__p_tag_radio_bts.pack(anchor="nw", padx=5, pady=5)
            self.tag_click_mode = tk.StringVar(self.__p_tag_radio_bts, "Delete")
            tag_click_radio_vals = {
                "Delete Selected": "Delete",
                "Apply Selected to All": "Apply_All",
                "Delete Selected from All": "Delete_All",
            }
            for text, value in tag_click_radio_vals.items():
                tk.Radiobutton(
                    self.__p_tag_radio_bts,
                    text=text,
                    variable=self.tag_click_mode,
                    value=value,
                ).pack(side=tk.LEFT, fill=tk.X, ipady=5)
            self.__p_tag_container = tk.Frame(self.__nbk_tagmodes_tab1)
            self.__p_tag_container.pack(anchor="sw", padx=5, pady=5)

            # pane for singular tag entry
            self.__p_tagger = tk.Frame(self.__p_editor)
            self.__p_tagger.pack(side=tk.LEFT)
            self.tag_entry_text = tk.StringVar()
            self.__txt_tag_entry = tk.Entry(
                self.__p_tagger, textvariable=self.tag_entry_text
            )  # , height=1, width=50
            self.__txt_tag_entry.pack(anchor="nw")
            self.tag_entry_text.trace_add("write", self.trace_tag_entry)
            self.__txt_tag_entry.bind(
                "<Return>", lambda event: self.on_tag_entry(event, self)
            )
            self.__txt_tag_entry.bind("<Tab>", self.on_tag_auto)
            self.__txt_tag_entry.bind("<Up>", self.nav_autofill)
            self.__txt_tag_entry.bind("<Down>", self.nav_autofill)
            self.__txt_tag_entry.bind("<Control-Right>", self.incr_display_handle)
            self.__txt_tag_entry.bind("<Control-Left>", self.decr_display_handle)
            self.__txt_tag_entry.bind(
                "<FocusIn>",
                lambda event: self.on_focus_in_entry_widget(
                    event, self.__txt_tag_entry, "Enter a tag..."
                ),
            )
            self.__txt_tag_entry.bind(
                "<FocusOut>",
                lambda event: self.on_focus_out_entry_widget(
                    event, self.__txt_tag_entry, "Enter a tag..."
                ),
            )
            self.on_focus_out_entry_widget(
                "<FocusOut>", self.__txt_tag_entry, "Enter a tag..."
            )

            # allow users to set preferred tag entry application option
            self.__p_radio_bts = tk.Frame(self.__p_tagger, width=25)
            self.__p_radio_bts.pack(anchor="sw")
            self.application_mode = tk.StringVar(self.__p_radio_bts, "Apply")
            application_radio_vals = {
                "Apply to Current": "Apply",
                "Apply to All": "Apply_All",
            }
            for text, value in application_radio_vals.items():
                new_bt = tk.Radiobutton(
                    self.__p_radio_bts,
                    text=text,
                    variable=self.application_mode,
                    value=value,
                )
                new_bt.pack(side=tk.LEFT, fill=tk.X, ipady=5)

            # expose a box for tag suggestions based on existing tag entry text
            self.__autofill_box = SuggestBox(self.__p_editor, color="red")

        build_info_pane()
        build_dataset_pane()
        build_editor_pane()
        self.display: PNGDisplayManager = PNGDisplayManager(
            self.__p_hrzbox, gui_height, self.refresh, self.dataset
        )

    def refresh(self):
        if self.dataset:
            self.update_index_counter_label_text()
            self.load_caption(self.get_png_path())

    def save_dataset(self):
        self.dataset.save_dataset()

    def on_resize(self, event):
        pass

    def get_png_path(self):
        if not self.dataset:
            return ""
        path = self.dataset.get_png_path(self.display.display_index)
        return path

    def get_txt_caption(self):
        return self.dataset.cache[self.get_png_path()][1]

    def tag_in_caption(self, tag):
        return self.dataset.tag_in_caption(tag, index=self.display.display_index)

    def update_index_counter_label_text(self):
        text = "N/A"
        if not self.dataset or not self.display:
            return text
        if len(self.dataset) == 0:
            return text
        text = f"{self.display.display_index + 1}/{len(self.dataset)}"
        if self.__l_index_counter is not None:
            self.__l_index_counter.config(text=text)
        return text

    def set_caption_display_text(self, text):
        if self.__caption_txt_field is not None:
            self.__caption_txt_field.config(state="normal")
            self.__caption_txt_field.delete("1.0", "end")
            self.__caption_txt_field.insert(tk.END, text)
            self.__caption_txt_field.config(state="disabled")

    def load_caption(self, png_path):
        """Loads contents of the editor window and all caption tags as interactive buttons

        1) Deletes contents of editor.
        2) Adds contents of txt_path file corresponding to png_path in the Dataset cache.
        3) Generates buttons representing each tag within the Dataset and displays them in the 'Tags' window.
        """
        self.set_caption_display_text(self.get_txt_caption())
        self.display_tags_as_boxes(self.__p_tag_container, self.get_txt_caption())

    def load_directory(self):
        directory = tkinter.filedialog.askdirectory()
        if not os.path.isdir(directory):
            print("Directory load operation was canceled.")
            return
        self.dataset = Dataset(directory, self)
        if len(self.dataset) == 0:
            # TODO: Log f"No valid images were found under directory {self.datasetdirectory}"
            pass
        if self.__l_info:
            self.__l_info.config(
                text=f"Working under directory: {self.dataset.directory}"
            )
        self.display.reset(self.dataset)
        self.refresh()

    def incr_display_handle(self, event):
        """For non-Button widget events passing 'event' as an argument"""
        self.display.incr_display()

    def decr_display_handle(self, event):
        """For non-Button widget events passing 'event' as an argument"""
        self.display.decr_display()

    def add_new_tagbox(self, widget, tag):
        new_bt = TagBox(
            self.dataset,
            widget,
            self.tag_click_mode,
            self.display.display_index,
            self.refresh,
            tag,
        )
        self.tag_btlist.append(new_bt)
        self.display_tagbox_grid()

    def display_tags_as_boxes(self, widget, tag_string, reload=True):
        """Deletes tagboxes that should not exist, adds those that should"""
        tag_strs = tag_string.rstrip(", ").split(", ")
        if len(self.tag_btlist) > 0:
            keep_bts = []
            for button in self.tag_btlist:
                if button.is_trigger:
                    keep_bts.append(button)
                    tag_strs.remove(button.tag_text)
                elif self.tag_in_caption(button.tag_text):
                    keep_bts.append(button)
                    tag_strs.remove(button.tag_text)
                else:
                    button.destroy()
            self.tag_btlist = keep_bts
        for tag in tag_strs:
            if tag.isspace() or not tag:
                continue
            self.add_new_tagbox(self.__p_tag_container, tag)
        self.display_tagbox_grid()

    def display_tagbox_grid(self):
        col_n = 0
        row_n = 0
        for tagbox in self.tag_btlist:
            span = max((len(tagbox.tag_text) // 16), 1)
            if tagbox.bt is None:
                continue
            tagbox.bt.grid(
                sticky="w", row=row_n, column=col_n, padx=2, pady=2, columnspan=span
            )
            col_n += span
            if col_n > 3:
                col_n = 0
                row_n += 1

    def on_tag_entry(self, event, win):
        if self.__txt_tag_entry is None:
            return
        negate = False
        entry = self.__txt_tag_entry
        text = entry.get().rstrip(", ").replace(",", "").lower()
        if text.startswith("-"):
            negate = True
            text = text.lstrip("-")
        if (box := self.__autofill_box) is not None and box.selected:
            text = box.selected.cget("text")
        entry.delete(0, "end")

        def try_continue(self):
            if text == self.dataset.trigger_word:
                return
            match self.application_mode.get():
                case "Apply":
                    if negate:
                        self.dataset.remove_tag_from_image_caption(
                            text, png_path=self.get_png_path()
                        )
                    else:
                        self.dataset.add_tag_to_image_caption(
                            text, png_path=self.get_png_path()
                        )
                case "Apply_All":
                    if negate:
                        print(
                            f'Removing tag "{text}" from all .txt files in dataset {self.dataset.directory}'
                        )
                        self.dataset.remove_tag_from_image_caption(
                            text, png_path=self.get_png_path(), all=True
                        )
                    else:
                        print(
                            f'Applying tag "{text}" to all .txt files in dataset {self.dataset.directory}'
                        )
                        self.dataset.add_tag_to_image_caption(
                            text, png_path=self.get_png_path(), all=True
                        )
                case _:
                    raise ValueError(
                        "only 'Apply' and 'Apply_All' are acceptable actions"
                    )
            self.refresh()

        try_continue(self)
        return "break"

    def on_tag_auto(self, event):
        if (box := self.__autofill_box) and (
            option_1_text := box.labels[0].cget("text")
        ):
            if t := self.tag_entry_text:
                if t.get().startswith("-"):
                    self.tag_entry_text.set(f"-{option_1_text}")
                else:
                    self.tag_entry_text.set(option_1_text)
            if self.__txt_tag_entry:
                self.__txt_tag_entry.icursor(tk.END)
        return "break"

    def trace_tag_entry(self, var, index, mode):
        if not self.dataset:
            return
        if not self.tag_entry_text:
            return
        text = self.tag_entry_text.get().lower()
        if not text:
            if box := self.__autofill_box:
                box.update([])
            return
        words_with_pre = self.dataset.tag_trie.words_with_prefix(text.lstrip("-"))
        options = []
        if len(words_with_pre) > 0:
            for suggestion in words_with_pre:
                if self.dataset.trigger_word == suggestion:
                    continue
                if text.startswith("-"):
                    if not self.tag_in_caption(suggestion):
                        continue
                else:
                    if self.tag_in_caption(suggestion):
                        continue
                options.append(suggestion)
                if len(options) == 3:
                    break
        if box := self.__autofill_box:
            box.update(options[:3])

    def nav_autofill(self, event):
        if box := self.__autofill_box:
            if event.keysym == "Up":
                box.navigate(1)
            elif event.keysym == "Down":
                box.navigate(-1)

    def on_focus_in_entry_widget(self, event, widget, placeholder_text):
        if isinstance(widget, tk.Entry):
            text = widget.get()
        elif isinstance(widget, tk.Text):
            text = widget.get("1.0", "end-1c")  # USED FOR TEXT WIDGETS ONLY
        else:
            return
        if text == placeholder_text:
            widget.delete(0, "end")
            widget.config(fg="black")

    def on_focus_out_entry_widget(self, event, widget, placeholder_text):
        if isinstance(widget, tk.Entry):
            text = widget.get()
        elif isinstance(widget, tk.Text):
            text = widget.get("1.0", "end-1c")  # USED FOR TEXT WIDGETS ONLY
        if len(text) == 0:
            widget.config(fg="gray")
            widget.insert(tk.END, placeholder_text)


class SuggestBox:
    def __init__(self, parent, color="black"):
        self.__p_listbox = tk.Frame(
            parent, height=3, width=50, highlightbackground="gray", highlightthickness=2
        )
        self.__p_listbox.pack(anchor="n", fill=tk.X, expand=False, padx=5, pady=5)
        self.__l_opt1 = tk.Label(
            self.__p_listbox, text="Option 1", fg=color, font=("Helvetica", 10, "bold")
        )
        self.__l_opt1.grid(column=0, row=0, sticky="w")
        self.__l_opt2 = tk.Label(
            self.__p_listbox, text="Option 2", fg=color, font=("Helvetica", 10, "bold")
        )
        self.lighten_foreground_color(self.__l_opt2, color, 0.165)
        self.__l_opt2.grid(column=0, row=1, sticky="w")
        self.__l_opt3 = tk.Label(
            self.__p_listbox, text="Option 3", fg=color, font=("Helvetica", 10, "bold")
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

    def update(self, options):
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
