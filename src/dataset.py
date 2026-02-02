from tkinter import Tk
from structures import Trie, Queue
from log_format import str_tail_after
import os


class Dataset:
    """Stores all data relevant to the current training session"""

    def __init__(self, directory, win):
        self.directory = directory
        self.win = win
        self.cache = {}
        self.tag_trie = Trie()
        self.trigger_word = None
        self.add_txt_queue = None
        if os.path.isdir(self.directory):
            self.expand_dataset_recursive(self.directory)
        # prompt user for action on .png files unaccompanied by .txt files
        if self.add_txt_queue is not None and self.win.active_queue_win is None:
            self.win.start_queue(
                self.add_txt_queue, func_on_yes=self.add_dataset_element
            )
        while self.win.active_queue_win is not None:
            pass
        self.generate_tag_trie()
        self.image_set = list(self.cache.keys())
        self.display_index = 0

    def save_dataset(self):
        if len(self.cache) == 0:
            raise Exception("No images were found in the dataset cache.")
        for key in self.cache:
            self.save_caption_to_txt(key)

    def save_caption_to_txt(self, png_path):
        txt_path = self.cache[png_path][0]
        if not os.path.isfile(txt_path):
            raise Exception("Supposed *.txt path is not a valid file")
        print(
            f"Saving caption for {str_tail_after(png_path, '/')} at {str_tail_after(txt_path, f'{str_tail_after(self.directory, '/')}/')}"
        )
        with open(txt_path, "w") as file:
            file.write(self.cache[png_path][1])

    def try_add_trie_tag(self, tag):
        if not tag.isspace():
            self.tag_trie.add(tag)

    def try_remove_trie_tag(self, tag):
        if not tag.isspace():
            self.tag_trie.remove(tag)

    def tag_in_caption(self, tag, index=None, png_path=None):
        """Returns whether or not the given tag is found within a specified caption.

        This function prioritizes its search in the following way:
            1) Is the tag in the caption of a specified png_path?
            2) Is the tag in the caption of a *.png path found within the dataset at a specified index?
            3) Is the tag in the caption of the current display index?
        """
        if index is None:
            index = self.display_index
        if png_path is not None:
            caption = self.cache[png_path][1]
        else:
            caption = self.cache[self.image_set[index]][1]
        search = "," + caption.replace(", ", ",").strip()
        return f",{tag}," in search

    def add_tag_to_image_caption(self, tag, png_path=None, all=False):
        if all:
            for key in self.cache:
                self.add_tag_to_image_caption(tag, png_path=key, all=False)
            return
        if not png_path:
            raise ValueError(
                "a .png path must be provided for the addition of a single tag to a corresponding .txt file"
            )
        if self.tag_in_caption(tag, png_path=png_path):
            return
        caption = self.cache[png_path][1]
        txt_path = self.cache[png_path][0]
        if caption.endswith(","):
            self.cache[png_path] = (txt_path, (caption + f" {tag}, "))
        else:
            self.cache[png_path] = (txt_path, (caption + f"{tag}, "))
        self.try_add_trie_tag(tag)

    def remove_tag_from_image_caption(self, tag, png_path=None, all=False):
        if all:
            for key in self.cache:
                self.remove_tag_from_image_caption(tag, png_path=key, all=False)
            return
        if not png_path:
            raise ValueError(
                "a .png path must be provided for the removal of a single tag from a corresponding .txt file"
            )
        if not self.tag_in_caption(tag, png_path=png_path):
            return
        txt_path = self.cache[png_path][0]
        caption = self.cache[png_path][1]
        self.cache[png_path] = (
            txt_path,
            (caption.replace(f", {tag}, ", ", ").replace(f", {tag},", ", ")),
        )
        self.try_remove_trie_tag(tag)

    def expand_dataset_recursive(self, path):
        """Given a directory, loads files within as a dataset.

        Takes a directory, then searches for files with .png extensions within. Recursively calls on directories.
        For each one found, an identically-named file with a .txt extension is sought.
        For each .png file without a corresponding .txt file, users are asked whether they'd like one generated.
            Users are only asked after all others are built.
            If the user chooses not to generate for a given file, the .png is discarded from the dataset.
            Users may select "Yes to All" in this popup menu to avoid choosing for each .png file missing a .txt.
        The property 'self.cache' is built as a dictionary of .png paths corresponding with tuple pairings
          of .txt paths and their contents (captions, separated by commas) in cache.
        """
        if not os.path.isfile(path):
            subpaths = os.listdir(path)
            if len(subpaths) > 0:
                for s in subpaths:
                    self.expand_dataset_recursive(os.path.join(path, s))
        elif path.endswith(".png"):
            if os.path.isfile(path.replace(".png", ".txt")):
                self.add_dataset_element(path)
            else:
                if self.add_txt_queue is None:
                    self.add_txt_queue = Queue()
                self.add_txt_queue.push(path)

    def add_dataset_element(self, png_path):
        """Given a path to a png file, adds existing txt file of the same name, or else returns an error"""
        if png_path in self.cache:
            print(
                f"Skipping {str_tail_after(png_path, f'{self.directory}/')} (already in dataset)."
            )
            return
        txt_path = png_path.replace(".png", ".txt")
        if os.path.isfile(txt_path):
            self.cache[png_path] = (txt_path, None)
            print(
                f"Adding training pair: {str_tail_after(png_path, f'{str_tail_after(self.directory, '/')}/')} -> {str_tail_after(txt_path, f'{str_tail_after(self.directory, '/')}/')}"
            )
        else:
            raise Exception(
                f".txt file still not found corresponding to image '{png_path}'"
            )

    def generate_tag_trie(self):
        """Populates tag trie and captions for the dataset.

        Reads each .txt file and populates the 'self.tag_trie' property with their contents.
        The tag trie also stores an integer associated with each tag representing the number of times it appears in the dataset.
        Also creates a cache for caption editing.
        """
        if len(self.cache) == 0:
            raise Exception(
                "nothing exists in the '.png_path : (.txt_path, caption)' dataset property"
            )
        for key in self.cache:
            txt_path = self.cache[key][0]
            if not txt_path:
                continue
            try:
                with open(txt_path, "r") as file:
                    file_content = file.read().strip()
                # eliminate all whitespace and delimit at commas to get a list of tags for this caption
                caption_tags = file_content.replace(", ", ",").split(",")
                # set a trigger word for this dataset if it hasn't been set already
                if self.trigger_word is None:
                    self.trigger_word = caption_tags[0]
                if self.trigger_word != caption_tags[0]:
                    print(
                        f"NOTICE: Trigger word '{self.trigger_word}' not found in file '{txt_path}.' Inserting for cache."
                    )
                    # ensure the trigger word does not exist anywhere ELSE within the caption
                    file_content = file_content.replace(f"{self.trigger_word}", f"")
                    # add the trigger word to the beginning of the caption
                    file_content = f"{self.trigger_word}, " + file_content.strip()
                # add caption to dataset
                self.cache[key] = (txt_path, file_content)
                # add all tags to the tag trie
                for tag in caption_tags:
                    self.try_add_trie_tag(tag)
            except FileNotFoundError:
                print(f"Error: The file '{txt_path}' was not found.")
            except Exception as e:
                print(f"An error occurred: {e}")
