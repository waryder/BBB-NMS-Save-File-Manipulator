#NMSHelpMenu.py

import sys
import webbrowser
from PyQt5.QtWidgets import QAction, QDialog
import os

class NMSHelpMenu(QDialog):
    def __init__(self, parent=None):
        super(NMSHelpMenu, self).__init__(parent)
        self.setWindowTitle("Help Menu")
        
    def create_help_menu(self, menu_bar):
        # Create the Help menu
        help_menu = menu_bar.addMenu("Help")

        # Add Help action
        help_action = QAction("Open Help", self)
        help_action.triggered.connect(self.open_help)
        help_menu.addAction(help_action)

    def open_help(self):
        # Get the path to the help/index.html file
        help_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "help/index.html"))
        # Open the help file in the system's default browser
        webbrowser.open(f"file://{help_file_path}")


            
            
            
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


    
            
