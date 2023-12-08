from PyQt6.QtWidgets import QFileDialog

def getFile(types):
    file, _ = QFileDialog.getOpenFileName(
        None,
        "Select a file...",
        "",
        f"{types};;"
    )
    return file
