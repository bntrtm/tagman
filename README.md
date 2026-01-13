# Lora Tag Manager

## Easy management for Low Rank Adaptation image captioning

Lora Tag Manager is a GUI application made with python's tkinter library, whose purpose is to provide users with an efficient and user-friendly tool for captioning PNG images with TXT files and pairing them for use as a dataset for LoRA model training.

![example](https://github.com/user-attachments/assets/59686119-e470-4960-8dc0-50ef38b9ebce)

Building a detailed dataset for Low Rank Adaptation model training is integral to getting good results. However, the process is rather tedious. Training programs building out an initial batch of TXT files to caption PNG images can include the same irrelevant tag in a multitude of images for the dataset, or otherwise miss some obvious ones.

Amending this issue becomes an interminable task while using a traditional text editor, as one must individually scrutinize every TXT file for errors or missing details in their image captions. This issue becomes more evident as one's dataset grows (which, for best results, is ideal).

Lora Tag Manager aims to equip users with the ability to easily visualize existing tags in image captions built within .txt files. To accomplish this, it offers the following features:

- Loads a dataset through a directory recursively
    - Prompts users on missing TXT captions for existing PNG images
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

Lora Tag Manager requires Python 3.13+ and the python Pillow (PIL) library.

With Python installed, you can install Pillow with `pip install Pillow`.

## User Instructions

1. Clone the project to your desired directory:
```
git clone https://github.com/bntrtm/lora-tag-manager.git
```
2. Run the program with `Python main.py`.
3. The GUI will load with no meaningful contents. To begin work on a dataset, you need to build one by doing the following:
    - Create a directory with at least one or more images within it (or within subdirectories) in PNG format.
    - Ensure that there exists at least one TXT file with a name otherwise identical to some PNG file within the hierarchy, and that it is in the same directory as the png file. Ideally, you already have TXT files generated for each PNG image using some other tool dedicated to LoRA image captioning.
    - Ensure that the first word of all TXT files (or of just the one existing TXT file) is equivalent to the "trigger word" you want to define your LoRA dataset.
4. Select the `Load` button in the top-left corner of the GUI window. It will prompt you for a directory; choose the directory pertaining to the dataset you built, whose image captions you wish to edit.
5. The program will load all PNG images and their existing TXT captions into memory. For each PNG image without a corresponding TXT caption, you will be prompted on whether or not you would like for those PNG images to be loaded into memory. Selecting "Yes" for these prompts will create the appropriate TXT files in the proper directory (or subdirectories) and load them into memory. The Trigger Word will be applied to these new TXT files.
6. [Use the program](https://github.com/bntrtm/lora-tag-manager/wiki/Tag-Management) for your purposes to perfect image captioning for your LoRA dataset!

## Contributor Expectations

Feel free to contribute to the project! When doing so, be sure to follow the [Python style guide](https://peps.python.org/pep-0008/).

Try to include unit tests for your feature contributions where possible under `tests/`.

Merge commits will not be accepted; when using `git pull`, please rebase your local changes onto the remote branch you are pulling, rather than making a merge commit. An efficient way to automate this process is to set up a local git configuration with the following command:

```
git config pull.rebase true
```
