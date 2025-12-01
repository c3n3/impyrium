from .default_files import defaults
from .default_files.ahk_get_file_script import ahkGetFile
from . import signals
from . import images
from PySide6.QtWidgets import QFileDialog
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import QByteArray
from . import work_queue, router
from .popups.single_select_popup import SingleSelectPopup
from .popups import build_a_popup

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

def isWayland():
    if os.name != 'posix':
        return False
    return os.environ.get('XDG_SESSION_TYPE') == 'wayland'

def getFileConsumer(fun, directory, types):
    def work():
        file = getFileFromDialog(types, directory)
        fun(file)
    work_queue.schedule(work)


def selectItemPopup(fun, items, name, devices):
    def work():
        dialog = SingleSelectPopup(fun, name, items, devices)
        devs, res = dialog.popUp()
        fun((devs, res))
    work_queue.schedule(work)

def buildPopupConsumer(fun, name, components, devices):
    def work():
        dialog = build_a_popup.BuildAPopup(fun, name, devices, components)
        devs, res = dialog.popUp()
        fun((devs, res))
    work_queue.schedule(work)

def sendUpdateDeviceListSignal():
    work_queue.schedule(lambda: router.send(signals.DEVICE_LIST_UPDATE, None))
