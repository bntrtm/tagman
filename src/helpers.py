import tkinter as tk


def get_widget_space(widget: tk.Widget) -> tuple[int, int]:
    """
    get_widget_space returns, as an XY tuple, the absolute amount of space made available to child widgets within the widget. This is done by subtracting any relevant styling elements from the widget's XY dimensions.
    """
    widget.update_idletasks()

    widget_w = widget.winfo_width()
    widget_h = widget.winfo_height()
    widget_bordering = (
        int(widget.cget("borderwidth")) + int(widget.cget("highlightthickness")) * 2
    )
    widget_padding_w = int(widget.cget("padx")) * 2
    widget_padding_h = int(widget.cget("pady")) * 2

    available_w = widget_w - widget_bordering - widget_padding_w
    available_h = widget_h - widget_bordering - widget_padding_h

    return (available_w, available_h)


def on_focus_in_entry_widget(event, widget, placeholder_text):
    if isinstance(widget, tk.Entry):
        text = widget.get()
    elif isinstance(widget, tk.Text):
        text = widget.get("1.0", "end-1c")  # USED FOR TEXT WIDGETS ONLY
    else:
        return
    if text == placeholder_text:
        widget.delete(0, "end")
        widget.config(fg="black")


def on_focus_out_entry_widget(event, widget, placeholder_text):
    if isinstance(widget, tk.Entry):
        text = widget.get()
    elif isinstance(widget, tk.Text):
        text = widget.get("1.0", "end-1c")  # USED FOR TEXT WIDGETS ONLY
    if len(text) == 0:
        widget.config(fg="gray")
        widget.insert(tk.END, placeholder_text)
