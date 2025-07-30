
import os
import base64
import shutil

class MetaFile():
    def __init__(self, name, localPath, encodeFolder) -> None:
        self.localPath = localPath
        self.name = name
        self.fileName = os.path.basename(self.localPath)
        self.encodeFolder = encodeFolder
        self.localDictName = "fileDict"
        self.defaultFileContent = f"""import base64
{self.localDictName} = {{}}
def getFile(fileCodeName: str):
    global {self.localDictName}
    decodecFileContent = base64.b64decode({self.localDictName}[fileCodeName]).decode()
    return decodecFileContent

def getFileInBase64(fileCodeName: str):
    global {self.localDictName}
    return {self.localDictName}[fileCodeName]
"""

    def baseFileExists(self):
        return os.path.exists(self.localPath)

    def generateEncode(self):
        if self.baseFileExists():
            if not os.path.exists(self.encodeFolder):
                os.mkdir(self.encodeFolder)
                with open(self.encodeFilePath(), "w") as f:
                    f.write(f"{self.defaultFileContent}\n")
            with open(self.localPath, "rb") as file:
                value = base64.b64encode(file.read()).decode()
                result = f"""
{self.localDictName}["{self.name}"] = "{value}"
"""

                with open(self.encodeFilePath(), "a") as f:
                    f.write(result)

    def encodeFilePath(self):
        return f"{self.encodeFolder}/__init__.py"

    @staticmethod
    def decodeMetaFile(base64Contents: str):
        decodecFileContent  = base64.b64decode(base64Contents).decode()
        return decodecFileContent

def getScriptPath():
    return f'{os.path.dirname(os.path.realpath(__file__)).replace(os.path.basename(__file__), "")}'

print("META FILES PATH: ", getScriptPath())
IMAGES_FILES_FOLDER = f"{getScriptPath()}/src/impyrium/images"

metaFolders = [
    IMAGES_FILES_FOLDER
]

files = [
    MetaFile("logo", f"{getScriptPath()}/graphics/imperium.png", IMAGES_FILES_FOLDER),
    MetaFile("cancel_button", f"{getScriptPath()}/graphics/cancel_button.png", IMAGES_FILES_FOLDER),
    MetaFile("default_device_logo", f"{getScriptPath()}/graphics/I.png", IMAGES_FILES_FOLDER)
]

def generateFiles(metaFolders=metaFolders, files=files):
    print("Generating meta files...")
    for folder in metaFolders:
        if os.path.exists(folder):
            shutil.rmtree(folder)
    for file in files:
        file.generateEncode()

def getBase64File(fileCodeName):
    f = files[fileCodeName]
    if f.baseFileExists():
        with open(f.localPath, "rb") as file:
            return base64.b64encode(file.read()).decode()
    else:
        return None

if __name__ == "__main__":
    generateFiles()
    print("Generated meta files.")
    for file in files:
        print(f"{file.name}: {file.encodeFilePath()}")
