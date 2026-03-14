from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from qfluentwidgets import SegmentedWidget


class SegmentedPivot(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.vbox_layout = QVBoxLayout(self)
        self.vbox_layout.setContentsMargins(0, 0, 0, 0)

        # 分段控件
        self.pivot = SegmentedWidget()
        self.vbox_layout.addWidget(self.pivot, 0, Qt.AlignmentFlag.AlignLeft)

        # 页面容器
        container = QWidget()
        container.setObjectName('pivot_tab_page')
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(15, 15, 15, 15)
        container_layout.setSpacing(0)

        # 堆叠页面
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.currentChanged.connect(self.onCurrentIndexChanged)
        container_layout.addWidget(self.stacked_widget)

        self.vbox_layout.addWidget(container)

        self.setStyleSheet("""
        SegmentedPivot {
            padding-left: 10px;
            font: 14px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC';
            color: black;
        }
        #pivot_tab_page {
            border: 1px solid #d0d0d0;
            border-radius: 8px;
            background-color: #fafafa;
        }""")

    def add_tab_page(self, route_key: str, name: str, w: QWidget):
        w.setObjectName(route_key)
        self.stacked_widget.addWidget(w)
        self.pivot.addItem(
            routeKey=route_key,
            text=name,
            onClick=lambda: self.stacked_widget.setCurrentWidget(w)
        )

    def onCurrentIndexChanged(self, index):
        w = self.stacked_widget.widget(index)
        self.pivot.setCurrentItem(w.objectName())

    def set_current_tab(self, index):
        w = self.stacked_widget.widget(index)
        if w:
            self.stacked_widget.setCurrentIndex(index)
            self.pivot.setCurrentItem(w.objectName())
