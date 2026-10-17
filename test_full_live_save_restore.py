# File: test_full_live_save_restore.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\test_full_live_save_restore.py
# Purpose: Test manual-only UI and PowerShell example using dummy folders, never actual saves.
import ast  # Extract production code without shared app initialization.
import os  # Select a hidden Qt platform.
import subprocess  # Exercise the example only against disposable dummy paths.
import tempfile  # Own all test filesystem changes.
import unittest  # Report real execution results.
from pathlib import Path  # Read the named module and dummy files.
os.environ['QT_QPA_PLATFORM'] = 'offscreen'  # Never open a visible application window.
from PyQt5.QtWidgets import QApplication, QDialog, QPlainTextEdit, QPushButton, QHBoxLayout, QVBoxLayout  # Real hidden Qt controls.
from PyQt5.QtCore import Qt  # Real flags.

ROOT = Path(__file__).resolve().parent  # Repository under test.
TREE = ast.parse((ROOT / 'FullLiveSaveRestoreDialog.py').read_text(encoding='utf-8'))  # Source only.
ENV = dict(QApplication=QApplication, QDialog=QDialog, QPlainTextEdit=QPlainTextEdit, QPushButton=QPushButton, QHBoxLayout=QHBoxLayout, QVBoxLayout=QVBoxLayout, Qt=Qt)  # Isolated dependencies.
NODES: list[ast.stmt] = [n for n in TREE.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and getattr(n, 'name', '') != 'show_restore_instructions']  # No source resolver or imports executed.
exec(compile(ast.Module(body=NODES, type_ignores=[]), 'restore-instructions-test', 'exec'), ENV)  # Actual production formatter/dialog.
APP = QApplication.instance() or QApplication([])  # Hidden Qt only.


class RestoreInstructionsTests(unittest.TestCase):
    # setUp: Make clearly dummy backup/live roots with spaces and an apostrophe to exercise quoting.
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='restore-text-test-', dir=os.environ.get('TMPDIR'))  # Scratch only.
        self.addCleanup(self.tmp.cleanup)  # Remove fixture-owned folders.
        root = Path(self.tmp.name) / "Bill's test data"  # PowerShell apostrophe regression.
        self.backups, self.live = root / 'Full NMS Save Backups', root / 'NMS'  # Never actual app/live paths.
        self.chosen = self.backups / 'dummy_timestamped_backup'  # Explicit test selection.
        (self.chosen / 'st_dummy' / 'empty').mkdir(parents=True)  # Complete dummy account shape.
        (self.chosen / 'st_dummy' / 'save.hg').write_bytes(b'DUMMY BACKUP')  # Not valid game content.
        self.live.mkdir()  # Existing live target required.
        (self.live / 'old-only.txt').write_text('DUMMY OLD')  # Must disappear only in the explicit script test.
        self.text = ENV['restore_instructions'](self.live, self.backups)  # Text generation alone cannot change files.

    # run_example: Run only the generated example, with paths restricted to this test's temporary root.
    def run_example(self, select=False):
        script = self.text.split('EXAMPLE WINDOWS POWERSHELL COMMANDS:\n\n', 1)[1]  # No prose executed.
        if select:  # User must deliberately replace the placeholder; test supplies its dummy folder.
            script = script.replace("$backupName = 'REPLACE_WITH_YOUR_TIMESTAMPED_BACKUP_FOLDER_NAME'", "$backupName = 'dummy_timestamped_backup'")  # Keep the guard's original placeholder intact.
        script_path = Path(self.tmp.name) / 'dummy-restore.ps1'  # Own the generated test script.
        script_path.write_text(script, encoding='utf-8-sig')  # Windows PowerShell script encoding.
        result = subprocess.run(['powershell.exe', '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass', '-File', str(script_path)], capture_output=True, text=True, timeout=15)  # Only dummy data may be deleted/copied.
        return result  # Assert the real exit status below.

    # test_placeholder_blocks_deletion: Copying the unedited example cannot remove any live file.
    def test_placeholder_blocks_deletion(self):
        result = self.run_example()  # Placeholder must throw before Remove-Item.
        self.assertNotEqual(result.returncode, 0)  # Refusal is expected.
        self.assertTrue((self.live / 'old-only.txt').exists())  # No deletion.

    # test_delete_then_copy_dummy_only: Real PowerShell/Robocopy removes obsolete files then recreates the tree.
    def test_delete_then_copy_dummy_only(self):
        result = self.run_example(select=True)  # Explicit dummy backup selection.
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)  # Actual command success.
        self.assertFalse((self.live / 'old-only.txt').exists())  # Delete-first semantics, not an overlay.
        self.assertEqual((self.live / 'st_dummy' / 'save.hg').read_bytes(), b'DUMMY BACKUP')  # Actual copied bytes.
        self.assertTrue((self.live / 'st_dummy' / 'empty').is_dir())  # Empty directory restored.
        self.assertEqual((self.chosen / 'st_dummy' / 'save.hg').read_bytes(), b'DUMMY BACKUP')  # Backup unchanged.

    # test_hidden_dialog_copy_close: Real widgets allow selection/copy and have no execute button.
    def test_hidden_dialog_copy_close(self):
        dialog = ENV['FullLiveSaveRestoreDialog'](self.text)  # No show/exec and no live source lookup.
        self.addCleanup(dialog.deleteLater)  # Dispose hidden widgets.
        self.assertTrue(dialog.text_box.isReadOnly())  # Selectable, not editable.
        buttons = {b.text(): b for b in dialog.findChildren(QPushButton)}  # Actual controls.
        self.assertEqual(set(buttons), {'Copy Text', 'Close'})  # No Run/Restore control.
        clipboard = APP.clipboard()  # Offscreen clipboard only.
        previous = clipboard.text()  # Preserve even the offscreen prior text.
        try:
            buttons['Copy Text'].click()  # Exercise the actual signal handler.
            self.assertEqual(clipboard.text(), self.text)  # Exact text, paths and line breaks.
        finally:
            clipboard.setText(previous)  # Restore clipboard contents.
        buttons['Close'].click()  # Dismiss only.
        self.assertEqual(dialog.result(), QDialog.Rejected)  # No restore acceptance.
        self.assertTrue((self.live / 'old-only.txt').exists())  # UI never changed fixture data.


if __name__ == '__main__':
    unittest.main(verbosity=2)  # Hidden controls and dummy commands only.
