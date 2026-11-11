#NMSHelpMenu.py

import sys
import webbrowser
from PyQt5.QtWidgets import QAction, QDialog, QMessageBox
import os

from version import DISPLAY_VERSION  # Row 520: one shared version source for Help → About.

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
        help_menu.addSeparator()  # Keep existing help separate from application identity.
        about_action = QAction('About', self)  # Add the requested Help → About entry.
        about_action.triggered.connect(self.show_about)  # Open a local modal informational popup only.
        help_menu.addAction(about_action)

    # show_about: Display the application name and exact requested version without touching editor data.
    def show_about(self):
        QMessageBox.about(self, 'About BBB NMS Save File Manipulator',
                          'BBB NMS Save File Manipulator\n' + DISPLAY_VERSION)  # Qt owns dismissal.

    def open_help(self):
        # Get the path to the help/index.html file
        help_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "help/index.html"))
        # Open the help file in the system's default browser
        webbrowser.open(f"file://{help_file_path}")


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
