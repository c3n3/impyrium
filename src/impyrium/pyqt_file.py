from PyQt6.QtWidgets import QFileDialog

def getFile(types, directory):
    file, _ = QFileDialog.getOpenFileName(
        None,
        "Select a file...",
        directory,
        f"{types};;"
    )
    return file
