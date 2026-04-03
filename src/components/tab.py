from tkinter import Frame, Misc


class EditorTab(Frame):
    """A frame with pre-configured padding."""

    def __init__(
        self,
        master: Misc | None,
        height: int,
    ):
        super().__init__(
            master=master,
            height=height,
        )

        self.pack(padx=5, pady=5)
