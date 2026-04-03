from typing import Callable
from state import State
import tkinter as tk


class TagBox(tk.Button):
    def __init__(
        self,
        state: State,
        master: tk.Widget,
        tag_click_mode: tk.StringVar,
        on_press_event: Callable,
        tag: str,
    ):
        self.state = state
        self.tag_click_mode = tag_click_mode
        self.on_press_event = on_press_event
        self.tag_text = tag
        super().__init__(master, text=tag, command=self.devise_action)
        self.is_trigger: bool = tag == self.state.dataset.trigger_word
        if self.is_trigger:
            self.config(text=f"{tag}🔒", bg="gold", state=tk.DISABLED)

    def devise_action(self):
        if self.is_trigger:
            return
        match self.tag_click_mode.get():
            case "Delete":
                self.state.dataset.remove_tag_from_image_caption(
                    self.tag_text, png_path=self.state.get_display_path()
                )
            case "Delete_All":
                print(
                    f'Removing tag "{self.tag_text}" from all .txt files in dataset {self.state.dataset.directory}'
                )
                self.state.dataset.remove_tag_from_image_caption(
                    self.tag_text, all=True
                )
            case "Apply_All":
                print(
                    f'Applying tag "{self.tag_text}" to all .txt files in dataset {self.state.dataset.directory}'
                )
                self.state.dataset.add_tag_to_image_caption(self.tag_text, all=True)
            case _:
                raise ValueError("only 'Delete' and 'Apply_All' are acceptable actions")
        if self.on_press_event:
            self.on_press_event()
