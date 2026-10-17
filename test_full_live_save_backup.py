# File: test_full_live_save_backup.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\test_full_live_save_backup.py
# Purpose: Synthetic full-folder backup and controller checks; never open actual saves or initialize Qt.
import ast  # Execute isolated production controller methods without GUI imports.
import datetime  # Fix proposed names for deterministic assertions.
import os  # Keep temporary fixtures in the configured scratch directory.
import tempfile  # Create disposable dummy sources/destinations only.
import unittest  # Report executed acceptance-boundary checks.
from pathlib import Path  # Read named production sources and temporary dummy files.
from types import SimpleNamespace  # Explicit synthetic Qt interfaces.
from unittest.mock import patch  # Simulate failures without touching protected files.
import FullLiveSaveBackup as ops  # Pure operations have no app/GUI or preference initialization.

ROOT = Path(__file__).resolve().parent  # Source code under test.
NOW = datetime.datetime(2026, 1, 2, 3, 4, 5)  # Controlled fixture timestamp, not a claim about current time.


# extracted_class: Compile the actual controller class against explicitly supplied synthetic services.
def extracted_class(env):
    tree = ast.parse((ROOT / 'FullLiveSaveBackupController.py').read_text(encoding='utf-8'))  # No Qt imports.
    node = next(n for n in tree.body if isinstance(n, ast.ClassDef))  # Dedicated controller only.
    exec(compile(ast.Module(body=[node], type_ignores=[]), 'backup-controller-fixture', 'exec'), env)  # Real methods.
    return env['FullLiveSaveBackupController']  # Caller owns the synthetic window.


