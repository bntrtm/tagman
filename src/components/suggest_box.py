import tkinter as tk


class SuggestBox(tk.Frame):
    """
    SuggestBox is a frame-based widget usable for displaying up to three choies to users in a dropdown list.
    Choices closer to the top of the box are shown more prominently.
    """

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
