# File: test_full_live_save_long_paths.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\test_full_live_save_long_paths.py
# Purpose: Exercise extended-length backup paths using disposable dummy files only.
import datetime  # Use deterministic backup naming.
import os  # Skip Windows-specific tests on other systems.
import shutil  # Clean up extended-length temporary trees.
import tempfile  # Isolate all test data from actual saves.
import unittest  # Report actual Windows filesystem results.
from pathlib import Path  # Build ordinary paths for proposals and display.
from unittest.mock import patch  # Inject a controlled verification failure.
import FullLiveSaveBackup as ops  # Import only the filesystem backup engine.


@unittest.skipUnless(os.name == 'nt', 'Windows extended-length paths only')
class LongPathTests(unittest.TestCase):
    # setUp: Create a short disposable root with long dummy source and destination descendants.
    def setUp(self):
        base = Path(r'C:\Users\Public\Claude\WindowsAutomation\scratch')  # Existing automation scratch location.
        base.mkdir(exist_ok=True)  # Never use any real save location.
        self.root = Path(tempfile.mkdtemp(prefix='backup-long-', dir=base))  # Unique fixture ownership.
        self.addCleanup(lambda: shutil.rmtree(ops._io_path(self.root)))  # Remove long files with the same namespace.
        self.source = self.root / ('source-' + 's' * 90) / 'NMS'  # Force long source paths independently of backup naming.
        self.account = self.source / 'st_dummy'  # Deliberately not a real Steam ID.
        self.relative = Path('st_dummy') / 'cache' / ('dummy-' + 'f' * 120 + '.DDS')  # Legal component length.
        ops._io_path(self.source / self.relative).parent.mkdir(parents=True)  # Extended source mkdir.
        ops._io_path(self.source / self.relative).write_bytes(b'DUMMY LONG PATH CONTENT')  # No game data.
        ops._io_path(self.account / 'cache' / ('empty-' + 'e' * 100)).mkdir()  # Long empty directory coverage.
        self.app = self.root / ('app-' + 'a' * 100)  # Long target paths independent of source depth.
        ops._io_path(self.app).mkdir()  # Prepare fixture-only app root.
        self.plan = ops.plan_backup(self.account, self.app, datetime.datetime(2026, 1, 2, 3, 4, 5))  # Real preflight.

    # test_extended_write_copy_and_verification: Execute production copy/metadata/hash checks over long paths.
    def test_extended_write_copy_and_verification(self):
        target = self.plan.destination / self.relative  # Ordinary output path exceeds the legacy limit.
        self.assertGreater(len(str(self.source / self.relative)), 260)  # Confirm long source coverage.
        self.assertGreater(len(str(target)), 260)  # Confirm long destination coverage.
        self.assertNotIn('\\\\?\\', ops.confirmation_text(self.plan))  # Keep UI paths ordinary.
        self.assertFalse(ops._io_path(self.plan.destination).exists())  # No output before Save.
        self.assertEqual(ops.execute_backup(self.plan, confirmed=True), str(self.plan.destination))  # Ordinary success path.
        self.assertEqual(ops._io_path(target).read_bytes(), b'DUMMY LONG PATH CONTENT')  # Actual read-back.
        self.assertEqual(ops.inventory(self.source), self.plan.entries)  # Source identity and metadata remain unchanged.
        shape = lambda entries: [(e.relative, e.directory, e.size) for e in entries]  # Compare structure without inode identity.
        self.assertEqual(shape(ops.inventory(self.source)), shape(ops.inventory(self.plan.destination)))  # Every entry copied.
        self.assertTrue(ops._io_path(self.plan.destination / 'st_dummy' / 'cache' / ('empty-' + 'e' * 100)).is_dir())  # Empty directory retained.
        print('Verified long source length:', len(str(self.source / self.relative)), 'destination length:', len(str(target)))  # Visible test evidence.

    # test_long_failure_cleanup: A failure after long files are copied removes only the new incomplete backup.
    def test_long_failure_cleanup(self):
        copy = ops.shutil.copy2  # Preserve real copying before injecting bad content.
        def corrupt(source, destination, **kwargs):
            result = copy(source, destination, **kwargs)  # First exercise the real long-path copy.
            Path(destination).write_bytes(b'CORRUPT')  # Trigger existing hash verification failure.
            return result  # The production verifier must refuse success.
        with patch.object(ops.shutil, 'copy2', side_effect=corrupt):  # No actual save activity.
            with self.assertRaisesRegex(ValueError, 'verification'):  # Ensure failure is detected.
                ops.execute_backup(self.plan, confirmed=True)  # Run against dummy directories only.
        self.assertFalse(ops._io_path(self.plan.destination).exists())  # Long incomplete backup removed.
        self.assertEqual(ops._io_path(self.source / self.relative).read_bytes(), b'DUMMY LONG PATH CONTENT')  # Source preserved.

    # test_prefix_conversion: Local, UNC and already-prefixed paths convert without duplication or network access.
    def test_prefix_conversion(self):
        prefix = chr(92) * 2 + '?' + chr(92)  # Literal namespace prefix, not a filesystem location.
        local = ops._io_path(self.source)  # Real local path conversion.
        self.assertEqual(str(local), prefix + str(self.source))  # Exact local namespace form.
        self.assertEqual(ops._io_path(local), local)  # Idempotent conversion.
        unc = chr(92) * 2 + 'server\\share\\folder'  # Synthetic UNC name; do not access it.
        self.assertEqual(str(ops._io_path(unc)), prefix + 'UNC\\server\\share\\folder')  # Exact UNC namespace form.
        self.assertEqual(ops._io_path(ops._io_path(unc)), ops._io_path(unc))  # UNC conversion is also idempotent.


if __name__ == '__main__':
    unittest.main(verbosity=2)  # Run dummy filesystem tests without launching the application.
