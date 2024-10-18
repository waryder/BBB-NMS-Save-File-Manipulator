#NMSHelpMenu.py

from imports import *

class NMSHelpMenu:
    def __init__(self, parent):
        # Parent is the main window instance
        self.parent = parent

    def create_help_menu(self, menubar):
        # Add the "Help" menu
        help_menu = menubar.addMenu('Help')

        # Create "Help" action
        help_action = QAction('Help', self.parent)
        help_action.triggered.connect(self.show_help_dialog)
        help_menu.addAction(help_action)

        # Create "Documentation" action
        doc_action = QAction('Documentation', self.parent)
        doc_action.triggered.connect(self.show_help_dialog)
        help_menu.addAction(doc_action)

    def show_help_dialog(self):
        # Open the help dialog (using QTextBrowser with navigation)
        dialog = NMSHelpDialog(self.parent)  # This is now NMSHelpDialog
        dialog.exec_()


class NMSHelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Help")

        # Create the QTextBrowser for displaying help content
        self.text_browser = QTextBrowser()

        # Load the main help page content
        self.load_main_page()

        # Connect link clicks to handle navigation using anchorClicked
        self.text_browser.anchorClicked.connect(self.handle_link)

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.text_browser)
        self.setLayout(layout)

    def load_main_page(self):
        self.text_browser.setHtml('''
            <h1>Main Help Page</h1>
            <p>Welcome to the main help section.</p>
            <p><a href="section1">Go to Section 1</a></p>
            <p><a href="section2">Go to Section 2</a></p>
        ''')

    def load_section1(self):
        self.text_browser.setHtml('''
            <h2>Section 1</h2>
            <p>This is the content of Section 1.</p>
            <p><a href="main">Back to Main Help</a></p>
        ''')

    def load_section2(self):
        self.text_browser.setHtml('''
            <h2>Section 2</h2>
            <p>This is the content of Section 2.</p>
            <p><a href="main">Back to Main Help</a></p>
        ''')

    def handle_link(self, url):
        link = url.toString()
        if link == "main":
            self.load_main_page()
        elif link == "section1":
            self.load_section1()
        elif link == "section2":
            self.load_section2()
            
            
            
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


    
            
