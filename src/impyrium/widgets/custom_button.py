from PySide6.QtWidgets import QPushButton, QWidget
from .. import common_css

class ImpPushButton(QPushButton):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.unfocus()
        self.setStyleSheet(self.getStyle())
        self.pressed.connect(self.onPress)
        self.released.connect(self.onRelease)

    def onPress(self):
        self.focus()

    def onRelease(self):
        self.unfocus()

    def getStyle(self):
        return f"""
        QPushButton {{
            background-color: {self.backgroundColor};
        }}
        QPushButton:hover {{
            background-color: {self.highlightColor};
            color: {self.textColor};
        }}
        """

    def focus(self):
        self.highlightColor = common_css.FOCUS_ACCENT_COLOR
        self.backgroundColor = common_css.FOCUS_MAIN_COLOR
        self.textColor = common_css.FOCUS_TEXT_COLOR
        self.setStyleSheet(self.getStyle())

    def unfocus(self):
        self.highlightColor = common_css.ACCENT_COLOR
        self.backgroundColor = common_css.MAIN_COLOR
        self.textColor = common_css.MAIN_TEXT_COLOR
        self.setStyleSheet(self.getStyle())
