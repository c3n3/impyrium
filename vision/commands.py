
class Command():
    def __init__(self, name, commandType, callback):
        self.name = name
        self.type = commandType
        self.callback = callback


def sendSomething(command, args):
    print("Something got called")
