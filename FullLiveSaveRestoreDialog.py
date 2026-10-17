# File: FullLiveSaveRestoreDialog.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\FullLiveSaveRestoreDialog.py
# Purpose: Display copyable manual restore instructions; never execute commands or modify saves.
from imports import *  # Follow the application's shared Qt dialog conventions.
import FullLiveSaveBackup as backup_ops  # Reuse actual application-root and NMS-source policies.
from OpenNmsSaveFileDialog import get_initial_save_folder  # Match the backup source selection.


# _ps_quote: Represent a Windows path as a literal PowerShell single-quoted string.
def _ps_quote(value):
    return "'" + str(value).replace("'", "''") + "'"  # Escape apostrophes without expanding dollar signs or backticks.


# restore_instructions: Show the approved three-line NMS restore example using actual runtime paths.
def restore_instructions(source, backup_root):
    source = backup_ops.Path(source).absolute()  # Full live NMS directory resolved by the app, not a fixed user path.
    root_text = str(backup_root).replace('`', '``').replace('$', '`$').replace('"', '`"')  # Keep the real root literal inside PowerShell double quotes.
    backup_expression = '"' + root_text + chr(92) + '$backupDirName"'  # Expand only the user-selected backup directory name.
    command = '\n'.join([  # Exactly three displayed lines; the app never executes them.
        "$backupDirName = 'REPLACE_WITH_YOUR_TIMESTAMPED_BACKUP_FOLDER_NAME'",  # The sole intentional placeholder.
        'Remove-Item -Path ' + _ps_quote(source / '*') + ' -Recurse -Force',  # Delete live NMS contents while retaining NMS itself.
        'robocopy ' + backup_expression + ' ' + _ps_quote(source) + ' /E /R:0 /W:0',  # Copy selected backup contents into live NMS.
    ])  # No generated checks, error handling, extra variables or shell execution.
    return ("We have decided not to implement restore functionality directly because it is very risky if you do not know what you are doing. "
            "The adjacent Full Live Save Backup menu option produces a standard copy of your game saves. "
            "At a high level, restoring involves deleting the live NMS directory contents and copying the saved contents back into the same place.\n\n"
            f"You can find this app's backups here:\n{backup_root}\n\n"
            f"Your live NMS directory on this system is:\n{source}\n\n"
            "We are confident in the backups this app produces, but putting one back in place is on you to learn about and have the confidence to decide whether these commands are appropriate for your system.\n\n"
            "WARNING: The example below first deletes ALL contents of your live NMS directory, including every subdirectory and file, and then copies the selected backup's contents into it. "
            "The NMS directory itself is retained. This can permanently erase game progress or leave your saves unusable if it is done wrong.\n\n"
            "Never operate on No Man's Sky files unless the game is shut down.\n\n"
            "Attempting the following is your decision and responsibility:\n\n"
            "You would replace REPLACE_WITH_YOUR_TIMESTAMPED_BACKUP_FOLDER_NAME below with the name of the backup directory you want to restore.\n\n"
            "EXAMPLE WINDOWS POWERSHELL COMMANDS:\n\n" + command)  # Warnings describe the exact whole-NMS-contents example approved by Bill.


class FullLiveSaveRestoreDialog(QDialog):
    # __init__: Present read-only, selectable instructions and explicit copy/close controls.
    def __init__(self, text, parent=None):
        super().__init__(parent)  # Modal ownership without touching the editor model.
        self.setWindowTitle('Full Live Save Restore — Manual Instructions')  # Distinguish guidance from an automated restore.
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)  # Match existing dialogs.
        self.resize(920, 680)  # Allow paths and commands to be reviewed with scrolling.
        self.text_box = QPlainTextEdit(self)  # Plain text preserves PowerShell quotes and line breaks.
        text_font = self.text_box.font()  # Start from the dialog's inherited text font.
        text_font.setPointSizeF(text_font.pointSizeF() + 2)  # Increase instruction and command text by two points.
        self.text_box.setFont(text_font)  # Apply only to the selectable dialog text.
        self.text_box.setReadOnly(True)  # Select/copy allowed; accidental edits disabled.
        self.text_box.setPlainText(text)  # Never interpret commands as markup or executable code.
        copy_button = QPushButton('Copy Text', self)  # Explicit user clipboard action only.
        copy_button.clicked.connect(self.copy_text)  # No clipboard writes until clicked.
        close_button = QPushButton('Close', self)  # No restore/execute control exists.
        close_button.clicked.connect(self.reject)  # Closing has no filesystem side effects.
        close_button.setDefault(True)  # Enter closes rather than initiating any action.
        buttons = QHBoxLayout()  # Separate actions from the scrollable instructions.
        buttons.addWidget(copy_button)  # Copy action first.
        buttons.addStretch()  # Keep Close at the right.
        buttons.addWidget(close_button)  # Close is the sole dismissal action.
        layout = QVBoxLayout(self)  # Attach the dialog layout.
        layout.addWidget(self.text_box)  # Selectable text consumes available space.
        layout.addLayout(buttons)  # Buttons remain visible while scrolling.

    # copy_text: Copy the displayed text without running or changing any command.
    def copy_text(self):
        QApplication.clipboard().setText(self.text_box.toPlainText())  # Clipboard only, no shell or file writes.


# show_restore_instructions: Resolve the same source/root as Backup, then display guidance only.
def show_restore_instructions(window):
    try:  # Missing source configuration must not produce guessed destructive commands.
        selected = get_initial_save_folder(window.ini_file_manager, window)  # Shared remembered/default source policy.
        source = backup_ops.source_root(selected)  # Resolve the actual live NMS directory using the same policy as Backup.
        root = backup_ops.application_root() / 'Full NMS Save Backups'  # Actual application backup directory.
        text = restore_instructions(source, root)  # Populate the three-line example with real runtime paths.
    except Exception as exc:  # Keep errors copyable, but do not offer a command with an unknown target.
        text = ('Manual restore instructions cannot determine the live save folder. Use File > Open NMS Save File to select it first. '
                'No restore command was generated and no files were changed.\n\n' + str(exc))  # Fail closed.
    return FullLiveSaveRestoreDialog(text, window).exec_()  # Modal display only; no command execution path.
