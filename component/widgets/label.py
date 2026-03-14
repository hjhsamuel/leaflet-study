from typing import Union

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from qfluentwidgets import FluentIconBase, IndicatorPosition, IconWidget


class IconLabel(QWidget):
    def __init__(self, title: str, icon: Union[QIcon, str, FluentIconBase], indicator=IndicatorPosition.RIGHT, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.label = QLabel(title)
        self.icon = IconWidget(icon, self)

        font_size = self.label.fontInfo().pointSize()
        icon_size = font_size // 3 + font_size
        self.icon.setFixedSize(icon_size, icon_size)

        if indicator == IndicatorPosition.LEFT:
            layout.addWidget(self.icon, alignment=Qt.AlignmentFlag.AlignLeft)
            layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignLeft)
        else:
            layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignLeft)
            layout.addWidget(self.icon, alignment=Qt.AlignmentFlag.AlignLeft)

    def text(self):
        return self.label.text()

    def setToolTip(self, arg__1):
        self.icon.setToolTip(arg__1)

