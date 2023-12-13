import os
from .default_file import DefaultFile

# import for the run effect
from . import py_file_defaults
from . import json_file_defaults
from . import ahk_get_file_script


def writeFiles(parentFolder, createExamples):
    os.makedirs(parentFolder, exist_ok=True)
    for file in DefaultFile.defaultFiles:
        file.setParent(parentFolder)
        if not createExamples and file.isExample:
            continue
        if file.shouldWrite() and not file.exists():
            p = os.path.dirname(f"{parentFolder}/{file.path}")
            if not os.path.exists(p):
                os.makedirs(p, exist_ok=True)
            file.write()
