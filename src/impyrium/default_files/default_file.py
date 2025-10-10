import os

class DefaultFile():
    defaultFiles = []

    def __init__(self, path, contents, isExample = True, shouldWriteFun=lambda: True) -> None:
        self.path = path
        self.contents = contents
        self.shouldWriteFun = shouldWriteFun
        self.isExample = isExample
        self.parentFolder = ""
        DefaultFile.defaultFiles.append(self)

    def shouldWrite(self):
        return self.shouldWriteFun()

    def setParent(self, parent):
        self.parentFolder = parent

    def write(self):
        print("Writing", self.getPath())
        with open(self.getPath(), 'w') as f:
            f.write(self.contents)

    def getPath(self):
        return f"{self.parentFolder}/{self.path}"

    def exists(self):
        return os.path.exists(self.getPath())
