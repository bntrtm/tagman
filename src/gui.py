from components import DisplayManager, Window, EditorTab, SuggestBox
from helpers import on_focus_in_entry_widget, on_focus_out_entry_widget
from tags import TagBox
from state import State
import tkinter.filedialog
from typing import Callable
import tkinter as tk
from tkinter import ttk
import os


class PNGDisplayManager(DisplayManager):
    def __init__(
        self,
        master: tk.Misc | None,
        height: int,
        cmd_on_update: Callable,
        state: State,
    ):
        super().__init__(master, height, cmd_on_update)
        self.state: State = state

    def on_update(self):
        self.display_from_path(
            self.state.get_display_path(), self.state.dataset.directory
        )
        super().on_update()

    def max_index(self) -> int:
        return len(self.state.dataset) - 1

    def set_display_index(self, val: int):
        self.state.display_index = val

    def get_display_index(self):
        return self.state.display_index

    def display_from_path(self, png_path, dir=""):
        if not self.state.dataset:
            return
        super().display_from_path(png_path, dir)


class Header(tk.Frame):
    def __init__(self, master: tk.Misc | None, state: State):
        super().__init__(
            master=master,
            highlightbackground="gray",
            highlightthickness=1,
            pady=2,
            padx=2,
        )

        self.state = state

        self.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._l_dir = tk.Label(
            self,
            text=f"Working under directory: {self.state.dataset.directory}",
        )
        self._l_dir.pack(side=tk.LEFT)
        self._l_index_counter = tk.Label(self, text="N/A")
        self._l_index_counter.pack(side=tk.RIGHT, padx=5)

    def refresh(self):
        self.set_directory_text()
        self.update_index_counter()

    def set_directory_text(self):
        text = "No dataset in memory. Load a directory to begin."
        if self.state.dataset and self.state.dataset.directory:
            text = f"Working under directory: {self.state.dataset.directory}"
        self._l_dir.config(text=text)

    def update_index_counter(self):
        text = "N/A"
        if self.state.dataset:
            text = f"{self.state.display_index + 1}/{len(self.state.dataset)}"
        self._l_index_counter.config(text=text)


class TagManagerWin(Window):
    def __init__(self, state: State, gui_width, gui_height, title="Tagman"):
        super().__init__(gui_width, gui_height, title=title)

        self.state = state

        # heading widget holds the Load button and info about the dataset directory
        heading = tk.Frame(master=self._f_master)
        heading.pack(side=tk.TOP, fill=tk.X, expand=True)
        tk.Button(heading, text="Load", command=self.load_directory).pack(side=tk.LEFT)
        self._f_header = Header(heading, self.state)
        self._f_header.pack(side=tk.LEFT, padx=5)

        self._p_hrzbox = tk.Frame(self._f_master)
        self._p_hrzbox.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.editor: Editor = Editor(self._p_hrzbox, gui_height, self.state)
        self.editor.pack(
            anchor="w", side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5
        )
        self._tagger: TagEntry = TagEntry(
            self.editor, gui_height, self.state, self.refresh
        )
        self._tagger.pack(
            anchor="w", side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5
        )

        self.display: PNGDisplayManager = PNGDisplayManager(
            self._p_hrzbox, gui_height, self.refresh, self.state
        )
        self.display.pack(
            anchor="w", side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5
        )

        self._root.bind("<Control-Right>", self.incr_display_handle)
        self._root.bind("<Control-Left>", self.decr_display_handle)

    def redraw(self):
        super().redraw()
        self.refresh()

    def refresh(self):
        if self.state.dataset:
            self._f_header.refresh()
            self.editor.load_caption(self.state.get_display_path())

    def load_directory(self):
        directory = tkinter.filedialog.askdirectory()
        if not os.path.isdir(directory):
            print("Directory load operation was canceled.")
            return
        self.state.dataset.__init__(directory, self)
        if len(self.state.dataset) == 0:
            print(
                f"No valid images were found under directory {self.state.dataset.directory}"
            )
            pass

        # HACK: self.refresh() used to be here.
        # But we need to render the image on first load.
        # Yet we can't do that AND display.on_update, or else an infinite
        # loop occurs. So here, we just call display.on_update directly.
        # This works EXACTLY as intended...but it doesn't logically flow.
        self.display.on_update()
        # self.refresh()

    def incr_display_handle(self, event):
        """For non-Button widget events passing 'event' as an argument"""
        self.display.incr_display()

    def decr_display_handle(self, event):
        """For non-Button widget events passing 'event' as an argument"""
        self.display.decr_display()

    def on_resize(self, event):
        pass


