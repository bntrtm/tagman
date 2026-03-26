# Tagman

## A Tag Manager for Captioning Image Datasets

Tagman (_tag manager_) is a `tkinter`-based GUI application, whose purpose is to provide users with an efficient and user-friendly tool for captioning PNG image datasets with TXT files generated from tags.

![example](https://github.com/user-attachments/assets/59686119-e470-4960-8dc0-50ef38b9ebce)

### About

Building a detailed dataset is integral to getting good results when you building any algorithm leveraging image captions, or training some form of AI model on image data. However, the process is rather tedious. Auto-captioning programs building out an initial batch of `TXT` files to caption `PNG` images can apply the same irrelevant tag to a multitude of images within the dataset, or otherwise miss some obvious ones, compromising data integrity.

Amending this issue becomes an interminable task while using a traditional text editor, as one must individually scrutinize every `TXT` file for errors or missing details in their image captions. This problem becomes more evident as one's dataset grows (which, for best results, is ideal).

Tagman aims to equip users with the ability to easily visualize existing tags in image captions built within `\*.txt`` files, or even start building from the ground up!

### Features

- Loads an image dataset through a directory recursively
  - Prompts users on missing `*.txt` captions for existing `*.png` images
- Trigger Word protection
  - The first tag picked up by loading a dataset is saved as the trigger word for all captioning and protected from deletion.
- Image display shows users what image they are currently captioning
- A robust tag entry mechanism
  - Add a tag to a single caption
  - Add a tag to all captions in the dataset
  - Remove a tag from a single caption
  - Remove a tag from all captions in the dataset
  - Smart autocompletion feature for both the above processes
    - Existing tags in the dataset are suggested for single captions without the tag
    - Existing tags in a single caption are suggested during a removal process

## Requirements

Tagman requires Python 3.13+, and the following dependencies:

- Pillow (PIL) library.
- tkinter

With `uv` installed (and the `pyproject.toml` file present), you can install these dependencies with:

```bash
uv sync
```

## Quick Start

Clone the project to your desired directory:

```bash
git clone https://github.com/bntrtm/tagman.git
```

Sync dependencies with `uv sync`, as discussed above.

Run the program with `uv run main.py`.

The GUI will load with no meaningful contents. To begin work on a dataset, you need to build one by doing the following:

- Create a directory with at least one or more images within it (or within subdirectories) in PNG format.
- Ensure that there exists at least one TXT file with a name otherwise identical to some PNG file within the hierarchy, and that it is in the same directory as the png file.
- Ensure that the first word of all TXT files (or of just the one existing TXT file) is equivalent to the "trigger word" you want to define your dataset.

Select the `Load` button in the top-left corner of the GUI window. It will prompt you for a directory; choose the directory pertaining to the dataset you built, whose image captions you wish to edit.

The program will load all PNG images and their existing TXT captions into memory. For each PNG image without a corresponding TXT caption, you will be prompted on whether or not you would like for those PNG images to be loaded into memory. Selecting "Yes" for these prompts will create the appropriate TXT files in the proper directory (or subdirectories) and load them into memory. The Trigger Word will be applied to these new TXT files.

## Usage

This repository's [internal wiki](https://github.com/bntrtm/tagman/wiki/Tag-Management) covers how you can use the program for your purposes to perfect image captioning for your dataset!
