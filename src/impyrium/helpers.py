from .default_files import defaults
from .default_files.ahk_get_file_script import ahkGetFile

from PyQt6.QtWidgets import QFileDialog

import os

def getCurrentlySelectedFile():
    TEMP_FILE = "__currently_selected__.txt"

    if ahkGetFile.exists():
        if not os.path.exists(defaults.AHK):
            print("You need AHK installed to get currently selected file")
            return ""

        os.system(f"\"{defaults.AHK}\" {ahkGetFile.getPath()} {TEMP_FILE}")

        f = open(TEMP_FILE)
        result = f.read()
        f.close()

        os.remove(TEMP_FILE)
        return result
    return ""

def getFileFromDialog(types, directory):
    file, _ = QFileDialog.getOpenFileName(
        None,
        "Select a file...",
        directory,
        f"{types};;"
    )
    return file
