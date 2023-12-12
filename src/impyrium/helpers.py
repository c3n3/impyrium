from .default_files import defaults
from .default_files.ahk_get_file_script import ahkGetFile

import os

def getCurrentlySelectedFile():
    TEMP_FILE = "__currently_selected__.txt"

    if ahkGetFile.exists():
        os.system(f"\"{defaults.AHK}\" {ahkGetFile.getPath()} {TEMP_FILE}")

        f = open(TEMP_FILE)
        result = f.read()
        f.close()

        os.remove(TEMP_FILE)
        return result
    return ""
