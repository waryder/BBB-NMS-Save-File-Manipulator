from imports import *
from PyQt5.QtGui import QTextDocument 

class TextSearchDialog(QDialog):  # Change QWidget to QDialog
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.parentTab = parent        
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("Search Dialog")

        # Create a line edit for search input
        self.line_edit = QLineEdit(self)
        self.line_edit.setPlaceholderText("Enter search term")

        # Create buttons for search and cancel
        self.searchUp_button = QPushButton("Search Backward", self)
        self.searchDown_button = QPushButton("Search Forward", self)
        self.cancel_button = QPushButton("Close", self)

        # Layout to hold widgets
        layout = QVBoxLayout()
        layout.addWidget(self.line_edit)
        layout.addWidget(self.searchUp_button)
        layout.addWidget(self.searchDown_button)
        layout.addWidget(self.cancel_button)
        self.setLayout(layout)

        # Connect buttons to respective methods
        self.searchUp_button.clicked.connect(self.perform_upSearch)
        self.searchDown_button.clicked.connect(self.perform_downSearch)
        self.cancel_button.clicked.connect(self.reject)  # Use reject() for canceling
        
        self.current_search_string = ""
        self.last_cursor_position = None

    def perform_upSearch(self):
        search_string = self.line_edit.text()
        if search_string:
            self.current_search_string = search_string
            self.last_cursor_position = self.parentTab.text_edit.textCursor()
            self.find_next_occurrence("backward") 
        
    def perform_downSearch(self):
        search_string = self.line_edit.text()
        if search_string:
            self.current_search_string = search_string
            self.last_cursor_position = self.parentTab.text_edit.textCursor()
            self.find_next_occurrence("forward") 
        
    def find_next_occurrence(self, direction="forward"):
        logger.debug("find_occurrence() ENTER")
        """
        Searches for the next occurrence of the current search string in the given direction.
        Automatically wraps based on config.
        
        :param direction: "forward" to search down, "backward" to search up
        """
        if not self.current_search_string:
            return  # If no search string is set, return
        
        # Get the QTextDocument object
        document = self.parentTab.text_edit.document()
        
        # Determine search direction
        cursor = self.parentTab.text_edit.textCursor()
        
        if direction == "backward":
            cursor = document.find(self.current_search_string, cursor, QTextDocument.FindBackward)
        else:  # Default is forward
            cursor = document.find(self.current_search_string, cursor)
        
        # If occurrence not found and wrapping is enabled
        if cursor.isNull():
            self.parentTab.text_edit.setTextCursor(self.last_cursor_position)
            self.show_no_more_matches_dialog()
            return
    
        # Highlight the found occurrence and update the last cursor position
        self.parentTab.text_edit.setTextCursor(cursor)
        self.parentTab.text_edit.ensureCursorVisible()  # Scroll to make the found text visible
        self.last_cursor_position = self.parentTab.text_edit.textCursor()  # Update last position
        
        logger.debug("find_occurrence() EXIT")    


    # New method to show a dialog when no more matches are found
    def show_no_more_matches_dialog(self):
        """
        Shows a message box when no more occurrences of the search string are found.
        """
        QMessageBox.information(self, "End of Search", "No more occurrences found.") 


# MIT License
#
# Copyright (c) [Year] [Your Name or Your Company] <youremail@example.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# 1. The above copyright notice and this permission notice shall be included
#    in all copies or substantial portions of the Software.
#
# 2. Attribution Requirement: Any use of this code, in whole or in part,
#    must retain the following attribution notice in the source code comments:
#    
#    This code includes portions of the software originally developed by
#    [Your Name or Your Company] <youremail@example.com>, available under the MIT License.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# This software makes use of PyQt5, which is licensed under the GPL v3 License.
# The PyQt5 library is a third-party library that is not covered under the 
# MIT License governing this software. As required by the GPL v3 License, 
# the source code for this software is made available, and you are free to
# modify and redistribute it under the terms of the GPL v3 License.
#
# You can find more details on the PyQt5 license here: https://www.riverbankcomputing.com/software/pyqt/license
# To comply with the GPL v3 License, you must include the full source code and this 
# license notice with any redistributions of this software that include PyQt5.


    
        