from .default_files import defaults
from .default_files.ahk_get_file_script import ahkGetFile
from . import signals
from .aitpi_signal import AitpiSignal
from . import images
from PySide6.QtWidgets import QFileDialog
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import QByteArray

import os

def getCurrentlySelectedFile():
    TEMP_FILE = "__currently_selected__.txt"

    if ahkGetFile.exists():
        if not os.path.exists(defaults.AHK):
            print("You need AHK installed to get currently selected file")
            return ""

        os.system(f"\"{defaults.AHK}\" {ahkGetFile.getPath()} {TEMP_FILE}")

        f = open(TEMP_FILE)
        result = f.read()
        f.close()

        os.remove(TEMP_FILE)
        return result
    return ""

def getFileFromDialog(types, directory):
    file, _ = QFileDialog.getOpenFileName(
        None,
        "Select a file...",
        directory,
        f"{types};;"
    )
    return file

def addStatusEntry(text):
    AitpiSignal.send(signals.ADD_SIDEBAR_STATUS_ENTRY, ("ADD", text))

def removeStatusEntry(text):
    AitpiSignal.send(signals.ADD_SIDEBAR_STATUS_ENTRY, ("REMOVE", text))

def getImageForPyQt(imageCodeName: str):
    img = images.getFileInBase64(imageCodeName)
    # ... (assuming you have a QLabel named 'image_label' in your UI)

    # Convert the base64 string back to QByteArray
    byte_array = QByteArray.fromBase64(img.encode('utf-8'))

    # Load the image from the QByteArray
    image = QImage()
    image.loadFromData(byte_array)

    # Create a QPixmap from the QImage
    pixmap = QPixmap.fromImage(image)
    return pixmap
