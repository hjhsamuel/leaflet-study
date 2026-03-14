import json
import sys
from typing import Optional

from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QTimer, QUrl, Signal, Slot, QObject
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidgetItem, QListWidget, QHBoxLayout, QMainWindow, QApplication
from qfluentwidgets import TransparentToolButton, TextEdit, ListWidget, PushButton
from qfluentwidgets import FluentIcon as FIF

from component.resource import resource_path
from component.widgets.navigation import SegmentedPivot

class MapBridge(QObject):
    route_steps = Signal(list)

    route_markers = Signal(list)
    route_marker_event = Signal(dict)

    error_msg = Signal(str)

    @Slot(list)
    def onRouteSteps(self, steps):
        self.route_steps.emit(steps)

    @Slot(list)
    def onRouteMarkers(self, markers):
        self.route_markers.emit(markers)

    @Slot(str)
    def onError(self, msg: str):
        self.error_msg.emit(msg)

    @Slot(dict)
    def onRouteMarkerEvent(self, info):
        self.route_marker_event.emit(info)


class MapWidget(QWebEngineView):
    loaded = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        self.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)

        self._ready = False
        self.loadFinished.connect(self._on_load_finished)

        self.bridge = MapBridge()
        self.channel = QWebChannel()
        self.channel.registerObject('bridge', self.bridge)
        self.page().setWebChannel(self.channel)

        file_path = resource_path('../static/web/leaflet.html')
        self.load(QUrl.fromLocalFile(file_path))

    def _on_load_finished(self, ok):
        if ok:
            self._ready = True
            self.loaded.emit()

    def _run_js(self, js_code):
        if self._ready:
            self.page().runJavaScript(js_code)
        else:
            self.loaded.connect(lambda: self.page().runJavaScript(js_code))

    def set_center(self, lng, lat, zoom=17):
        js_code = f"map.setView([{lat}, {lng}], {zoom});"
        self._run_js(js_code)

    def draw_route(self, route_id: int, polyline: str, steps: list) -> Optional[Exception]:
        lines = []
        parts = polyline.split(';')
        for part in parts:
            points = part.split(',')
            if len(points) != 2:
                return Exception('invalid polyline')
            lines.append([points[1], points[0]])
        if len(lines) == 0:
            return Exception('invalid polyline')
        param = [{'id': route_id, 'polyline': lines, 'steps': steps}]
        data = json.dumps(param)
        js_code = f'drawRoute({data});'
        self._run_js(js_code)
        return None

    def select_route(self, route_id: int):
        js_code = f"selectRoute({route_id});"
        self._run_js(js_code)

    def add_markers(self, markers):
        data = json.dumps(markers)
        js_code = f'addMarkers({data});'
        self._run_js(js_code)

    def clear_markers(self):
        js_code = f'clearMarkers();'
        self._run_js(js_code)


class FluentSlidePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Widget | Qt.WindowType.FramelessWindowHint)

        self.panel_width = 340
        self.setFixedWidth(self.panel_width)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tab_widget = SegmentedPivot(self)
        self.tab_widget.setAutoFillBackground(True)
        layout.addWidget(self.tab_widget, alignment=Qt.AlignmentFlag.AlignTop)

        self.toggle_btn = TransparentToolButton(FIF.MENU, parent)
        self.toggle_btn.setFixedSize(40, 40)
        self.toggle_btn.clicked.connect(self.toggle)

        layout.addStretch()

        # 动画
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(250)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.opened = False

        QTimer.singleShot(0, self.init_position)

    def init_position(self):
        p = self.parent()

        self.setGeometry(p.width(), 0, self.panel_width, p.height())

        self.update_button()

    def open(self):
        parent = self.parent()

        start = QRect(parent.width(), 0, self.width(), parent.height())
        end = QRect(parent.width() - self.width(), 0, self.width(), parent.height() // 2)

        self.animation.stop()
        self.animation.setStartValue(start)
        self.animation.setEndValue(end)
        self.animation.start()

        self.opened = True

        self.update_button()

    def close(self):
        parent = self.parent()

        start = QRect(parent.width() - self.width(), 0, self.width(), parent.height())
        end = QRect(parent.width(), 0, self.width(), parent.height())

        self.animation.stop()
        self.animation.setStartValue(start)
        self.animation.setEndValue(end)
        self.animation.start()

        self.opened = False

        self.update_button()

    def toggle(self):
        if self.opened:
            self.close()
        else:
            self.open()

    def update_button(self):
        p = self.parent()

        if self.opened:
            x = p.width() - self.width() - 40
        else:
            x = p.width() - 40

        # y = p.height() // 2 - 20
        y = 0
        self.toggle_btn.setGeometry(x, y, 40, 40)

    def update_layout(self):
        parent = self.parent()

        if self.opened:
            x = parent.width() - self.panel_width
        else:
            x = parent.width()

        self.setGeometry(x, 0, self.panel_width, parent.height())

        self.tab_widget.setFixedHeight(max(self.height() // 2, 240))

        self.update_button()

    def add_tab(self, route_key: str, name: str, w: QWidget):
        self.tab_widget.add_tab_page(route_key, name, w)

    def set_current_tab(self, index):
        self.tab_widget.set_current_tab(index)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setMinimumSize(800, 600)

        self.container = QWidget()
        self.setCentralWidget(self.container)
        self.vbox_layout = QVBoxLayout(self.container)
        self.vbox_layout.setContentsMargins(0, 0, 0, 0)

        self.hbox_layout = QHBoxLayout()
        self.hbox_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.vbox_layout.addLayout(self.hbox_layout)

        self.btn = PushButton('绘制路径轨迹')
        self.btn.clicked.connect(self._draw_routes)
        self.hbox_layout.addWidget(self.btn)

        self.prt_scr_btn = PushButton('截图')
        self.prt_scr_btn.clicked.connect(self._capture_image)
        self.hbox_layout.addWidget(self.prt_scr_btn)

        self.map = MapWidget(self)
        self.map.bridge.route_steps.connect(self._show_route_steps)
        self.map.bridge.route_marker_event.connect(self._route_marker_event)
        self.vbox_layout.addWidget(self.map, stretch=1)

        self.side_panel = FluentSlidePanel(self.map)
        self.side_panel.setGeometry(self.width(), 0, self.side_panel.width(), self.height())
        self.side_panel.update_button()
        self._init_side_panel()

    def _init_side_panel(self):
        # 导航
        self.driving_steps = TextEdit()
        self.driving_steps.setReadOnly(True)
        self.side_panel.add_tab('driving_steps', '导航', self.driving_steps)

        # 途径点
        self.driving_waypoints = ListWidget()
        self.driving_waypoints.setDragEnabled(True)
        self.driving_waypoints.setAcceptDrops(True)
        self.driving_waypoints.setDropIndicatorShown(True)
        self.driving_waypoints.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.driving_waypoints.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.side_panel.add_tab('driving_waypoints', '途径点', self.driving_waypoints)

        self.side_panel.set_current_tab(0)

    def _draw_routes(self):
        path = "D:/workspace/driving.json"
        with open(path, 'r', encoding='utf-8') as f:
            info = json.load(f)
            index = 1
            for item in info['route']['paths']:
                steps = []
                lines = []
                for step in item['steps']:
                    lines.append(step['polyline'])
                    steps.append({
                        'road_name': step['road_name'] if 'road_name' in step.keys() else '',
                        'step_distance': step['step_distance'],
                        'instruction': step['instruction']
                    })
                self.map.draw_route(index, ';'.join(lines), steps)
                index += 1
        self.map.select_route(1)

    def _capture_image(self):
        pixmap = self.map.grab()
        pixmap.save('D:/workspace/out.png')
        print('-------- Saved ----------')

    def _show_route_steps(self, steps):
        self.driving_steps.clear()
        lines = []
        for step in steps:
            road_name = step["road_name"] if step["road_name"] else '无名道路'
            lines.append(f'**{road_name}**')
            lines.append('')
            lines.append(f'  {step["instruction"]}  ')
        self.driving_steps.setMarkdown(' \n '.join(lines))

    def _route_marker_event(self, info):
        if info['op'] == 1:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, info['id'])
            item.setText(f'{info["lng"]}, {info["lat"]}')
            self.driving_waypoints.addItem(item)
        elif info['op'] == 2:
            for index in range(self.driving_waypoints.count()):
                item = self.driving_waypoints.item(index)
                if item.data(Qt.ItemDataRole.UserRole) == info['id']:
                    self.driving_waypoints.takeItem(index)
                    del item
                    return

    def _toggle_panel(self):
        self.side_panel.toggle()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.side_panel.update_layout()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    w = MainWindow()
    w.show()

    sys.exit(app.exec())
