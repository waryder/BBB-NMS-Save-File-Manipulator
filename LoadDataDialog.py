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



