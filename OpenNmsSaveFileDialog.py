# File: OpenNmsSaveFileDialog.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\OpenNmsSaveFileDialog.py
# Purpose: Stub popup launched by the main window's "Open NMS Save File" button.
#          The real design (save-file picker / slot selection via nms_save_codec) is still to come.

# Pull in the shared PyQt5 widgets, Qt namespace and logger used across the app
from imports import *

# Project/file prefix for debug output, per Bill's code standards
DEBUG_PREFIX = "[BBB-NMS-SFM/OpenNmsSaveFileDialog]"
# Gate for non-error debug output; leave False for normal runs
DEBUG_ENABLED = False


class OpenNmsSaveFileDialog(QDialog):
    # __init__
    # Builds the placeholder popup: a title, a "not yet designed" note, and a Close button.
    def __init__(self, parent=None):
        # Initialize the base QDialog with the main window as parent
        super().__init__(parent)

        # Optional trace that the stub was opened
        if DEBUG_ENABLED:
            logger.debug(f"{DEBUG_PREFIX} __init__: stub popup created")

        # Window title matches the button that opens it
        self.setWindowTitle("Open NMS Save File")
        # Give the stub a sensible starting size
        self.setMinimumSize(320, 120)
        # Remove the "?" context-help button, matching LoadDataDialog
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        # Placeholder text so it is obvious this popup is not finished
        label = QLabel("<b>Open NMS Save File</b><br>This popup is not designed yet.")

        # Close button simply dismisses the dialog as "rejected"
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.reject)

        # Stack the label and button vertically
        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.close_button)
        # Apply the layout to the dialog
        self.setLayout(layout)
