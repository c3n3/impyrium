
import os
import base64

class MetaFile():
    def __init__(self, localPath, encodeFolder) -> None:
        self.localPath = localPath
        self.fileName = os.path.basename(self.localPath)
        self.encodeFolder = encodeFolder

    def baseFileExists(self):
        return os.path.exists(self.localPath)
    
    def generateEncode(self):
        if self.baseFileExists():
            if not os.path.exists(self.encodeFolder):
                os.mkdir(self.encodeFolder)
                with open(f"{self.encodeFolder}/__init__.py", "w") as f:
                    f.write("\n")
            with open(self.localPath, "rb") as file:
                value = base64.b64encode(file.read()).decode()
                result = f"""
value = "{value}"
                         """

                with open(self.encodeFilePath(), "w") as f:
                    f.write(result)

    def encodeFilePath(self):
        return f"{self.encodeFolder}/{self.fileName}__.py"

    def getFilePath(self, outputFolder=None):
        if self.baseFileExists():
            return self.localPath
        elif os.path.exists(self.encodeFolder):
            if not os.path.exists(f"{self.encodeFolder}/{self.fileName}") and os.path.exists(self.encodeFilePath()):
                from pydoc import importfile
                pyfile = importfile(self.encodeFilePath())
                fileResult = pyfile.value
                if outputFolder is None:
                    outputFolder = self.encodeFolder
                if not os.path.isdir(outputFolder):
                    os.mkdir(outputFolder)
                with open(f"{outputFolder}/{self.fileName}", "wb") as f:
                    f.write(base64.b64decode(fileResult))

            if os.path.exists(f"{outputFolder}/{self.fileName}"):
                return f"{outputFolder}/{self.fileName}"
        return None



def getScriptPath():
    return f'{os.path.dirname(os.path.realpath(__file__)).replace(os.path.basename(__file__), "")}'


META_FILES_FOLDER = f"{getScriptPath()}/_meta_files_"

files = {
    "logo": MetaFile(f"{getScriptPath()}/../../graphics/imperium.jpg", META_FILES_FOLDER),
    "cancel_button": MetaFile(f"{getScriptPath()}/../../graphics/cancel_button.png", META_FILES_FOLDER),
    "default_device_logo": MetaFile(f"{getScriptPath()}/../../graphics/I.png", META_FILES_FOLDER)
}

def generateFiles():
    for key, value in files.items():
        value.generateEncode()


def getFile(fileCodeName):
    from . import getTempFolder

    f = files[fileCodeName]

    generatedFolder = f"{getTempFolder()}/meta_files/"

    path = f.getFilePath(generatedFolder)

    return path
