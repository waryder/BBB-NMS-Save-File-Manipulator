from PyQt5.QtWidgets import QPlainTextEdit, QWidget, QTextEdit
from PyQt5.QtGui import QPainter, QColor, QTextFormat, QKeySequence, QFont
from PyQt5.QtCore import QRect, QSize, Qt, QEvent, QTimer

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super(LineNumberArea, self).__init__(editor)
        self.editor = editor

    def sizeHint(self):
        # Return a suggested size that respects the current width for line numbers
        return QSize(self.editor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.editor.lineNumberAreaPaintEvent(event)

        # Add a black right-hand border
        painter = QPainter(self)
        painter.setPen(Qt.black)
        painter.drawLine(self.width() - 1, 0, self.width() - 1, self.height())


class CustomTextEdit(QPlainTextEdit):
    def __init__(self, parent=None):
        super(CustomTextEdit, self).__init__(parent)
        self.parent_tab = parent
        self.setLineWrapMode(QPlainTextEdit.NoWrap)

        # Set the font size for the text editor and line number area
        font = self.font()
        font.setPointSize(10)  # Replace '12' with your desired font size
        self.setFont(font)

        self.setStyleSheet("""
            QPlainTextEdit {
                border: 1px solid black;  /* Solid 1px black border */
            }
        """)

        # Create and initialize the line number area
        self.lineNumberArea = LineNumberArea(self)
        self.lineNumberArea.setFont(font)  # Use the same font for the line number area


        # Connect signals
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)

        # Set initial width for line number area
        self.updateLineNumberAreaWidth(0)

    def lineNumberAreaWidth(self):
        # Calculate the width needed to display the highest line number
        digits = len(str(max(1, self.blockCount())))
        # Add some spacing
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def updateLineNumberAreaWidth(self, _):
        # Adjust the margin to make space for line numbers
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            # Scroll the line number area along with the text
            self.lineNumberArea.scroll(0, dy)
        else:
            # Repaint the line number area if needed
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())

        # If the user resized the editor or the update region covers everything
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super(CustomTextEdit, self).resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(),
                                              self.lineNumberAreaWidth(), cr.height()))

    def lineNumberAreaPaintEvent(self, event):
        # Draw the background and line numbers
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), Qt.lightGray)

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.setPen(Qt.black)
                painter.drawText(0, top, self.lineNumberArea.width(),
                                 self.fontMetrics().height(),
                                 Qt.AlignRight, number)
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            blockNumber += 1

    def highlightCurrentLine(self):
        # QPlainTextEdit uses QTextEdit.ExtraSelection to specify extra selections
        extraSelections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            lineColor = QColor(Qt.yellow).lighter(160)
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        self.setExtraSelections(extraSelections)

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Paste):
            if self.parent_tab:
                self.parent_tab.set_led_based_on_app_thread_load()  # Update indicator
            super(CustomTextEdit, self).keyPressEvent(event)
        else:
            super(CustomTextEdit, self).keyPressEvent(event)

    def event(self, event):
        if event.type() == QEvent.Clipboard:
            if self.parent_tab:
                self.parent_tab.set_led_based_on_app_thread_load()  # Update indicator
        return super(CustomTextEdit, self).event(event)






# from imports import *
#
# class CustomTextEdit(QPlainTextEdit):
#     def __init__(self, parent=None):
#         super(CustomTextEdit, self).__init__(parent)
#         self.parent_tab = parent  # Reference to the parent tab object
#         self.setLineWrapMode(QPlainTextEdit.NoWrap)
#         #self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
#
#     def keyPressEvent(self, event):
#         # Check if Ctrl+V or Cmd+V (on macOS) is pressed
#         if event.matches(QKeySequence.Paste):
#             self.parent_tab.set_led_based_on_app_thread_load()  # Update indicator
#             super(CustomTextEdit, self).keyPressEvent(event)  # Let the normal paste occur
#         else:
#             super(CustomTextEdit, self).keyPressEvent(event)
#
#     def event(self, event):
#         # Capture all paste events (context menu and programmatically)
#         if event.type() == QEvent.Clipboard:
#             self.parent_tab.set_led_based_on_app_thread_load()  # Update indicator
#         return super(CustomTextEdit, self).event(event)


# Copyright (C) 2024-2026 BigBuffaloBill - Bill Ryder <me@billryder.com>
#
# This file is part of BBB NMS Save File Manipulator.
#
# BBB NMS Save File Manipulator is free software: you can redistribute it and/or modify it under the terms of
# the GNU General Public License as published by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# BBB NMS Save File Manipulator is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details. You should have received a copy of the GNU General Public License along with
# this program (see the LICENSE file). If not, see <https://www.gnu.org/licenses/>.
