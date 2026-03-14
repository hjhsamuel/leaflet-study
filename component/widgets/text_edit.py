import json

from PySide6.QtCore import QSize, Qt, QRect
from PySide6.QtGui import QPainter, QColor, QTextFormat
from PySide6.QtWidgets import QWidget, QPlainTextEdit, QTextEdit
from qfluentwidgets import InfoBar, InfoBarPosition


class TextLineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return self.editor.line_number_size()

    def paintEvent(self, event):
        self.editor.paint_line_number_area(event)


class TextEditBase(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)

        self.line_number_area = TextLineNumberArea(self)

        self.blockCountChanged.connect(self._update_line_number_width)
        self.updateRequest.connect(self._update_line_number_area)
        self.cursorPositionChanged.connect(self._highlight_current_line)

        self._update_line_number_width(0)
        self._highlight_current_line()

        self.setStyleSheet("""
        QPlainTextEdit {
            background-color: #1e1e2f;
            color: #f8f8f2;
            border-radius: 8px;
            padding: 0px;
            font-family: Consolas;
            font-size: 14px;
        }
        QScrollBar:vertical {
            border: none;
            background: #2e2e3f;
            width: 20px;
            margin: 0px 0px 0px 0px;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical {
            background: #55557f;
            min-height: 20px;
            border-radius: 3px;
        }
        QScrollBar::add-line, QScrollBar::sub-line {
            height: 0px;
        }
        QScrollBar:horizontal {
            border: none;
            background: #2e2e3f;
            height: 10px;
            margin: 0px 0px 0px 0px;
            border-radius: 6px;
        }
        QScrollBar::handle:horizontal {
            background: #55557f;
            min-height: 20px;
            border-radius: 3px;
        }""")

        self

    def line_number_width(self):
        digits = len(str(max(1, self.blockCount())))
        space = 10 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def line_number_size(self):
        width = self.line_number_width()
        size = self.line_number_area.sizeHint().expandedTo(QSize(width, 0))
        return size

    def _update_line_number_width(self, _):
        self.setViewportMargins(self.line_number_width(), 0, 0, 0)

    def _update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self._update_line_number_width(0)

    def paint_line_number_area(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor('#2e2e3f'))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor('#c6c6c6'))
                painter.drawText(0, top, self.line_number_area.width() - 2, self.fontMetrics().height(),
                                 Qt.AlignmentFlag.AlignRight, number)
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1

    def resizeEvent(self, e):
        super().resizeEvent(e)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_width(), cr.height()))

    def _highlight_current_line(self):
        extra_selections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor('#33334f')
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        self.setExtraSelections(extra_selections)

    def wheelEvent(self, event):
        # 禁用外部滚动
        super().wheelEvent(event)
        event.accept()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Tab:
            cursor = self.textCursor()
            cursor.insertText(' ' * 4)
        else:
            super().keyPressEvent(e)


class JsonTextEdit(TextEditBase):
    def __init__(self, parent):
        super().__init__(parent)

    def prettyFormat(self):
        try:
            obj = json.loads(self.toPlainText())
            self.setPlainText(json.dumps(obj, ensure_ascii=False, indent=4))
        except json.JSONDecodeError as e:
            InfoBar.error(
                title='JSON 格式化失败',
                content=f'{e.msg}(行 {e.lineno}，列 {e.colno})',
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self.parent(),
            )


class YamlTextEdit(TextEditBase):
    def __init__(self, parent):
        super().__init__(parent)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Tab:
            cursor = self.textCursor()
            cursor.insertText(' ' * 2)
        else:
            super().keyPressEvent(e)
