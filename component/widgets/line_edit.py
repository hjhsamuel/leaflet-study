from typing import List

from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from qfluentwidgets import TransparentToolButton, LineEdit, LineEditButton, RoundMenu
from qfluentwidgets.common.icon import FluentIcon as FIF


class MenuItem(QWidget):
    def __init__(self, name: str, remove_callback, user_data: object = None):
        super().__init__()
        self.name = name
        self.remove_callback = remove_callback
        self.user_data = user_data

        self.layout = QHBoxLayout(self)

        self.delete_btn = TransparentToolButton(FIF.DELETE)
        self.delete_btn.setFixedSize(18, 18)
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.clicked.connect(lambda: self.remove_callback(self.name))

        self.layout.addWidget(self.delete_btn, 0, Qt.AlignmentFlag.AlignLeft)

        self.label = QLabel(name)

        self.layout.addWidget(self.label, 1, Qt.AlignmentFlag.AlignLeft)
        self.layout.addStretch()


class ArrayLineEdit(LineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.items = []  # type: List[MenuItem]
        self.menu = None

        self.returnPressed.connect(self.add_item_from_input)

        self.drop_btn = LineEditButton(FIF.ARROW_DOWN, self)
        self.drop_btn.setFixedSize(28, 28)
        self.drop_btn.clicked.connect(self.show_menu)
        self.hBoxLayout.addWidget(self.drop_btn, 0, Qt.AlignmentFlag.AlignRight)

    def add_item_from_input(self):
        name = self.text().strip()
        if not name:
            return

        index = self.find_name(name)
        if index < 0:
            item = MenuItem(name, self.remove_item)
            item.setFixedHeight(30)
            self.items.append(item)
        self.clear()

    def find_name(self, name: str) -> int:
        for i, item in enumerate(self.items):
            if item.name == name:
                return i
        return -1

    def remove_item(self, name: str):
        index = self.find_name(name)
        if index >= 0:
            self.items.pop(index)
            self.show_menu()

    def show_menu(self):
        if not self.items:
            return

        if self.menu:
            self.menu.deleteLater()

        menu = RoundMenu(parent=self)
        menu.setContentsMargins(0, 0, 0, 0)
        menu.setItemHeight(32)
        menu.view.setMaxVisibleItems(5)
        menu.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.menu = menu

        for item in self.items:
            item.setFixedWidth(self.width() + item.delete_btn.width())
            item.setFixedHeight(self.height())
            item.label.setFont(self.font())
            menu.addWidget(item, selectable=False)

        x = -menu.width() // 2 + menu.layout().contentsMargins().left() + self.width() // 2
        pd = self.mapToGlobal(QPoint(x, self.height()))
        menu.exec_(pd)

    def value(self) -> List[str]:
        vals = []
        for item in self.items:
            vals.append(item.name)
        return vals

    def load_value(self, names: List[str]):
        for name in names:
            item = MenuItem(name, self.remove_item)
            item.setFixedHeight(30)
            self.items.append(item)
