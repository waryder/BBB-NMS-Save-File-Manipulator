# File: FullLiveSaveBackupController.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\FullLiveSaveBackupController.py
# Purpose: Present Save/Cancel for a reviewed full live-folder backup, preserving editor state.
from imports import *  # Reuse the application's existing Qt/message/progress components.
import FullLiveSaveBackup as backup_ops  # Qt-free planning, copy and verification.
import NmsSlotOperations as slot_ops  # Reuse the existing single gated trace switch.
from OpenNmsSaveFileDialog import get_initial_save_folder  # Exactly the same source preference/default as File > Open.


class FullLiveSaveBackupController:  # One short-lived request, independent of loaded slot/model/dirty LEDs.
    DEBUG_PREFIX = '[BBB-NMS-SFM/FullLiveSaveBackupController]'  # Always identify errors by project and source.

    # __init__: Retain the owner without starting a backup or inspecting game files.
    def __init__(self, window):
        self.window = window  # The actual main window supplies preferences and existing activity guards.

    # run: Refuse reentrancy and restore the original guard/interaction state after every outcome.
    def run(self):
        window = self.window  # Keep lifetime ownership explicit.
        if window._nms_loading:  # Another load/save/backup owns the transaction guard.
            return False  # Do not open a nested confirmation or touch files.
        enabled = window.isEnabled()  # Respect a previously disabled owner on cleanup.
        window._nms_loading = True  # Block nested load/save requests while modal dialogs process events.
        try:
            return self._request()  # Planning is read-only; confirmation gates all output creation.
        except Exception as exc:
            print(f'{self.DEBUG_PREFIX} run: ERROR {exc}', flush=True)  # Never suppress errors with the debug switch.
            QMessageBox.warning(window, 'Full Live Save Backup Failed', str(exc))  # No successful-backup claim.
            return False  # Original editor model/source/LEDs remain untouched.
        finally:
            window._nms_loading = False  # Restore the prior false guard after success, Cancel or error.
            window.setEnabled(enabled)  # Do not leave the app disabled on failure.

    # _request: Plan the exact full source and destination before asking for explicit Save consent.
    def _request(self):
        folder = get_initial_save_folder(self.window.ini_file_manager, self.window)  # No new preference or picker.
        plan = backup_ops.plan_backup(folder)  # Read-only source inventory, size and destination-volume space.
        slot_ops.trace('FullLiveSaveBackupController', 'backup_proposed', source=str(plan.source), destination=str(plan.destination), bytes=plan.total_bytes)  # No save JSON.
        reply = QMessageBox.warning(self.window, 'Full Live Save Backup', backup_ops.confirmation_text(plan),
                                   QMessageBox.Save | QMessageBox.Cancel, QMessageBox.Cancel)  # Only Save authorizes writes.
        if reply != QMessageBox.Save:  # Escape/window close/Cancel are identical no-write outcomes.
            return False  # No backup root, destination, progress popup or success notice is created.
        destination = self._copy(plan)  # Verify the exact approved proposal before reporting success.
        QMessageBox.information(self.window, 'Full Live Save Backup', f'Backup complete and verified:\n{destination}')  # Exact resulting Windows path.
        return True  # Actual GUI acceptance remains Bill-run.

    # _copy: Paint existing progress while synchronous copying and verification own the app guard.
    def _copy(self, plan):
        progress = None  # Also clean up a partially constructed dialog.
        self.window.setEnabled(False)  # Prevent editor changes while copying.
        try:
            progress = TextOnlyLoadingDialog('Backing up live save files, please wait…', self.window)  # Existing visual design.
            progress.setEnabled(True)  # Child progress must remain paintable with a disabled owner.
            progress.show()  # No guessed timer or nested exec loop.
            QApplication.processEvents(QEventLoop.ExcludeUserInputEvents)  # Paint before synchronous I/O.
            return backup_ops.execute_backup(plan, confirmed=True)  # Only the explicit Save branch reaches this writer.
        finally:
            if progress is not None:  # Error setup or copy cannot strand the popup.
                progress.accept()  # Programmatic completion of this short-lived progress dialog.
                progress.deleteLater()  # Release it before success/error notification.
