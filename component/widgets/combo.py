from typing import List

from PIL.ImageQt import QPixmap
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from qfluentwidgets import DropDownToolButton, RoundMenu, CheckBox, IconWidget, Action

from component.widgets.label import IconLabel


class MultiCombo(QWidget):
    select_item_changed = Signal(object)  # List[Tuple[str, object]]

    def __init__(self, title: str = None, icon=None, parent=None):
        super().__init__(parent)

        self.item_cnt = 0
        self.selected_items = set()

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.icon_widget = None
        self.label = None
        self.btn = DropDownToolButton()
        self.menu = RoundMenu()

        if title:
            if icon is not None:
                self.label = IconLabel(title, icon)
            else:
                self.label = QLabel(title)
            self.layout.addWidget(self.label, 0, Qt.AlignmentFlag.AlignLeft)

        self.init_button()

    def init_button(self):
        self.btn.setMinimumWidth(160)
        self.btn.setMaximumWidth(320)

        self.checkboxes = []

        self.select_all_cb = CheckBox('全选', self.menu)
        self.select_all_cb.stateChanged.connect(self.on_select_all_toggled)
        self.menu.addWidget(self.select_all_cb)

        self.btn.setMenu(self.menu)
        self.layout.addWidget(self.btn, 1, Qt.AlignmentFlag.AlignLeft)

    def on_select_all_toggled(self, state):
        if state == Qt.CheckState.Checked.value:
            for cb in self.checkboxes:
                cb.blockSignals(True)
                cb.setChecked(True)
                cb.blockSignals(False)
                self.selected_items.add((cb.text(), cb.user_data))
        elif state == Qt.CheckState.Unchecked.value:
            for cb in self.checkboxes:
                cb.blockSignals(True)
                cb.setChecked(False)
                cb.blockSignals(False)
            self.selected_items.clear()

        self.update_button_text()

    def update_button_text(self):
        signal_data = []
        if self.selected_items:
            label_text = []
            for text, user_data in self.selected_items:
                label_text.append(text)
                signal_data.append((text, user_data))
            self.btn.setText(', '.join(label_text))
        else:
            self.btn.setText('')
        self.select_item_changed.emit(signal_data)

    def add(self, name: str, user_data: object):
        cb = CheckBox(name, self.menu)
        cb.user_data = user_data
        cb.stateChanged.connect(lambda state, c=cb: self.on_item_toggled(c, state))
        self.menu.addWidget(cb)
        self.checkboxes.append(cb)

        self.item_cnt += 1

    def on_item_toggled(self, c, state):
        item_tuple = (c.text(), c.user_data)
        if state == Qt.CheckState.Checked.value:
            self.selected_items.add(item_tuple)
        else:
            self.selected_items.discard(item_tuple)
        self.update_button_text()
        self.sync_select_all_state()

    def sync_select_all_state(self):
        total = len(self.checkboxes)
        checked = sum(1 for cb in self.checkboxes if cb.isChecked())

        self.select_all_cb.blockSignals(True)
        if checked == total:
            self.select_all_cb.setCheckState(Qt.CheckState.Checked)
        elif checked == 0:
            self.select_all_cb.setCheckState(Qt.CheckState.Unchecked)
        else:
            self.select_all_cb.setCheckState(Qt.CheckState.PartiallyChecked)
        self.select_all_cb.blockSignals(False)

    def set_current_data(self, datas: List[object]):
        data_set = set()
        for data in datas:
            data_set.add(data)
        for cb in self.checkboxes:
            if cb.user_data in data_set:
                cb.setChecked(True)