class BackupTests(unittest.TestCase):
    # setUp: Prepare representative multiple-account/root/hidden/empty-directory dummy data.
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='nms-full-backup-test-', dir=os.environ.get('TMPDIR'))  # Scratch only.
        self.addCleanup(self.tmp.cleanup)  # Remove test artifacts, never real game data.
        self.root = Path(self.tmp.name)  # Every I/O target stays under this temporary root.
        self.source = self.root / 'Users' / 'billr' / 'AppData' / 'Roaming' / 'HelloGames' / 'NMS'  # Dummy Steam-shaped tree.
        self.selected = self.source / 'st_123'  # Selected account, not a live Steam ID.
        (self.selected / 'cache' / 'empty').mkdir(parents=True)  # Empty subdirectories matter.
        (self.source / 'st_456').mkdir()  # A second account must also be copied.
        (self.selected / 'save.hg').write_bytes(b'DUMMY\x00DATA')  # Deliberately not a real NMS save.
        (self.source / 'st_456' / 'mf_save.hg').write_bytes(b'DUMMY META')  # All file types must copy.
        (self.source / '.root-file').write_bytes(b'DUMMY ROOT')  # Root/hidden-style file included.
        self.app = self.root / 'application root'  # Spaces in native destination paths.
        self.app.mkdir()  # Existing source/executable application directory.

    # plan: Build the exact proposal using only this test's dummy source and destination.
    def plan(self):
        return ops.plan_backup(str(self.selected), self.app, NOW)  # No actual default/application paths used.

    # tree_bytes: Compare file bytes and empty-directory structure under a dummy root.
    def tree_bytes(self, root):
        return {str(p.relative_to(root)): None if p.is_dir() else p.read_bytes() for p in root.rglob('*')}  # Fixture-only traversal.

    # test_preflight_paths_and_space: Preflight reproduces the BAT structure without making backup directories.
    def test_preflight_paths_and_space(self):
        plan = self.plan()  # Read-only dummy inventory.
        self.assertEqual(plan.source, self.source)  # Whole NMS, not selected st_* alone.
        self.assertEqual(plan.destination, self.app / 'Full NMS Save Backups' / 'billr_AppData_Roaming_HelloGames_NMS_2026_01_02_03_04_05')  # Exact structure.
        self.assertEqual(plan.total_bytes, sum(len(v) for v in self.tree_bytes(self.source).values() if v is not None))  # Real dummy byte total.
        self.assertFalse(plan.destination.parent.exists())  # No mkdir before Save.
        self.assertGreater(plan.free_bytes, 0)  # Real destination-volume free-space query.
        self.assertEqual(ops.source_root(self.source), self.source)  # Direct NMS selection also supported.

    # test_confirmation_content: Paths, MB values and the requested question use the retained proposal.
    def test_confirmation_content(self):
        plan = self.plan()  # No writes.
        text = ops.confirmation_text(plan)  # Actual formatter.
        self.assertIn(f'from {plan.source} into new directory {plan.destination};', text)  # Full paths.
        self.assertIn(f'{plan.total_bytes / 1000000:,.2f} MB new disk usage', text)  # Decimal MB.
        self.assertIn(f'{(plan.free_bytes - plan.total_bytes) / 1000000:,.2f} MB free. Proceed?', text)  # Expected remaining free space.
        self.assertIn('estimates', text)  # Do not present logical payload as guaranteed physical allocation.

    # test_success_copies_all_accounts_and_empty_directories: Real dummy file I/O exercises the production copier.
    def test_success_copies_all_accounts_and_empty_directories(self):
        before, plan = self.tree_bytes(self.source), self.plan()  # Capture original dummy tree.
        result = ops.execute_backup(plan, confirmed=True)  # Approved fixture-only copy.
        self.assertEqual(result, str(plan.destination))  # Exact verified output.
        self.assertEqual(self.tree_bytes(plan.destination), before)  # Complete structure and content.
        self.assertEqual(self.tree_bytes(self.source), before)  # Source untouched.
        self.assertTrue((plan.destination / 'st_123' / 'cache' / 'empty').is_dir())  # Empty directories copied.

    # test_requires_literal_consent: No truthy substitute may cause directory creation.
    def test_requires_literal_consent(self):
        plan = self.plan()  # No output created.
        for consent in (False, None, 'Save', 1):
            with self.assertRaises(PermissionError): ops.execute_backup(plan, confirmed=consent)  # Only literal True.
        self.assertFalse(plan.destination.parent.exists())  # No write on refusal.

    # test_no_merge_and_collision_after_review: A destination appearing during confirmation remains untouched.
    def test_no_merge_and_collision_after_review(self):
        plan = self.plan()  # Fresh target initially absent.
        plan.destination.mkdir(parents=True)  # Simulate another backup winning the destination.
        marker = plan.destination / 'existing.txt'  # Prove no overwrite or cleanup of another backup.
        marker.write_bytes(b'KEEP')  # Fixture output owned by another operation.
        with self.assertRaises(FileExistsError): ops.execute_backup(plan, confirmed=True)  # Fail before copy.
        self.assertEqual(marker.read_bytes(), b'KEEP')  # Preserve existing contents.
        with self.assertRaises(FileExistsError): self.plan()  # Preflight also refuses timestamp collisions.

    # test_changed_source_aborts_before_output: Source edits during confirmation require a new proposal.
    def test_changed_source_aborts_before_output(self):
        plan = self.plan()  # Inventory before change.
        (self.selected / 'new.txt').write_bytes(b'CHANGED')  # Simulate external game/file activity.
        with self.assertRaisesRegex(ValueError, 'changed during confirmation'): ops.execute_backup(plan, confirmed=True)
        self.assertFalse(plan.destination.parent.exists())  # No output was created.

    # test_space_rechecked: Both proposal and Save refuse insufficient free space.
    def test_space_rechecked(self):
        plan = self.plan()  # Valid original proposal.
        with patch.object(ops, '_free_space', return_value=0):  # No actual disk exhaustion.
            with self.assertRaises(OSError): self.plan()  # Preflight failure.
            with self.assertRaises(OSError): ops.execute_backup(plan, confirmed=True)  # Save-time failure.
        self.assertFalse(plan.destination.parent.exists())  # No output writes.

    # test_copy_failure_cleans_only_own_target: Permission/copy errors cannot leave a claimed complete backup.
    def test_copy_failure_cleans_only_own_target(self):
        plan, before = self.plan(), self.tree_bytes(self.source)  # Original source capture.
        sibling = plan.destination.parent / 'older-backup'  # Existing backup must survive failure cleanup.
        sibling.mkdir(parents=True)  # Dummy sibling only.
        with patch.object(ops.shutil, 'copy2', side_effect=OSError('synthetic copy failure')):
            with self.assertRaisesRegex(OSError, 'synthetic'): ops.execute_backup(plan, confirmed=True)
        self.assertFalse(plan.destination.exists())  # Incomplete target removed.
        self.assertTrue(sibling.exists())  # Existing backup preserved.
        self.assertEqual(self.tree_bytes(self.source), before)  # Source unchanged.

    # test_verification_failure_is_not_success: Corrupted destination bytes are detected and removed.
    def test_verification_failure_is_not_success(self):
        plan = self.plan()  # Retain verified dummy source proposal.
        def corrupt(source, destination, **unused):
            Path(destination).write_bytes(b'CORRUPT')  # Deliberately violate the actual copy contract.
        with patch.object(ops.shutil, 'copy2', side_effect=corrupt):
            with self.assertRaisesRegex(ValueError, 'verification'): ops.execute_backup(plan, confirmed=True)
        self.assertFalse(plan.destination.exists())  # No success with corrupted files.

    # test_source_change_during_copy_is_detected: A new file during copying aborts the whole backup.
    def test_source_change_during_copy_is_detected(self):
        plan, copy = self.plan(), ops.shutil.copy2  # Actual copy function for ordinary dummy data.
        def mutate(source, destination, **kwargs):
            result = copy(source, destination, **kwargs)  # Copy the current dummy file normally.
            (self.source / 'new-during-copy').write_bytes(b'NEW')  # Simulated concurrent change.
            return result  # End-of-copy inventory must reject omission of this file.
        with patch.object(ops.shutil, 'copy2', side_effect=mutate):
            with self.assertRaisesRegex(ValueError, 'changed during copying'): ops.execute_backup(plan, confirmed=True)
        self.assertFalse(plan.destination.exists())  # No incomplete backup retained.

    # test_missing_and_overlapping_sources_refused: Fail closed instead of backing up arbitrary parents recursively.
    def test_missing_and_overlapping_sources_refused(self):
        for value in ('', self.root / 'missing', self.root):
            with self.assertRaises(ValueError): ops.source_root(value)  # No cwd or arbitrary parent fallback.
        with self.assertRaises(ValueError): ops.plan_backup(self.selected, self.source, NOW)  # Destination inside source.

    # test_reparse_entries_refused: Reparse points are not silently followed or excluded.
    def test_reparse_entries_refused(self):
        fake = SimpleNamespace(st_mode=0o100644, st_file_attributes=0x400)  # Windows reparse-point metadata.
        path = SimpleNamespace(lstat=lambda: fake)  # No actual junction/system modification needed.
        with self.assertRaisesRegex(ValueError, 'reparse'): ops._checked_stat(path)  # Fail clearly.

    # test_application_roots: Backups stay beside source or executable, never the current/extraction directory.
    def test_application_roots(self):
        with patch.object(ops.sys, 'frozen', False, create=True):
            self.assertEqual(ops.application_root(), ROOT)  # Actual source module root.
        with patch.object(ops.sys, 'frozen', True, create=True), patch.object(ops.sys, 'executable', str(self.app / 'editor.exe')):
            self.assertEqual(ops.application_root(), self.app)  # Simulated packaged executable location.


