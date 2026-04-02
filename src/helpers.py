from warnings import deprecated
import tkinter as tk


@deprecated("use get_widget_space")
def get_widget_inner_canvas_size(widget: tk.Misc):
    height = widget.winfo_height()
    width = widget.winfo_width()
    bd = int(widget.cget("borderwidth"))
    ht = int(widget.cget("highlightthickness"))
    pady = int(widget.cget("pady"))
    padx = int(widget.cget("padx"))
    height_loss = (bd + ht + pady) * 2
    width_loss = (bd + ht + padx) * 2
    return height - height_loss, width - width_loss


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
