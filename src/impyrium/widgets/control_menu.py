from ..worker_thread import WorkerThread
from .. import control
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider
from PySide6.QtCore import Qt
from .custom_button import ImpPushButton

class ControlsScrollView(QWidget):
    def __init__(self, category, autoReserve, abilities=set(), onControlDeleted=None):
        super(ControlsScrollView, self).__init__()
        self.layout = QVBoxLayout(self)
        self.autoReserve = autoReserve
        self.onControlDeleted = onControlDeleted
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        controls = control.getControls()
        self.worker = WorkerThread()
        self.worker.start()
        self.count = 0
        self.category = category
        if category in controls:
            for c in controls[category]:
                mod = self.getObjectMod(c)
                if mod is None:
                    print(f"Mod is None for {c.name}, cannot do anything with this, please fix")
                    continue
                for item in mod:
                    self.layout.addWidget(item)
                    if not c.enabled or (not c.getRequiredAbilities().issubset(abilities) and not autoReserve):
                        item.hide()
                    else:
                        self.count += 1
        else:
            print("Could not find any controls for ", category)

    def generateButtonCallbackFun(self, ctrl: control.ControlButton, event):
        def fun():
            if ctrl.enabled:
                ctrl.handleGuiEvent(event, control.DeviceType.getControlDevList(ctrl, self.autoReserve))
        return fun

    def generateSliderCallbackFun(self, ctrl: control.ControlSlider):
        def fun(value):
            if ctrl.enabled:
                def item():
                    ctrl.setValueFromSlider(value)
                    ctrl.handleGuiEvent(control.ControlEvents.VALUE_SET, control.DeviceType.getControlDevList(ctrl, self.autoReserve))

                if 'event' in ctrl.data and ctrl.data['event'] is not None:
                    self.worker.removeItem(ctrl.data['event'])
                ctrl.data['event'] = self.worker.scheduleItem(0.5, item)
        return fun

    def generateDeleteCallback(self, ctrl, container_widget):
        """Generate a callback to delete a control."""
        def fun():
            # Call the control's onDelete callback if provided
            if ctrl.onDelete:
                ctrl.onDelete(ctrl)

            # Unregister the control
            control.unregisterControl(ctrl)

            # Remove the widget from the layout
            container_widget.setParent(None)
            container_widget.deleteLater()

            # Update count
            self.count -= 1

            # Notify parent if callback provided
            if self.onControlDeleted:
                self.onControlDeleted(ctrl)
        return fun

    def getObjectMod(self, ctrl):
        if type(ctrl) == control.ControlButton or type(ctrl) == control.ControlFile or issubclass(type(ctrl), control.ControlButton):
            # If deletable, wrap in a container with delete button
            if ctrl.deletable:
                container = QWidget()
                layout = QHBoxLayout(container)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(2)

                button = ImpPushButton()
                button.setMinimumHeight(25)
                button.setText(ctrl.name)
                button.pressed.connect(self.generateButtonCallbackFun(ctrl, control.ControlEvents.BUTTON_PRESS))
                button.released.connect(self.generateButtonCallbackFun(ctrl, control.ControlEvents.BUTTON_RELEASE))

                delete_button = ImpPushButton()
                delete_button.setText("✕")
                delete_button.setFixedWidth(25)
                delete_button.setMinimumHeight(25)
                delete_button.setToolTip(f"Delete '{ctrl.name}'")
                delete_button.setStyleSheet("QPushButton { color: red; font-weight: bold; }")
                delete_button.clicked.connect(self.generateDeleteCallback(ctrl, container))

                layout.addWidget(button, stretch=1)
                layout.addWidget(delete_button, stretch=0)
                return [container]
            else:
                button = ImpPushButton()
                button.setMinimumHeight(25)
                button.setText(ctrl.name)
                button.pressed.connect(self.generateButtonCallbackFun(ctrl, control.ControlEvents.BUTTON_PRESS))
                button.released.connect(self.generateButtonCallbackFun(ctrl, control.ControlEvents.BUTTON_RELEASE))
                return [button]
        if type(ctrl) == control.ControlSlider:
            ret = QSlider(Qt.Orientation.Horizontal)
            res = ctrl.generateSliderValues()
            ret.setMinimum(res[0])
            ret.setMaximum(res[1])
            ret.setMinimumHeight(25)
            label = QLabel(ctrl.name)
            ret.valueChanged.connect(self.generateSliderCallbackFun(ctrl))
            label.setBuddy(ret)
            # ret.setStyleSheet("QWidget{ border-right: 1px solid grey; border-left: 1px solid grey }")
            return [label, ret]
        return None

class ControlsTypeSection(QWidget):
    def __init__(self, category, autoReserve, abilities=set(), parent: QWidget = None):
        super().__init__(parent)
        container = QWidget()
        containerLayout = QVBoxLayout()
        subwidget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        button = ImpPushButton(container)
        button.setText(category)
        button.clicked.connect(self.buttonPressed)
        subwidget.setStyleSheet('QWidget{ border: 1px solid grey; }')
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(button)
        self.controlsView = ControlsScrollView(category, autoReserve, abilities)
        self.controlsView.setStyleSheet(f"QWidget{{ border: revert; }}")
        if self.controlsView.count > 0:
            self.showing = True
            self.controlsView.show()
        else:
            self.showing = False
            self.controlsView.hide()
        layout.addWidget(self.controlsView)
        subwidget.setLayout(layout)
        containerLayout.addWidget(subwidget)
        self.setLayout(containerLayout)

    def buttonPressed(self):
        self.showing = not self.showing
        if (self.showing):
            self.controlsView.show()
        else:
            self.controlsView.hide()
