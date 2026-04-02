from typing import Callable
from dataset import Dataset
from tkinter import Button, DISABLED, Widget, StringVar


class TagBox:
    def __init__(
        self,
        dataset: Dataset,
        parent: Widget,
        tag_click_mode: StringVar,
        display_index: int,
        on_press: Callable | None,
        tag: str,
    ):
        self.dataset = dataset
        self.parent = parent
        self.tag_click_mode = tag_click_mode
        self.display_index = display_index
        self.on_press = on_press
        self.tag_text = tag
        self.is_trigger = False
        if tag == self.dataset.trigger_word:
            self.is_trigger = True
        self.bt = Button(parent, text=tag, command=self.devise_action)
        if self.is_trigger:
            self.bt.config(text=f"{tag}🔒", bg="gold", state=DISABLED)

    def devise_action(self):
        if self.is_trigger:
            return
        match self.tag_click_mode.get():
            case "Delete":
                self.dataset.remove_tag_from_image_caption(
                    self.tag_text,
                    png_path=self.dataset.get_png_path(self.display_index),
                )
            case "Delete_All":
                print(
                    f'Removing tag "{self.tag_text}" from all .txt files in dataset {self.dataset.directory}'
                )
                self.dataset.remove_tag_from_image_caption(self.tag_text, all=True)
            case "Apply_All":
                print(
                    f'Applying tag "{self.tag_text}" to all .txt files in dataset {self.dataset.directory}'
                )
                self.dataset.add_tag_to_image_caption(self.tag_text, all=True)
            case _:
                raise ValueError("only 'Delete' and 'Apply_All' are acceptable actions")
        if self.on_press:
            self.on_press()

    def destroy(self):
        if self.bt and self.bt.winfo_exists():
            self.bt.destroy()
