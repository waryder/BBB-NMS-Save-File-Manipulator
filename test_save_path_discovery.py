# File: test_save_path_discovery.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\test_save_path_discovery.py
# Purpose: Exercise real discovery/picker methods on synthetic metadata and dummy folders without app/Qt initialization.
import ast  # Extract production functions without importing the app or real preferences.
import os  # Restrict temporary I/O and set controlled fixture timestamps.
import struct  # Construct explicitly synthetic metadata fields.
import tempfile  # Own all fixture files under configured scratch.
import unittest  # Report executed isolated checks.
from pathlib import Path  # Read named source files and dummy fixtures only.
from types import SimpleNamespace  # Supply the small picker/UI interfaces under test.
from typing import Any, Dict, List  # Dynamic AST environments intentionally contain heterogeneous services.
from unittest.mock import Mock, patch  # Observe persistence, confirmations and picker arguments.
from nms_save_codec.meta_info import list_save_slots  # Actual read-only metadata scanner.
from nms_save_codec.xxtea import encrypt_meta  # Actual metadata encryption for synthetic records.
from nms_save_codec.slots import guess_slot_from_filename  # Match the real metadata key family.
import FullLiveSaveBackup as backup_ops  # Pure source-root resolver shared with manual Restore.

ROOT = Path(__file__).resolve().parent  # The named repository is the only production source read.


# load_dialog_code: Compile real functions and dialog methods against non-GUI interfaces.
def load_dialog_code():
    tree = ast.parse((ROOT / 'OpenNmsSaveFileDialog.py').read_text(encoding='utf-8'))  # No shared imports execute.
    nodes: List[ast.stmt] = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef))]  # Actual code, not a reimplementation.
    env: Dict[str, Any] = dict(os=os, list_save_slots=list_save_slots, logger=Mock(), QDialog=object, DEBUG_PREFIX='[BBB-NMS-SFM/OpenNmsSaveFileDialog]')  # Explicit dependencies.
    env.update(QMessageBox=SimpleNamespace(Ok=1, Cancel=2, warning=Mock(return_value=1)), slot_ops=SimpleNamespace(trace=Mock()))  # No modal windows.
    exec(compile(ast.Module(body=nodes, type_ignores=[]), 'actual-save-folder-methods', 'exec'), env)  # Methods run only when tests call them.
    return env  # Each test receives fresh mocks and function globals.


