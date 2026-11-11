from imports import *

class LoadDataDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Set up the dialog layout
        self.setWindowTitle("BBB NMS Save File Manipulator")
        self.setMinimumSize(200, 100)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        # Create the label
        label = QLabel("<b>Load the full data for the 'BaseContext' JSON<br> object from your No Man's Sky Save File...</b>")

        # Create the button to load data from clipboard
        self.import_button = QPushButton("Import 'BaseContext' JSON from Clipboard")
        self.import_button.setFixedSize(300, 40)  # Adjust size as needed
        self.import_button.clicked.connect(self.accept)  # Close the dialog and accept input

        # Create the "Skip Data Load" checkbox
        self.skip_data_checkbox = QCheckBox("Skip Data Load")

        # Arrange widgets in the main dialog layout
        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.import_button)

        # Add a horizontal layout for the checkbox
        checkbox_layout = QHBoxLayout()
        checkbox_layout.addWidget(self.skip_data_checkbox)
        checkbox_layout.addStretch()  # Align to the left

        layout.addLayout(checkbox_layout)

        self.setLayout(layout)

    def get_text(self):
        """Fetch and return text from the system clipboard."""
        clipboard = QApplication.clipboard()
        return clipboard.text()

    def is_skip_data_load_checked(self):
        """Return the state of the 'Skip Data Load' checkbox."""
        return self.skip_data_checkbox.isChecked()




# class LoadDataDialog(QDialog):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#
#         # Set up the dialog layout
#         self.setWindowTitle("BBB NMS Save File Manipulator")
#         self.setMinimumSize(200, 100)
#         self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
#
#         # Create the label
#         label = QLabel("<b>Load the full data for the 'BaseContext' JSON<br> object from your No Man's Sky Save File...</b>")
#
#         # Create the button to load data from clipboard
#         self.import_button = QPushButton("Import 'BaseContext' JSON from Clipboard")
#         self.import_button.setFixedSize(300, 40)  # Adjust size as needed
#         self.import_button.clicked.connect(self.accept)  # Close the dialog and accept input
#
#         # Arrange widgets in the main dialog layout
#         layout = QVBoxLayout()
#         layout.addWidget(label)
#         layout.addWidget(self.import_button)
#
#         self.setLayout(layout)
#
#     def get_text(self):
#         # Fetch and return text from the system clipboard
#         clipboard = QApplication.clipboard()
#         return clipboard.text()


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
