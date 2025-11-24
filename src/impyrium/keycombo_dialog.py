import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QDialog, QMainWindow, QPushButton, QWidget, QVBoxLayout, QLabel, QComboBox, QHBoxLayout

from . import common_css

from .pyqt6_key_map import pyqt6Map

from .inputless_combo import InputlessCombo

class KeyComboDialog(QDialog):
    def __init__(self, doneFun, parent: QWidget = None):
        super().__init__(parent)
        self.doneFun = doneFun
        self.setStyleSheet(common_css.MAIN_STYLE)
        self.mainLayout = QVBoxLayout(self)
        self.instructions = QLabel(self)
        self.instructions.setText("Record key combo")
        self.setWindowTitle("Key Combo")
        self.setMinimumWidth(450)
        def createResultLabel():
            ret = QLabel(self)
            ret.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ret.setMinimumHeight(200)
            ret.setMinimumWidth(200)
            return ret

        self.results = createResultLabel()

        self.type = 'button'
        self.resultWidget = QWidget()
        self.resultLayout = QHBoxLayout()
        self.resultLayout.addWidget(self.results)
        self.resultWidget.setLayout(self.resultLayout)


        self.mainLayout.addWidget(self.instructions)
        self.mainLayout.addWidget(self.resultWidget)

        self.setLayout(self.mainLayout)
        self.keysList = set()
        self.pressed = set()
        self.keysIndex = 0


    def getString(self):
        keylist = []
        for key in self.keysList:
            if key is None:
                continue
            elif (hasattr(key, 'char')):
                keylist.append(key.char+"+")
            elif len(key.name) > 1:
                keylist.insert(0, f"<{key.name}>+")
            else:
                raise Exception("Invalid key" + key)
        return ("".join(keylist))[:-1]

    def keyPressEvent(self, event):
        self.pressed.add(pyqt6Map[event.key()])
        self.keysList.add(pyqt6Map[event.key()])
        self.results.setText(self.getString())
        self.update()

    def keyReleaseEvent(self, event):
        if pyqt6Map[event.key()] in self.pressed:
            self.pressed.remove(pyqt6Map[event.key()])
        if len(self.keysList) == 0:
            return
        self.doneFun(self.getString())
        self.close()


if __name__ == '__main__':
    class TestApp(QMainWindow):
        def __init__(self):
            super().__init__()

            self.setWindowTitle("My App")

            button = QPushButton("Press me for a dialog!")
            button.clicked.connect(self.button_clicked)
            self.setCentralWidget(button)

        def addInput(self, t, item):
            print(t, item)

        def button_clicked(self, s):
            print("click", s)

            dlg = KeyComboDialog(self.addInput, self)
            dlg.exec()

    app = QApplication(sys.argv)

    window = TestApp()
    window.show()

    app.exec()
