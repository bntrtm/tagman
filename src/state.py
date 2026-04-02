from dataset import Dataset


class State:
    """
    State can be passed around between widgets to track a store of
    persistent values independent of GUI elements.
    """

    def __init__(self, dataset: Dataset | None):
        self.display_index = 0
        if not dataset:
            self.dataset: Dataset = Dataset("", None, True)
        else:
            self.dataset = dataset

    def get_display_path(self) -> str:
        if not self.dataset:
            return ""
        return self.dataset.get_png_path(self.display_index)
