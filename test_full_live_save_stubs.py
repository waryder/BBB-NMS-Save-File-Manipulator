# File: test_full_live_save_stubs.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\test_full_live_save_stubs.py
# Purpose: Execute actual menu/button methods with synthetic widgets; no Qt app or save access.
import ast  # Extract actual production methods without importing the app.
import unittest  # Report executed regression checks.
from pathlib import Path  # Read only named project source files.
from types import SimpleNamespace  # Supply isolated Qt-shaped interfaces.

ROOT = Path(__file__).resolve().parent  # Resolve the working copy under test.


# methods: Compile only the named production methods with explicitly supplied dependencies.
def methods(filename, names, env):
    tree = ast.parse((ROOT / filename).read_text(encoding='utf-8'))  # No production imports run.
    nodes: list[ast.stmt] = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name in names]  # Exact scope.
    assert len(nodes) == len(names)  # Fail if an expected integration method disappears.
    exec(compile(ast.Module(body=nodes, type_ignores=[]), filename, 'exec'), env)  # Execute real method bodies.
    return env  # Callers bind the resulting functions to synthetic hosts.


class Control:  # Synthetic button/action records real signal wiring and labels.
    # __init__: Capture construction and expose one callback slot.
    def __init__(self, text, *unused):
        self.text, self.callback = text, None  # No real widgets are created.
        self.clicked = self.triggered = SimpleNamespace(connect=self.connect)  # Both Qt interfaces.

    # connect: Store the actual production callback.
    def connect(self, callback):
        self.callback = callback  # No automatic invocation.

    # setFixedWidth: Record existing control dimensions.
    def setFixedWidth(self, width):
        self.width = width  # Layout assertion only.


class Container:  # Synthetic menu/layout preserves actual action order.
    # __init__: Start with no children.
    def __init__(self):
        self.items = []  # No UI/event loop.

    # addAction: Record the exact action instance.
    def addAction(self, action):
        self.items.append(action)  # Preserve wiring for trigger checks.

    # addWidget: Record remaining dialog buttons.
    def addWidget(self, widget):
        self.items.append(widget)  # Preserve actual layout order.

    # addSeparator: Record a menu separator.
    def addSeparator(self):
        self.items.append(None)  # Distinct from an action.

    # addStretch: Record no synthetic widget for alignment spacing.
    def addStretch(self):
        pass  # No rendering claim.


class FullLiveSaveStubTests(unittest.TestCase):
    # test_dialog_has_only_load_and_close: Execute the actual button factory and its connected callbacks.
    def test_dialog_has_only_load_and_close(self):
        events = []  # Only synthetic callbacks may run.
        env = methods('OpenNmsSaveFileDialog.py', {'_build_button_row'}, {'QHBoxLayout': Container, 'QPushButton': Control})  # No folder scan.
        host = SimpleNamespace(_on_open_clicked=lambda: events.append('load'), reject=lambda: events.append('close'))  # Minimal host.
        row = env['_build_button_row'](host)  # Execute actual factory.
        self.assertEqual([b.text for b in row.items], ['Load Slot', 'Close'])  # Old buttons absent.
        for button in row.items:
            self.assertEqual(button.width, 130)  # Existing dimensions preserved.
            button.callback()  # Exercise real signal targets.
        self.assertEqual(events, ['load', 'close'])  # No backup/restore callback.

    # test_file_menu_backup_and_restore_wiring: Verify live backup dispatch and unchanged notice-only restore.
    def test_file_menu_backup_and_restore_wiring(self):
        notices, menus = [], {}  # Observe real production callback effects.
        names = {'create_menu_bar', 'create_full_live_save_actions', 'full_live_save_backup', 'full_live_save_restore_stub'}  # Actual integration.
        env = {'QAction': Control, 'QMessageBox': SimpleNamespace(information=lambda *args: notices.append(args[1:]))}  # No I/O services supplied.
        backup_calls = []  # Controller dispatch only; no backup or save access in this integration test.
        env['FullLiveSaveBackupController'] = lambda host: SimpleNamespace(run=lambda: backup_calls.append(host))  # Explicit synthetic controller.
        env['show_restore_instructions'] = lambda host: notices.append(('manual instructions', host))  # No save or command execution.
        env['NMSHelpMenu'] = lambda host: SimpleNamespace(create_help_menu=lambda bar: None)  # Isolate unrelated Help.
        env = methods('BBB_NMS_Save_File_Manipulator.py', names, env)  # No app imports.
        bar = SimpleNamespace(addMenu=lambda title: menus.setdefault(title, Container()))  # Actual File-menu placement.
        host = SimpleNamespace(menuBar=lambda: bar, open_file=lambda: None, save_file=lambda: None, create_tools_menu=lambda bar: None)  # No save objects.
        for name in names:
            setattr(host, name, lambda *args, name=name: env[name](host, *args))  # Bind actual methods.
        host.create_menu_bar()  # Exercise production integration, not a reconstructed menu.
        actions = [a for a in menus['File'].items if a is not None]  # Ignore separator.
        self.assertEqual([a.text for a in actions], ['Open NMS Save File', 'Save NMS Save File', 'Full Live Save Backup', 'Full Live Save Restore'])  # Exact order/labels.
        for action in actions[2:]:
            action.callback()  # Actual handlers can only show notices.
        self.assertEqual(backup_calls, [host])  # Full backup calls the dedicated controller once.
        self.assertEqual(notices, [('manual instructions', host)])  # Restore opens copyable guidance only.

    # test_slot_archive_implementation_removed: Require removal rather than hidden/disconnected functionality.
    def test_slot_archive_implementation_removed(self):
        removed = {'backup_nms_slot', 'restore_nms_slot', '_nms_backup_directory', '_checked_backup_snapshot', '_on_slot_backup_clicked', '_on_restore_clicked', 'read_zip_slot', '_zip_members', '_slot_from_names', 'backup_name', 'zip_bytes', '_backup_target', '_verify_backup', '_commit_backup', 'write_backup'}  # Retired API.
        for filename in ['OpenNmsSaveFileDialog.py', 'NmsLoadController.py', 'NmsSlotOperations.py']:
            source = (ROOT / filename).read_text(encoding='utf-8')  # Named production files only.
            tree = ast.parse(source)  # Inspect definitions and references.
            identifiers = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}  # Defined helpers.
            identifiers.update(n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute))  # Remaining calls.
            self.assertFalse(removed & identifiers, filename)  # No orphan retired API.
            self.assertNotIn('Save Slot Backup', source)  # Old dialog label removed.
            self.assertNotIn('Load Slot Backup', source)  # Old restore label removed.
            self.assertNotIn('import zipfile', source)  # No slot ZIP engine retained.

    # test_changed_files_parse_and_keep_crlf: Check Gaming-PC grammar and Windows line endings.
    def test_changed_files_parse_and_keep_crlf(self):
        for filename in ['OpenNmsSaveFileDialog.py', 'NmsLoadController.py', 'NmsSlotOperations.py', 'BBB_NMS_Save_File_Manipulator.py', 'test_full_live_save_stubs.py']:
            payload = (ROOT / filename).read_bytes()  # Source-only checks.
            ast.parse(payload.decode('utf-8'), feature_version=(3, 12))  # Target Python grammar.
            self.assertNotIn(bytes([10]), payload.replace(bytes([13, 10]), b''), filename)  # Consistent CRLF.


if __name__ == '__main__':
    unittest.main(verbosity=2)  # Explicit console-only invocation.
