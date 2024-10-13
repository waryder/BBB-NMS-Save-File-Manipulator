from imports import *

class CustomTextEdit(QPlainTextEdit):
    def __init__(self, parent=None):
        self.first_tab_obj = parent  # Reference to the parent tab object
        super(CustomTextEdit, self).__init__(parent)

    def keyPressEvent(self, event):
        # Check if Ctrl+V or Cmd+V (on macOS) is pressed
        if event.matches(QKeySequence.Paste):
            print("Text pasted via keyboard shortcut")
            self.first_tab_obj.update_status_indicator_to_green(False)  # Update indicator
            super(CustomTextEdit, self).keyPressEvent(event)  # Let the normal paste occur
        else:
            super(CustomTextEdit, self).keyPressEvent(event)

    def event(self, event):
        # Capture all paste events (context menu and programmatically)
        if event.type() == QEvent.Clipboard:
            print("Text pasted via paste event")
            self.first_tab_obj.update_status_indicator_to_green(False)  # Update indicator
        return super(CustomTextEdit, self).event(event)