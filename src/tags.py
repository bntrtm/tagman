from tkinter import Button, DISABLED


class TagBox:
    def __init__(self, win, parent, tag):
        self.win = win
        self.parent = parent
        self.tag_text = tag
        self.is_trigger = False
        if self.win is not None:
            if self.win.dataset is not None:
                if tag == self.win.dataset.trigger_word:
                    self.is_trigger = True
        self.bt = Button(parent, text=tag, command=self.devise_action)
        if self.is_trigger:
            self.bt.config(text=f"{tag}🔒", bg="gold", state=DISABLED)

    def devise_action(self):
        if self.is_trigger:
            return
        match self.win.tag_click_mode.get():
            case "Delete":
                self.win.dataset.remove_tag_from_image_caption(
                    self.tag_text, png_path=self.win.get_png_path()
                )
            case "Delete_All":
                print(
                    f'Removing tag "{self.tag_text}" from all .txt files in dataset {self.win.directory}'
                )
                self.win.dataset.remove_tag_from_image_caption(self.tag_text, all=True)
            case "Apply_All":
                print(
                    f'Applying tag "{self.tag_text}" to all .txt files in dataset {self.win.directory}'
                )
                self.win.dataset.add_tag_to_image_caption(self.tag_text, all=True)
            case _:
                raise ValueError("only 'Delete' and 'Apply_All' are acceptable actions")
        self.win.refresh()

    def destroy(self):
        if self.bt is not None and self.bt.winfo_exists():
            self.bt.destroy()