class SavePathDiscoveryTests(unittest.TestCase):
    # setUp: Isolate the NMS root, application environment and all generated fixture bytes.
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='nms-path-fixture-', dir=os.environ['TMPDIR'])  # Never the live AppData tree.
        self.addCleanup(self.tmp.cleanup)  # Remove only owned dummy data.
        self.root = Path(self.tmp.name) / 'HelloGames' / 'NMS'  # Conventional shape inside scratch.
        self.root.mkdir(parents=True)  # Fixture setup, not production discovery writes.
        self.env = load_dialog_code()  # No actual preferences or Qt initialized.
        self.env['NMS_SAVE_ROOT'] = str(self.root)  # Override before any discovery runs.
        self.patcher = patch.dict(os.environ, APPDATA=self.tmp.name)  # No missing-variable/current-directory ambiguity.
        self.patcher.start()  # Production APPDATA guard sees a controlled value.
        self.addCleanup(self.patcher.stop)  # Restore the environment after the test.

    # save: Make a data marker and properly encrypted synthetic metadata for the actual scanner.
    def save(self, account, timestamp, filename='save.hg'):
        folder = self.root / account  # Every account is underneath the owned fixture root.
        folder.mkdir(exist_ok=True)  # Multiple files may share one dummy account.
        (folder / filename).write_bytes(b'SYNTHETIC DATA MARKER - NOT A GAME SAVE')  # Discovery never decodes payloads.
        plain = bytearray(0x1B0)  # Current Steam/GOG metadata shape only.
        struct.pack_into('<I', plain, 0, 0xEEEEEEBE)  # Required successful-decryption marker.
        struct.pack_into('<I', plain, 0x164, timestamp)  # Embedded time is the only discovery ranking source.
        (folder / ('mf_' + filename)).write_bytes(encrypt_meta(bytes(plain), guess_slot_from_filename(filename)))  # Real cipher path.
        return str(folder)  # Production functions use native paths.

    # discover: Execute the real folder-discovery function against the isolated root.
    def discover(self):
        return self.env['find_default_save_folder']()  # No duplicated discovery algorithm in the test.

    # dialog: Supply only the interfaces used by the real picker and preference methods.
    def dialog(self, folder=''):
        obj = self.env['OpenNmsSaveFileDialog'].__new__(self.env['OpenNmsSaveFileDialog'])  # Skip GUI construction.
        obj.save_folder = folder  # Controlled selected location.
        obj.ini_file_manager = SimpleNamespace(get_nms_save_folder=Mock(return_value=folder), store_nms_save_folder=Mock())  # Dummy preferences only.
        obj.save_path_label, obj.storage_label = Mock(), Mock()  # Observe presented values without Qt.
        obj._populate_slots = Mock()  # Individual picker tests do not need slot-population work.
        return obj  # Actual production bound methods are retained.

    # test_latest_across_steam_and_gog: GOG can win over Steam using real decoded metadata.
    def test_latest_across_steam_and_gog(self):
        self.save('st_fixture', 100)  # Older Steam account.
        gog = self.save('DefaultUser', 300)  # Newer GOG account.
        self.assertEqual(self.discover(), gog)  # Compare across both supported platforms.

    # test_latest_across_slots_and_manual: Rank an account by its newest file, not its first slot.
    def test_latest_across_slots_and_manual(self):
        steam = self.save('st_fixture', 100)  # First Auto is not this account's latest.
        self.save('st_fixture', 500, 'save10.hg')  # Manual save in a later slot wins for its folder.
        self.save('DefaultUser', 300)  # GOG does not win merely from first-slot recency.
        self.assertEqual(self.discover(), steam)  # Do not change which slot the UI itself defaults to.

    # test_metadata_beats_filesystem_date: A newer filesystem timestamp cannot override embedded time.
    def test_metadata_beats_filesystem_date(self):
        steam = self.save('st_fixture', 600)  # Embedded winner.
        gog = self.save('DefaultUser', 100)  # Embedded loser.
        os.utime(Path(steam) / 'save.hg', (1000, 1000))  # Deliberately old filesystem date on the winner.
        os.utime(Path(gog) / 'save.hg', (2000000000, 2000000000))  # Deliberately newer filesystem date on the loser.
        self.assertEqual(self.discover(), steam)  # Actual metadata, not stat().st_mtime, decides.

    # test_tie_keeps_encountered_order_without_sorting: Explicitly reverse enumeration to distinguish first from alphabetical.
    def test_tie_keeps_encountered_order_without_sorting(self):
        first = self.save('st_z_fixture', 400)  # Alphabetically after the other account.
        self.save('st_a_fixture', 400)  # Identical embedded timestamp.
        real_listdir = os.listdir  # Keep the metadata scanner's own listing real.
        def listing(folder):  # listing: Override only the top-level account encounter order.
            return ['st_z_fixture', 'st_a_fixture'] if str(folder) == str(self.root) else real_listdir(folder)  # No accidental recursion.
        with patch.object(os, 'listdir', side_effect=listing):
            self.assertEqual(self.discover(), first)  # First encountered, no sorting or tie popup.
        self.env['QMessageBox'].warning.assert_not_called()  # Discovery never asks which tied account.

    # test_empty_unreadable_zero_and_other_folders_ignored: Only supported accounts with readable positive times compete.
    def test_empty_unreadable_zero_and_other_folders_ignored(self):
        (self.root / 'st_empty').mkdir()  # No save metadata.
        bad = Path(self.save('st_bad', 1000))  # Replace synthetic metadata with malformed bytes.
        (bad / 'mf_save.hg').write_bytes(b'BROKEN')  # Scanner records a per-file error.
        self.save('DefaultUser', 0)  # Missing positive embedded time.
        self.save('copied-backup', 9999)  # Not a conventional discovery target.
        self.assertEqual(self.discover(), '')  # Manual selection still remains available.

    # test_one_unreadable_account_does_not_block_another: Folder-level failures are isolated.
    def test_one_unreadable_account_does_not_block_another(self):
        good = self.save('DefaultUser', 200)  # Accessible candidate.
        (self.root / 'st_denied').mkdir()  # Simulated inaccessible candidate.
        real_scanner = self.env['list_save_slots']  # Actual scanner for the good account.
        def scan(folder):  # scan: Simulate permission denial only for one explicitly named fixture.
            if str(folder).endswith('st_denied'): raise PermissionError('synthetic denial')  # No real ACL changes.
            return real_scanner(folder)  # Keep actual metadata decoding elsewhere.
        self.env['list_save_slots'] = scan  # Control the production function's injected dependency.
        self.assertEqual(self.discover(), good)  # Continue to accessible accounts.
        self.env['logger'].error.assert_called()  # Never silently claim a failed read succeeded.

    # test_missing_root_or_appdata_returns_empty: Never accidentally discover relative to the app's directory.
    def test_missing_root_or_appdata_returns_empty(self):
        self.env['NMS_SAVE_ROOT'] = str(self.root / 'missing')  # No such fixture root.
        self.assertEqual(self.discover(), '')  # Normal no-candidate outcome.
        self.env['NMS_SAVE_ROOT'] = str(self.root)  # Restore an existing fixture root.
        with patch.dict(os.environ, clear=True):
            self.assertEqual(self.discover(), '')  # Missing APPDATA is not permission to search the current directory.

    # test_remembered_path_wins_over_newer_discovery: Reopen remains at the last accepted directory.
    def test_remembered_path_wins_over_newer_discovery(self):
        remembered = self.save('st_fixture', 100)  # User's accepted account.
        self.save('DefaultUser', 9999)  # Other newer account must not redirect the app.
        obj = self.dialog(remembered)  # Actual helper receives only dummy preferences.
        self.assertEqual(self.env['get_initial_save_folder'](obj.ini_file_manager), remembered)  # Reopened Save Path.
        self.assertEqual(obj._picker_start_folder(), remembered)  # Picker also stays at the existing accepted account.
        obj.ini_file_manager.store_nms_save_folder.assert_not_called()  # Reading never rewrites preferences.

    # test_missing_remembered_path_clears_then_discovers_only_for_picker: No silent account fallback on Open.
    def test_missing_remembered_path_clears_then_discovers_only_for_picker(self):
        newest = self.save('DefaultUser', 300)  # Replacement suggestion exists.
        obj = self.dialog(str(self.root / 'st_gone'))  # Stale preference without that directory.
        self.assertEqual(self.env['get_initial_save_folder'](obj.ini_file_manager), '')  # Blank initial Save Path.
        self.assertEqual(obj._picker_start_folder(), newest)  # Discovery waits until Pick Folder is invoked.
        obj.ini_file_manager.store_nms_save_folder.assert_not_called()  # No automatic write/selection.

    # test_picker_cancel_has_no_side_effects: Cancel must not persist or populate the suggestion.
    def test_picker_cancel_has_no_side_effects(self):
        candidate = self.save('DefaultUser', 300)  # Initial directory suggestion only.
        obj = self.dialog()  # First-use state remains blank until acceptance.
        picker = SimpleNamespace(ShowDirsOnly=1, getExistingDirectory=Mock(return_value=''))  # Simulate native Cancel.
        self.env['QFileDialog'] = picker  # No real native window opens.
        obj._on_pick_folder_clicked()  # Real handler, discovery, and cancellation branch.
        self.assertEqual(picker.getExistingDirectory.call_args.args[2], candidate)  # Newest account suggested to picker.
        self.assertEqual(obj.save_folder, '')  # Cancel does not commit a discovered path.
        obj.ini_file_manager.store_nms_save_folder.assert_not_called()  # No preference write.
        obj._populate_slots.assert_not_called()  # Existing selection details unchanged.

    # test_manual_selection_persists_and_reopens: User override is remembered through the same production methods.
    def test_manual_selection_persists_and_reopens(self):
        self.save('st_latest', 9999)  # Discovery candidate may be overridden.
        manual = self.save('DefaultUser', 100)  # Explicitly selected older account.
        obj = self.dialog()  # Empty prior path.
        self.env['QFileDialog'] = SimpleNamespace(ShowDirsOnly=1, getExistingDirectory=Mock(return_value=manual))  # Manual picker result.
        obj._on_pick_folder_clicked()  # Real confirm/persist/update flow.
        obj.ini_file_manager.store_nms_save_folder.assert_called_once_with(manual)  # Durable store API used.
        self.assertEqual(obj.save_folder, manual)  # Selection, not discovery recency, is authoritative.
        obj._populate_slots.assert_called_once()  # Refresh existing slot workflow after accepted selection.
        obj.ini_file_manager.get_nms_save_folder.return_value = manual  # Simulate the next app start's stored value.
        self.assertEqual(self.env['get_initial_save_folder'](obj.ini_file_manager), manual)  # Reopen at accepted account.

    # test_preference_cancel_and_failure_preserve_selection: No display/model update before successful persistence.
    def test_preference_cancel_and_failure_preserve_selection(self):
        current, other = self.save('st_current', 100), self.save('DefaultUser', 200)  # Both paths exist.
        obj = self.dialog(current)  # Existing selected account.
        self.env['QMessageBox'].warning.return_value = 2  # Existing write warning cancelled.
        obj._apply_save_folder(other)  # No store or UI update.
        obj.ini_file_manager.store_nms_save_folder.assert_not_called()  # Consent boundary retained.
        self.env['QMessageBox'].warning.return_value = 1  # Consent for a failing preference write.
        obj.ini_file_manager.store_nms_save_folder.side_effect = OSError('synthetic write failure')  # No real configuration changed.
        obj._apply_save_folder(other)  # Report failure while keeping the old folder.
        self.assertEqual(obj.save_folder, current)  # Never show an unpersisted replacement.
        obj._populate_slots.assert_not_called()  # Existing details stay intact on either refusal.

    # test_picker_discovery_error_still_allows_manual_browsing: Root read errors cannot crash the picker.
    def test_picker_discovery_error_still_allows_manual_browsing(self):
        obj = self.dialog()  # No selected account.
        self.env['find_default_save_folder'] = Mock(side_effect=PermissionError('synthetic root denial'))  # Simulate directory listing failure.
        self.assertEqual(obj._picker_start_folder(), '')  # Native default/manual browsing remains available.
        self.env['logger'].error.assert_called()  # Surface the real failure.

    # test_storage_labels_and_population: Platform display tracks the account while slot order remains unchanged.
    def test_storage_labels_and_population(self):
        for name, expected in [('st_fixture', 'Steam'), ('DefaultUser', 'GOG'), ('copied-folder', 'Steam/GOG'), ('', '')]:
            self.assertEqual(self.env['storage_label'](str(self.root / name) if name else ''), expected)  # Exact labels.
        obj = self.dialog(self.save('DefaultUser', 300))  # Actual metadata for one GOG slot.
        obj.slot_combo, obj.file_combo, obj._on_file_changed = Mock(), Mock(), Mock()  # No actual Qt or auto-selection behavior changed.
        self.env['OpenNmsSaveFileDialog']._populate_slots(obj)  # Execute production method rather than mocked instance method.
        obj.storage_label.setText.assert_called_once_with('GOG')  # Correct platform on population.
        obj.slot_combo.addItem.assert_called_once()  # Existing metadata slot-population path works.

    # test_backup_and_manual_restore_share_both_platform_roots: Both account names expand to the same whole-NMS tree.
    def test_backup_and_manual_restore_share_both_platform_roots(self):
        for name in ('st_fixture', 'DefaultUser'):
            selected = self.save(name, 300)  # Only dummy files.
            self.assertEqual(backup_ops.source_root(selected), self.root)  # Resolver used by both Backup and manual Restore.
        with self.assertRaises(ValueError): backup_ops.source_root(self.root / 'st_missing')  # No missing-account expansion.
        with self.assertRaises(ValueError): backup_ops.source_root(self.root / 'DefaultUser_missing')  # No arbitrary source expansion.

    # test_gog_full_backup_copies_accounts_without_source_changes: Exercise actual production copy/verification on dummy data.
    def test_gog_full_backup_copies_accounts_without_source_changes(self):
        selected = self.save('DefaultUser', 300)  # GOG chosen account.
        self.save('st_fixture', 100)  # Whole-NMS scope includes Steam as before.
        before = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}  # Fixture-only inventory.
        app_root = Path(self.tmp.name) / 'dummy-app'  # Destination is outside the dummy source tree.
        app_root.mkdir()  # Explicit fixture setup.
        plan = backup_ops.plan_backup(selected, app_root=app_root)  # Real root resolution and preflight.
        result = Path(backup_ops.execute_backup(plan, confirmed=True))  # Real copy, no live paths involved.
        after = {str(p.relative_to(result)): p.read_bytes() for p in result.rglob('*') if p.is_file()}  # Read back copied fixture bytes.
        self.assertEqual(after, before)  # All accounts included and byte-verified.
        self.assertEqual({str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}, before)  # Source unchanged.


if __name__ == '__main__':
    unittest.main(verbosity=2)  # Run on Gaming PC only, without Qt/app/real save access.
