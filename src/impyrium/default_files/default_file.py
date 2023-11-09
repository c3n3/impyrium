
class DefaultFile():
    defaultFiles = []

    def __init__(self, path, contents) -> None:
        self.path = path
        self.contents = contents
        DefaultFile.defaultFiles.append(self)
