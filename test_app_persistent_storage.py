# File: test_app_persistent_storage.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\test_app_persistent_storage.py
# Purpose: Exercise storage policy against disposable directories; no Qt windows or game saves.
import ast  # Verify startup order without importing the Qt application.
import os  # Control only the test process's proposed parent directory.
import tempfile  # Own all fixture files beneath an explicitly supplied scratch directory.
import unittest  # Report executable assertions using the standard library.
from pathlib import Path  # Use real native filesystem paths for the storage core.
from unittest.mock import patch  # Inject denied access without changing real permissions.
import AppPersistentStorage as storage  # Importing policy itself never selects or writes storage.
import FullLiveSaveBackup as backup_ops  # Exercise the shared selected-tree backup root.


class StoragePolicyTests(unittest.TestCase):
    # setUp: Create disposable roots outside every real application/game data directory.
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(dir=os.environ['NMS_STORAGE_TEST_SCRATCH'])
        self.base = Path(self.temporary.name)  # Each test owns a unique sandbox.
        self.app = self.base / 'app'
        self.app.mkdir()  # Represent a source or executable directory without using the actual one.
        self.root = self.base / storage.DATA_NAME
        self.root.mkdir()  # Existing selected root, initially without children.
        self.previous = storage._data_root

    # tearDown: Restore module state and remove only fixture-owned directories.
    def tearDown(self):
        storage._data_root = self.previous
        self.temporary.cleanup()

    # test_complete_tree: Create every approved category without touching unrelated files.
    def test_complete_tree(self):
        storage.validate_root(self.root)
        self.assertTrue(all((self.root / item).is_dir() for item in storage.SUBDIRECTORIES))
        self.assertEqual(list((self.root / 'Settings').iterdir()), [])

    # test_single_value_roundtrip: Preserve a selected non-default absolute root across locator reads.
    def test_single_value_roundtrip(self):
        storage.save_locator(self.app, self.root)
        self.assertEqual((self.app / storage.LOCATOR_NAME).read_text(encoding='utf-8'), str(self.root))
        self.assertEqual(storage.read_locator(self.app), self.root)
        self.assertEqual(sorted(p.name for p in self.app.iterdir()), [storage.LOCATOR_NAME])

    # test_missing_locator: Never discover an existing default-looking directory implicitly.
    def test_missing_locator(self):
        with self.assertRaises(FileNotFoundError):
            storage.read_locator(self.app)

    # test_missing_recorded_root: A missing selected root must not be silently recreated.
    def test_missing_recorded_root(self):
        self.root.rmdir()
        with self.assertRaises(ValueError):
            storage.validate_root(self.root)
        self.assertFalse(self.root.exists())

    # test_invalid_locator_values: Reject multiple values, relative roots and the wrong root name.
    def test_invalid_locator_values(self):
        for value in ('', 'relative', str(self.root) + '\nextra', str(self.app)):
            with self.subTest(value=value):
                (self.app / storage.LOCATOR_NAME).write_text(value, encoding='utf-8')
                with self.assertRaises(ValueError):
                    storage.read_locator(self.app)

    # test_unreadable_locator: Propagate a real read failure so startup can offer reselection.
    def test_unreadable_locator(self):
        with patch.object(Path, 'read_text', side_effect=PermissionError('denied')):
            with self.assertRaises(PermissionError):
                storage.read_locator(self.app)

    # test_preserves_data: Revalidating an existing tree does not rewrite its settings.
    def test_preserves_data(self):
        storage.validate_root(self.root)
        ini = self.root / 'Settings' / 'app_preferences.ini'
        ini.write_bytes(b'[Preferences]\r\nnms_save_folder = fixture-only\r\n')
        before = ini.read_bytes()
        storage.validate_root(self.root)
        self.assertEqual(ini.read_bytes(), before)

    # test_category_collision: An ordinary file where a directory belongs must not be overwritten.
    def test_category_collision(self):
        (self.root / 'Settings').write_bytes(b'KEEP')
        with self.assertRaises(OSError):
            storage.validate_root(self.root)
        self.assertEqual((self.root / 'Settings').read_bytes(), b'KEEP')

    # test_denied_root: Refuse an unwritable selected root instead of guessing another location.
    def test_denied_root(self):
        with patch.object(storage, 'check_writable', side_effect=PermissionError('denied')):
            with self.assertRaises(PermissionError):
                storage.validate_root(self.root)

    # test_proposed_local_parent: Use valid LOCALAPPDATA only as a dialog proposal.
    def test_proposed_local_parent(self):
        with patch.dict(os.environ, {'LOCALAPPDATA': str(self.base)}):
            self.assertEqual(storage.default_selection(self.app), self.root)
        self.assertIsNone(storage._data_root)

    # test_proposed_fallback: Missing or unusable LOCALAPPDATA proposes the application directory.
    def test_proposed_fallback(self):
        for value in ('', str(self.base / 'absent'), 'relative'):
            with patch.dict(os.environ, {'LOCALAPPDATA': value}):
                self.assertEqual(storage.default_selection(self.app), self.app / storage.DATA_NAME)
        with patch.dict(os.environ, {'LOCALAPPDATA': str(self.base)}):
            with patch.object(storage, 'check_writable', side_effect=PermissionError('denied')):
                self.assertEqual(storage.default_selection(self.app), self.app / storage.DATA_NAME)

    # test_locator_failure_preserves_previous: Failed atomic replacement retains the old value and cleans staging.
    def test_locator_failure_preserves_previous(self):
        storage.save_locator(self.app, self.root)
        with patch.object(storage.os, 'replace', side_effect=PermissionError('denied')):
            with self.assertRaises(PermissionError):
                storage.save_locator(self.app, self.app / storage.DATA_NAME)
        self.assertEqual((self.app / storage.LOCATOR_NAME).read_text(encoding='utf-8'), str(self.root))
        self.assertEqual(len(list(self.app.iterdir())), 1)

    # test_failure_wording: Include the target, practical remedies and the exact required closing line.
    def test_failure_wording(self):
        text = storage.locator_failure_text(self.app, PermissionError('fixture denied'))
        self.assertIn(str(self.app / storage.LOCATOR_NAME), text)
        self.assertIn('Recommended solutions:', text)
        self.assertTrue(text.endswith('Hit OK to Close the App...'))

    # test_paths_require_initialization: Prevent an uninitialized caller from falling back to an old location.
    def test_paths_require_initialization(self):
        storage._data_root = None
        with self.assertRaises(RuntimeError):
            storage.data_path('Settings')

    # test_category_routing_and_traversal: Backup shares the selected root and traversal is refused.
    def test_category_routing_and_traversal(self):
        storage._data_root = storage.validate_root(self.root)
        self.assertEqual(backup_ops.backup_root(), self.root / 'Backups' / 'Full NMS Save Backups')
        with self.assertRaises(ValueError):
            storage.data_path('..', 'outside')

    # test_safe_backup_suggestions: In-game labels cannot escape or change the default backup category.
    def test_safe_backup_suggestions(self):
        storage._data_root = storage.validate_root(self.root)
        for label in ('..\\..\\..\\outside', '..\\Contexts\\example', 'C:\\outside', 'a/b',
                      'CON', 'nul.json', '... ', '', 'name?*<>|', 'a' * 500, 'line\nfeed'):
            with self.subTest(label=label):
                suggestion = storage.suggested_backup_path('Bases', label)
                self.assertEqual(suggestion.parent, self.root / 'Backups' / 'Bases')
                self.assertTrue(suggestion.name)
                self.assertLessEqual(len(suggestion.name), 121)
                self.assertNotIn('\\', suggestion.name)
        self.assertEqual(storage.suggested_backup_path('Inventories', 'My Inventory').name, 'My Inventory')
    # test_valid_startup: A valid locator bypasses selection and publishes its recorded root.
    def test_valid_startup(self):
        from types import SimpleNamespace
        from unittest.mock import Mock
        storage.save_locator(self.app, self.root)
        messages = SimpleNamespace(warning=Mock(), critical=Mock(), Ok=1)
        with patch.dict('sys.modules', {'PyQt5.QtWidgets': SimpleNamespace(QMessageBox=messages)}):
            with patch.object(storage, 'application_root', return_value=self.app):
                with patch.object(storage, 'select_directory') as picker:
                    self.assertTrue(storage.initialize_storage())
                    picker.assert_not_called()
        self.assertEqual(storage.data_path(), self.root)

    # test_cancelled_startup: A missing locator never auto-selects an existing default root.
    def test_cancelled_startup(self):
        from types import SimpleNamespace
        from unittest.mock import Mock
        messages = SimpleNamespace(warning=Mock(), critical=Mock(), Ok=1)
        with patch.dict('sys.modules', {'PyQt5.QtWidgets': SimpleNamespace(QMessageBox=messages)}):
            with patch.object(storage, 'application_root', return_value=self.app):
                with patch.object(storage, 'select_directory', return_value=None):
                    self.assertFalse(storage.initialize_storage())
        self.assertIsNone(storage._data_root)
        self.assertFalse((self.app / storage.LOCATOR_NAME).exists())

    # test_selected_startup: A confirmed non-default root is recorded without substituting a default.
    def test_selected_startup(self):
        from types import SimpleNamespace
        from unittest.mock import Mock
        messages = SimpleNamespace(warning=Mock(), critical=Mock(), Ok=1)
        with patch.dict('sys.modules', {'PyQt5.QtWidgets': SimpleNamespace(QMessageBox=messages)}):
            with patch.object(storage, 'application_root', return_value=self.app):
                with patch.object(storage, 'select_directory', return_value=str(self.root)):
                    self.assertTrue(storage.initialize_storage())
        self.assertEqual(storage.read_locator(self.app), self.root)

    # test_locator_write_failure_exits: A failed locator write alerts without publishing app storage.
    def test_locator_write_failure_exits(self):
        from types import SimpleNamespace
        from unittest.mock import Mock
        storage.save_locator(self.app, self.root)
        messages = SimpleNamespace(warning=Mock(), critical=Mock(), Ok=1)
        with patch.dict('sys.modules', {'PyQt5.QtWidgets': SimpleNamespace(QMessageBox=messages)}):
            with patch.object(storage, 'application_root', return_value=self.app):
                with patch.object(storage, 'save_locator', side_effect=PermissionError('denied')):
                    self.assertFalse(storage.initialize_storage())
        self.assertIsNone(storage._data_root)
        self.assertTrue(messages.critical.call_args.args[2].endswith('Hit OK to Close the App...'))

    # test_startup_order: Initialize Qt, storage and preferences before the main window.
    def test_startup_order(self):
        text = Path(__file__).with_name('BBB_NMS_Save_File_Manipulator.py').read_text(encoding='utf-8')
        tree = ast.parse(text)
        main = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'main')
        calls = {ast.unparse(node.func): node.lineno for node in ast.walk(main) if isinstance(node, ast.Call)}
        self.assertLess(calls['QApplication'], calls['storage.initialize_storage'])
        self.assertLess(calls['storage.initialize_storage'], calls['ini_file_manager.initialize'])
        self.assertLess(calls['ini_file_manager.initialize'], calls['MainWindow'])


if __name__ == '__main__':
    unittest.main()  # Tests use only disposable fixtures and never initialize Qt or load a save.
