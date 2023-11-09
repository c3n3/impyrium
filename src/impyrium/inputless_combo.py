from PyQt6.QtCore import QEvent, QObject
from PyQt6.QtWidgets import QWidget, QComboBox


class InputlessCombo(QComboBox):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)

        self.installEventFilter(self)
        self.view().installEventFilter(self)

    def eventFilter(self, a0: QObject, a1: QEvent) -> bool:
        if a1.type() == QEvent.Type.KeyPress:
            self.parent().keyPressEvent(a1)
            return True
        if a1.type() == QEvent.Type.KeyRelease:
            self.parent().keyReleaseEvent(a1)
            return True
        return super().eventFilter(a0, a1)
