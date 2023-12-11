
class DefaultFile():
    defaultFiles = []

    def __init__(self, path, contents, shouldWriteFun=lambda: True) -> None:
        self.path = path
        self.contents = contents
        self.shouldWriteFun = shouldWriteFun
        DefaultFile.defaultFiles.append(self)

    def shouldWrite(self):
        return self.shouldWriteFun()

