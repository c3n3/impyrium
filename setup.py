from setuptools import setup

import os

def getScriptPath():
    return f'{os.path.dirname(os.path.realpath(__file__)).replace(os.path.basename(__file__), "")}'

if __name__ == "__main__":
    # Generate the files so using them in the lib works
    from pydoc import importfile
    metaFiles = importfile(f"{getScriptPath()}/src/impyrium/meta_files.py")
    metaFiles.generateFiles()
    setup()
