from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget, QBoxLayout
from qfluentwidgets import MessageBoxBase, TitleLabel


class CustomMessageBox(MessageBoxBase):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.title_label = TitleLabel('', self)
        self.viewLayout.addWidget(self.title_label)

        self.vbox_layout = QVBoxLayout()
        self.viewLayout.addLayout(self.vbox_layout)

        self.yesButton.setText('保存')
        self.cancelButton.setText('取消')

        self.widget.setMinimumWidth(360)

    def add_widget(self, w: QWidget, stretch: int = 0, alignment = Qt.AlignmentFlag.AlignLeft):
        self.vbox_layout.addWidget(w, stretch, alignment)

    def add_layout(self, layout: QBoxLayout):
        self.vbox_layout.addLayout(layout, 1)