class OptionsTab(EditorTab):
    def __init__(self, master: tk.Misc | None, height: int, state: State):
        super().__init__(
            master=master,
            height=height,
        )

        self.state: State = state
        tk.Button(self, text="Save Dataset", command=self.save_dataset).pack(
            padx=5, pady=5
        )

    def save_dataset(self):
        self.state.dataset.save_dataset()


class Editor(tk.Frame):
    def __init__(self, master: tk.Misc | None, height: int, state: State):
        super().__init__(
            master=master,
            height=height,
            highlightbackground="gray",
            highlightthickness=2,
        )

        self.state: State = state

        self.pack(anchor="w", side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.__l_editor = tk.Label(self, text="Tag Text Editor")
        self.__l_editor.pack()

        # build editor in tab layout
        self._nbk_tabs = ttk.Notebook(self, height=18)
        self._nbk_tabs.pack(fill=tk.BOTH, expand=True)

        self._f_tab_tagman = EditorTab(self._nbk_tabs, height)
        self._nbk_tabs.add(self._f_tab_tagman, text="Tag Editor")
        self.tag_btlist = []

        self._f_tab_caption = EditorTab(self._nbk_tabs, height)
        self._nbk_tabs.add(self._f_tab_caption, text="Caption")

        self._f_tab_options = OptionsTab(self._nbk_tabs, height, state)
        self._nbk_tabs.add(self._f_tab_options, text="Options")
        self._caption_txt_field = tk.Text(
            self._f_tab_caption, wrap=tk.WORD, state="disabled"
        )
        self._caption_txt_field.pack(padx=5, pady=5)

        # allow users to set preferred tag button action
        self._f_tag_radio_bts = tk.Frame(self._f_tab_tagman, width=25)
        self._f_tag_radio_bts.pack(anchor="nw", padx=5, pady=5)
        self.tag_click_mode = tk.StringVar(self._f_tag_radio_bts, "Delete")
        tag_click_radio_vals = {
            "Delete Selected": "Delete",
            "Apply Selected to All": "Apply_All",
            "Delete Selected from All": "Delete_All",
        }
        for text, value in tag_click_radio_vals.items():
            tk.Radiobutton(
                self._f_tag_radio_bts,
                text=text,
                variable=self.tag_click_mode,
                value=value,
            ).pack(side=tk.LEFT, fill=tk.X, ipady=5)
        self._f_tag_container = tk.Frame(self._f_tab_tagman)
        self._f_tag_container.pack(anchor="sw", padx=5, pady=5)

    def set_caption_display_text(self, text):
        if self._caption_txt_field is not None:
            self._caption_txt_field.config(state="normal")
            self._caption_txt_field.delete("1.0", "end")
            self._caption_txt_field.insert(tk.END, text)
            self._caption_txt_field.config(state="disabled")

    def load_caption(self, png_path):
        """Loads contents of the editor window and all caption tags as interactive buttons

        1) Deletes contents of editor.
        2) Adds contents of txt_path file corresponding to png_path in the Dataset cache.
        3) Generates buttons representing each tag within the Dataset and displays them in the 'Tags' window.
        """
        txt_caption = self.state.dataset.cache[self.state.get_display_path()][1]
        self.set_caption_display_text(txt_caption)
        self.display_tags_as_boxes(self._f_tag_container, txt_caption)

    def add_new_tagbox(self, tag):
        new_bt = TagBox(
            self.state,
            self._f_tag_container,
            self.tag_click_mode,
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
                elif self.state.dataset.tag_in_caption(
                    button.tag_text, index=self.state.display_index
                ):
                    keep_bts.append(button)
                    tag_strs.remove(button.tag_text)
                else:
                    button.destroy()
            self.tag_btlist = keep_bts
        for tag in tag_strs:
            if tag.isspace() or not tag:
                continue
            self.add_new_tagbox(tag)
        self.display_tagbox_grid()

    def display_tagbox_grid(self):
        col_n = 0
        row_n = 0
        for tagbox in self.tag_btlist:
            span = max((len(tagbox.tag_text) // 16), 1)
            if tagbox is None:
                continue
            tagbox.grid(
                sticky="w", row=row_n, column=col_n, padx=2, pady=2, columnspan=span
            )
            col_n += span
            if col_n > 3:
                col_n = 0
                row_n += 1


class TagEntry(tk.Frame):
    """a widget for singular tag entry"""

    def __init__(
        self, master: tk.Misc | None, height: int, state: State, on_entry_do: Callable
    ):
        super().__init__(master=master, height=height)
        self.pack(side=tk.LEFT, fill=tk.X)

        self.state: State = state
        self.on_entry_do = on_entry_do

        entry_vertical = tk.Frame(self)
        entry_vertical.pack(side=tk.LEFT, fill=tk.X)
        self._text = tk.StringVar()
        self._entry = tk.Entry(entry_vertical, textvariable=self._text)
        self._entry.pack(fill=tk.X, padx=2, pady=2)
        self._entry.pack(anchor="nw")
        self._text.trace_add("write", self.trace_tag_entry)
        self._entry.bind("<Return>", lambda event: self.on_tag_entry(event, self))
        self._entry.bind("<Tab>", self.on_tag_auto)
        self._entry.bind("<Up>", self.nav_autofill)
        self._entry.bind("<Down>", self.nav_autofill)

        self._entry.bind(
            "<FocusIn>",
            lambda event: on_focus_in_entry_widget(
                event, self._entry, "Enter a tag..."
            ),
        )
        self._entry.bind(
            "<FocusOut>",
            lambda event: on_focus_out_entry_widget(
                event, self._entry, "Enter a tag..."
            ),
        )
        on_focus_out_entry_widget("<FocusOut>", self._entry, "Enter a tag...")

        # allow users to set preferred tag entry application option
        self._f_radio_bts = tk.Frame(entry_vertical, width=25)
        self._f_radio_bts.pack(anchor="sw")
        self.application_mode = tk.StringVar(self._f_radio_bts, "Apply")
        application_radio_vals = {
            "Apply to Current": "Apply",
            "Apply to All": "Apply_All",
        }
        for text, value in application_radio_vals.items():
            new_bt = tk.Radiobutton(
                self._f_radio_bts,
                text=text,
                variable=self.application_mode,
                value=value,
            )
            new_bt.pack(side=tk.LEFT, fill=tk.X, ipady=5)

        # expose a box for tag suggestions based on existing tag entry text
        self._autofill_box = SuggestBox(self, color="red")
        self._autofill_box.pack(anchor="n", fill=tk.X, expand=False, padx=5, pady=5)

    def on_tag_entry(self, event, win):
        negate = False
        entry = self._entry
        text = entry.get().rstrip(", ").replace(",", "").lower()
        if text.startswith("-"):
            negate = True
            text = text.lstrip("-")
        if (box := self._autofill_box) is not None and box.selected:
            text = box.selected.cget("text")
        entry.delete(0, "end")

        def try_continue(self: TagEntry):
            if text == self.state.dataset.trigger_word:
                return
            match self.application_mode.get():
                case "Apply":
                    if negate:
                        self.state.dataset.remove_tag_from_image_caption(
                            text, png_path=self.state.get_display_path()
                        )
                    else:
                        self.state.dataset.add_tag_to_image_caption(
                            text, png_path=self.state.get_display_path()
                        )
                case "Apply_All":
                    if negate:
                        print(
                            f'Removing tag "{text}" from all .txt files in dataset {self.state.dataset.directory}'
                        )
                        self.state.dataset.remove_tag_from_image_caption(
                            text, png_path=self.state.get_display_path(), all=True
                        )
                    else:
                        print(
                            f'Applying tag "{text}" to all .txt files in dataset {self.state.dataset.directory}'
                        )
                        self.state.dataset.add_tag_to_image_caption(
                            text, png_path=self.state.get_display_path(), all=True
                        )
                case _:
                    raise ValueError(
                        "only 'Apply' and 'Apply_All' are acceptable actions"
                    )
            self.on_entry_do()

        try_continue(self)
        return "break"

    def on_tag_auto(self, event):
        if (box := self._autofill_box) and (
            option_1_text := box.labels[0].cget("text")
        ):
            if t := self._text:
                if t.get().startswith("-"):
                    self._text.set(f"-{option_1_text}")
                else:
                    self._text.set(option_1_text)
            if self._entry:
                self._entry.icursor(tk.END)
        return "break"

    def trace_tag_entry(self, var, index, mode):
        if not self.state.dataset:
            return
        if not self._text:
            return
        text = self._text.get().lower()
        if not text:
            self._autofill_box.update(options=[])
            return
        words_with_pre = self.state.dataset.tag_trie.words_with_prefix(text.lstrip("-"))
        options = []
        if len(words_with_pre) > 0:
            for suggestion in words_with_pre:
                if self.state.dataset.trigger_word == suggestion:
                    continue
                if text.startswith("-"):
                    if not self.state.dataset.tag_in_caption(
                        suggestion, self.state.display_index
                    ):
                        continue
                else:
                    if self.state.dataset.tag_in_caption(
                        suggestion, self.state.display_index
                    ):
                        continue
                options.append(suggestion)
                if len(options) == 3:
                    break
        self._autofill_box.update(options=options[:3])

    def nav_autofill(self, event):
        if box := self._autofill_box:
            if event.keysym == "Up":
                box.navigate(1)
            elif event.keysym == "Down":
                box.navigate(-1)
