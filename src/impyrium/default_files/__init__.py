import os
from .default_file import DefaultFile

# import for the run effect
from . import py_file_defaults
from . import json_file_defaults

def writeFiles(parentFolder):
    os.makedirs(parentFolder, exist_ok=True)
    for file in DefaultFile.defaultFiles:
        p = os.path.dirname(f"{parentFolder}/{file.path}")
        os.makedirs(p, exist_ok=True)
        with open(f"{parentFolder}/{file.path}", 'w') as f:
            f.write(file.contents)
