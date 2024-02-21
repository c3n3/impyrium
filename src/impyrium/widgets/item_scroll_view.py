from PyQt6.QtWidgets import (
    QScrollArea,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtCore import Qt, pyqtBoundSignal, pyqtSignal, pyqtSlot, QTimer

class ItemScrollView(QScrollArea):
    def __init__(self, items, parent: QWidget = None) -> None:
        super(ItemScrollView, self).__init__(parent)
        widget = QWidget()
        self.mainLayout = QVBoxLayout(widget)
        self.mainLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.items = items
        for item in items:
            self.mainLayout.addWidget(item)
        self.setWidget(widget)
        self.setWidgetResizable(True)
        self.selectedItems = set()

    def addItem(self, item):
        self.mainLayout.addWidget(item)

    def removeItem(self, item):
        self.mainLayout.removeWidget(item)

    def toggleIndexHighlight(self, index):
        if index is None or index >= len(self.items):
            return
        widget = self.items[index]
        if index not in self.selectedItems:
            widget.setStyleSheet("background-color: red")
            widget.update()
            self.selectedItems.add(index)
        else:
            widget.setStyleSheet("")
            widget.update()
            self.selectedItems.remove(index)
