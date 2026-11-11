# File: StartupDisclaimerDialog.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\StartupDisclaimerDialog.py
# Purpose: Show the alpha-software warning at startup with an atomic, persistent opt-out.
from imports import *  # Follow the application's existing dialog conventions.

DISCLAIMER_TEXT = (
    'DISCLAIMER\n\n'
    'No warranty is provided, express or implied. Use this software at your own risk.\n\n'
    'I\'m a software engineer with a 25-year career, and I use this editor every day. '
    'However, it is alpha software, and not all functions have been fully tested. '
    'I expect it to work correctly most of the time, but I would NEVER use ANY save-file '
    'editor without first backing up the most recent live save files.\n\n'
    'This editor includes Full Live Save Backup to automate that process. Please use it!\n\n'
    'Feedback is welcome—contact BigBuffaloBill on Discord!'
)


class StartupDisclaimerDialog(QDialog):
    # __init__: Present the warning without reading or changing any game-save data.
    def __init__(self, parent):
        super().__init__(parent)  # Keep the startup warning modal to the main window.
        self.preferences = parent.ini_file_manager  # Reuse the existing persistent preference manager.
        self.setWindowTitle('Disclaimer')  # Capitalize the popup title.
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)  # Remove the unused help button.
        self.setMinimumWidth(620)  # Give the warning readable wrapped paragraphs.
        layout = QVBoxLayout(self)  # Let Qt size the dialog for the current font.
        message = QLabel(DISCLAIMER_TEXT)  # Render the wording literally, not as rich text.
        message.setTextFormat(Qt.PlainText)  # Preserve the exact warning and punctuation.
        message.setWordWrap(True)  # Keep all paragraphs inside the dialog.
        message.setTextInteractionFlags(Qt.TextSelectableByMouse)  # Allow copying the warning.
        layout.addWidget(message)  # Place the full disclaimer above its opt-out.
        self.hide_message = QCheckBox('Do not show this message again')  # Unchecked on first display.
        layout.addWidget(self.hide_message)  # Require an explicit opt-out choice.
        buttons = QHBoxLayout()  # Right-align the acknowledgment button.
        buttons.addStretch()  # Keep the button at the right edge.
        acknowledge = QPushButton('OK')  # Preserve the standard uppercase acronym.
        acknowledge.clicked.connect(self.accept)  # Persist the choice only on acknowledgment.
        buttons.addWidget(acknowledge)  # Retain a normal keyboard-accessible push button.
        layout.addLayout(buttons)  # Complete the warning layout.

    # accept: Save an explicit opt-out before dismissing; keep the warning open if persistence fails.
    def accept(self):
        if self.hide_message.isChecked():  # Unchecked acknowledgment needs no preference write.
            try:  # Never claim the message is suppressed when persistence failed.
                self.preferences.store_hide_startup_disclaimer(True)  # Atomic write preserves other settings.
            except Exception as error:
                QMessageBox.warning(self, 'Disclaimer Preferences',
                    'Your choice could not be saved. Uncheck the box to continue without saving it.\n\n' + str(error))
                return  # Let the user retry or continue without opting out.
        super().accept()  # Window-close and Escape use rejection and never persist an opt-out.


# show_startup_disclaimer: Skip only an explicitly saved opt-out; otherwise show the modal warning.
def show_startup_disclaimer(window):
    if not window.ini_file_manager.get_hide_startup_disclaimer():  # Missing/invalid preference means show it.
        StartupDisclaimerDialog(window).exec_()  # Closing this popup never closes or changes the editor.