class ControllerTests(unittest.TestCase):
    # exercise: Execute the real controller with fake widgets and no game/save dependencies.
    def exercise(self, mode):
        events, notices = [], []  # Observe consent and cleanup order.
        window = SimpleNamespace(_nms_loading=mode == 'busy', enabled=True, ini_file_manager=object())  # No app initialization.
        window.isEnabled = lambda: window.enabled  # Synthetic owner interface.
        window.setEnabled = lambda value: setattr(window, 'enabled', value)  # Interaction restoration.
        plan = SimpleNamespace(source='fixture-source', destination='fixture-output', total_bytes=123)  # No real filesystem path.
        box = SimpleNamespace(Save=1, Cancel=2, warning=lambda *args: notices.append(args) or (1 if mode != 'cancel' else 2), information=lambda *args: events.append('success'))  # Save/Cancel.
        env = {'QMessageBox': box, 'get_initial_save_folder': lambda *args: 'fixture-folder', 'slot_ops': SimpleNamespace(trace=lambda *args, **kwargs: None)}  # Explicit dependencies.
        def write(proposal, confirmed):
            self.assertIs(proposal, plan)  # Exact retained proposal, not a regenerated timestamp.
            self.assertTrue(confirmed)  # Save branch only.
            events.append('copy')  # No actual files accessed.
            if mode == 'failure': raise OSError('synthetic copy error')  # Exercise cleanup and warning.
            return 'fixture-output'  # Synthetic verified target.
        env['backup_ops'] = SimpleNamespace(plan_backup=lambda folder: plan, confirmation_text=lambda plan: 'fixture confirmation', execute_backup=write)  # No source/default reads.
        class Progress:  # Explicitly fake UI lifecycle.
            def __init__(self, *args): events.append('progress')  # Only Save may construct progress.
            def setEnabled(self, value): pass  # No Qt state.
            def show(self): events.append('show')  # Before copy.
            def accept(self): events.append('dismiss')  # Before notification.
            def deleteLater(self): pass  # No QObject exists.
        env.update(TextOnlyLoadingDialog=Progress, QApplication=SimpleNamespace(processEvents=lambda flags: None), QEventLoop=SimpleNamespace(ExcludeUserInputEvents=0))  # No app/event loop.
        controller = extracted_class(env)(window)  # Actual production request controller.
        result = controller.run()  # Real control flow.
        self.assertTrue(window.enabled)  # No stranded disabled main window.
        self.assertEqual(window._nms_loading, mode == 'busy')  # Preserve existing activity guard.
        return result, events, notices  # Assertions distinguish Save, Cancel, failure and reentrancy.

    # test_save_cancel_failure_and_busy: Every controller outcome preserves the owner and consent boundary.
    def test_save_cancel_failure_and_busy(self):
        for mode in ('success', 'cancel', 'failure', 'busy'):
            with self.subTest(mode=mode):
                result, events, notices = self.exercise(mode)  # Actual controller bodies.
                self.assertEqual(result, mode == 'success')  # Never claim success after failure/Cancel.
                if mode in ('cancel', 'busy'): self.assertEqual(events, [])  # No post-Cancel action.
                if mode == 'busy': self.assertEqual(notices, [])  # No nested popup.
                if mode in ('success', 'failure'):
                    self.assertLess(events.index('show'), events.index('copy'))  # Paint before I/O.
                    self.assertIn('dismiss', events)  # Cleanup on success and failure.
                if mode == 'success': self.assertLess(events.index('dismiss'), events.index('success'))  # Notification after cleanup.

    # test_shared_folder_policy_and_spacing: Source discovery stays shared and both rows get one font-height blank line.
    def test_shared_folder_policy_and_spacing(self):
        main = (ROOT / 'BBB_NMS_Save_File_Manipulator.py').read_text(encoding='utf-8')  # Integration source.
        tree = ast.parse(main)  # No MainWindow construction.
        layout_calls = sorted((n.lineno, n.func.attr) for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name) and n.func.value.id == 'main_layout')  # Actual order.
        self.assertEqual([name for _, name in layout_calls][:5], ['addLayout', 'addSpacing', 'addLayout', 'addSpacing', 'addWidget'])  # One line after each row.
        self.assertEqual(main.count('main_layout.addSpacing(self.fontMetrics().lineSpacing())'), 2)  # Font-relative line height.
        dialog = (ROOT / 'OpenNmsSaveFileDialog.py').read_text(encoding='utf-8')  # Shared selection integration.
        self.assertIn('return get_initial_save_folder(self.ini_file_manager, self)', dialog)  # Open and Backup share one helper.
        for filename in ('FullLiveSaveBackup.py', 'FullLiveSaveBackupController.py', 'OpenNmsSaveFileDialog.py', 'BBB_NMS_Save_File_Manipulator.py'):
            source = (ROOT / filename).read_text(encoding='utf-8')  # Scope-only reads.
            ast.parse(source, feature_version=(3, 12))  # Gaming-PC target grammar.


if __name__ == '__main__':
    unittest.main(verbosity=2)  # Explicit synthetic-only console invocation.
