from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import IndeterminateProgressRing


class LoadingProgressRing(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet("background-color: rgba(0, 0, 0, 50);")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.loading = IndeterminateProgressRing(self)
        self.loading.setFixedSize(50, 50)
        layout.addWidget(self.loading, alignment=Qt.AlignmentFlag.AlignCenter)

        self.hide()

    def resizeEvent(self, event):
        if self.parent():
            self.setGeometry(self.parent().rect())
        super().resizeEvent(event)

    def display(self):
        self.loading.start()
        self.show()

    def undisplay(self):
        self.hide()
        self.loading.stop()