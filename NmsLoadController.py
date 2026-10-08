# File: NmsLoadController.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\NmsLoadController.py
# Purpose: Row-40 GUI load/restore transactions, live target identity, dirty LED and confirmed backups.
from imports import *  # Use the application's existing Qt widgets and helpers.
import copy  # Preserve previous model state for rollback and independent editing.
import hashlib  # Compare model and live-source bytes without logging save contents.
import NmsSlotOperations as slot_ops  # Share one global stdout tracing switch and selector.


class NmsLoadController:  # Mix row-40 operations into the existing main window.
    DEBUG_PREFIX = "[BBB-NMS-SFM/NmsLoadController]"  # Identify this source in diagnostics.

    # init_nms_load_state: Initialize retained source and observe all four editing tabs.
    def init_nms_load_state(self):
        self.nms_source = None  # No live identity belongs to startup placeholder/clipboard data.
        self.nms_data_changed = True  # Placeholder data is never saved/consistent with a live file.
        self._nms_loading = False  # Suppress false dirty events during controlled load transactions.
        self._nms_baseline = None  # A successful live load supplies a semantic model fingerprint.
        self._nms_tabs = (self.tab1, self.tab2, self.tab3, self.tab4)  # Include Teleport Endpoints.
        self.file_changed_indicator = QWidget(self)  # Keep this separate from the background LED.
        self.file_changed_indicator.setFixedSize(10, 10)  # Match the other small indicators.
        self.file_changed_label = QLabel(self)  # Show source slot/file and consistency in plain text.
        self.model.modelChanged.connect(self._nms_model_changed)  # Observe edits through data views.
        for tab in self._nms_tabs:  # Observe raw unsynced text and direct tree mutations too.
            tab.text_edit.textChanged.connect(self._nms_editor_changed)  # Raw text may be invalid JSON.
            tab.tree_widget.itemChanged.connect(self._nms_editor_changed)  # Any real item edit is dirty.
        self._nms_observer = QTimer(self)  # Existing tab operations sometimes suppress model signals.
        self._nms_observer.timeout.connect(self._observe_nms_model)  # Catch those silent in-place mutations.
        self._nms_observer.start(1000)  # Check consistent data once per second; dirty data needs no hashing.
        self._update_nms_led()  # Show the initial no-live-source state.
        self._nms_trace("init_state", has_source=False, changed=True)  # Reveal invisible startup state.

    # _nms_trace: Send metadata-only events to stdout using the shared module switch.
    def _nms_trace(self, event, **fields):
        slot_ops.trace("NmsLoadController", event, **fields)  # The helper owns gating and prefixing.

    # _nms_error: Always report errors regardless of the debug switch, then inform Bill.
    def _nms_error(self, action, exc):
        print(f"{self.DEBUG_PREFIX} {action}: ERROR {exc}", flush=True)  # Errors are never gated.
        QMessageBox.warning(self, action, str(exc))  # Retain the existing app data on failed requests.

    # _nms_fingerprint: Compute a stable semantic checksum without exposing the JSON payload.
    def _nms_fingerprint(self):
        text = json.dumps(self.model.get_data(), sort_keys=True, separators=(",", ":"))  # Ignore formatting.
        return hashlib.sha256(text.encode("utf-8")).hexdigest()  # Compare data, not object identity.

    # _nms_editor_changed: Mark even unsynchronized edits as changed until explicitly loaded/saved.
    def _nms_editor_changed(self, *unused):
        if not self._nms_loading:  # Programmatic population must not invalidate a fresh live load.
            self._mark_nms_changed("editor_changed")  # Conservative even if only whitespace changed.

    # _nms_model_changed: Detect model changes not surfaced through an editor's signals.
    def _nms_model_changed(self, unused=None):
        if not self._nms_loading and self._nms_fingerprint() != self._nms_baseline:  # Catch data operations.
            self._mark_nms_changed("model_changed")  # JSON copy saves do not clear this live state.

    # _observe_nms_model: Detect existing operations that change shared data while Qt signals are blocked.
    def _observe_nms_model(self):
        if not self._nms_loading and self.nms_source is not None and not self.nms_data_changed:  # Only consistent live state needs polling.
            if self._nms_fingerprint() != self._nms_baseline:  # Compare semantic data rather than widget activity.
                self._mark_nms_changed("silent_model_mutation")  # Backup also performs this check synchronously.

    # _mark_nms_changed: Set the live-file state red and log transitions rather than every keystroke.
    def _mark_nms_changed(self, reason):
        was_changed = self.nms_data_changed  # Avoid enormous duplicate traces during typing.
        self.nms_data_changed = True  # Unsaved edits and ZIP divergence cannot permit Backup.
        self._update_nms_led()  # Keep the visible status and authoritative flag aligned.
        if not was_changed:  # Only a real transition needs a debug event.
            self._nms_trace("dirty_transition", reason=reason, changed=True)  # Record why green became red.

    # _update_nms_led: Present live consistency without altering the background-processing indicator.
    def _update_nms_led(self):
        saved = self.nms_source is not None and not self.nms_data_changed  # No source is never green.
        color = GREEN_LED_COLOR if saved else "red"  # Use the app's existing green palette.
        self.file_changed_indicator.setStyleSheet(f"background-color: {color}; border-radius: 4px;")  # LED.
        status = "saved/consistent" if saved else "changed / not saved live"  # Explain the meaning.
        identity = "no live source" if self.nms_source is None else f"slot {self.nms_source['slot']} / {self.nms_source['file_name']}"  # Target.
        self.file_changed_label.setText(f"Live file: {status} ({identity})")  # Do not silently hide targeting.
        self.file_changed_indicator.setToolTip("Green: consistent with loaded live file. Red: unsaved, ZIP, or no live source.")  # Distinct status.

    # confirm_nms_replacement: Warn, but never block solely because the current data is unsaved.
    def confirm_nms_replacement(self, kind):
        text = f"{kind} will OVERWRITE all currently loaded data, including unsaved edits.\nContinue?\n(No live save files will be written.)"  # Scope warning.
        reply = QMessageBox.warning(self, kind, text, QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)  # Explicit consent.
        accepted = reply == QMessageBox.Ok  # A close/cancel declines the request.
        self._nms_trace("replacement_confirmation", kind=kind, accepted=accepted, changed=self.nms_data_changed)  # State before commit.
        return accepted  # No source/LED/model mutation occurs here.

    # _confirm_manual_tie: Present row 35's exact words; OK loads Manual and Cancel abandons.
    def _confirm_manual_tie(self, message):
        reply = QMessageBox.warning(self, "Equal save timestamps", message, QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)  # Exact body.
        accepted = reply == QMessageBox.Ok  # Never silently fall back to Auto.
        self._nms_trace("tie_confirmation", manual_accepted=accepted)  # Expose the otherwise hidden branch.
        return accepted  # Selection helper handles the decision identically for live and ZIP.

    # load_nms_live_slot: Read and decode the pair before committing the selected file into the app.
    def load_nms_live_slot(self, folder, slot, on_load_confirmed=None):
        if self._nms_loading:  # Existing render helpers process Qt events; prevent a nested load/backup transaction.
            self._nms_trace("request_ignored_during_load", action="load_nms_live_slot")  # Keep the current commit isolated.
            return False  # No second warning, picker, read or write.
        if not self.confirm_nms_replacement("Load Slot"):  # Cancellation is a complete no-op.
            return False  # Leave source, model and LED untouched.
        try:  # Any file/metadata/codec error must retain the previous app state.
            snapshot = slot_ops.read_live_slot(folder, slot)  # Read-only, bounded four-file snapshot.
            return self._load_nms_snapshot(snapshot, folder, "live", on_load_confirmed=on_load_confirmed)  # Close the picker after all confirmations, before decoding.
        except Exception as exc:  # Report unsupported/corrupt/incomplete saves without crashing.
            self._nms_error("Load Slot failed", exc)  # Errors always reach stdout.
            return False  # No successful load was committed.

    # restore_nms_slot: Choose a ZIP, warn, then decode entirely in memory with the current live-folder context.
    def restore_nms_slot(self, live_folder):
        if self._nms_loading:  # Existing render helpers process Qt events; prevent a nested load/backup transaction.
            self._nms_trace("request_ignored_during_load", action="restore_nms_slot")  # Keep the current commit isolated.
            return False  # No second warning, picker, read or write.
        path, unused = QFileDialog.getOpenFileName(self, "Restore Slot", self._nms_backup_directory(), "Slot backups (*.zip)")  # Same start directory.
        if not path:  # File picker cancellation leaves every state intact.
            self._nms_trace("restore_picker_cancel")  # Record a user cancellation without treating it as error.
            return False  # No reads/extraction/writes are needed.
        if not self.confirm_nms_replacement("Restore Slot"):  # Unsaved data is allowed after warning.
            return False  # Do not touch source or LED on decline.
        try:  # ZIP integrity and filename validation happen before UI commit.
            snapshot = slot_ops.read_zip_slot(path)  # No extraction and no automatic safety backup.
            return self._load_nms_snapshot(snapshot, live_folder, "zip", path)  # Slot comes from internal names.
        except Exception as exc:  # Reject mixed slots, duplicates, malformed metadata and corrupt JSON.
            self._nms_error("Restore Slot failed", exc)  # Explain why the old data remains.
            return False  # Signal the popup to stay open.

    # _load_nms_snapshot: Stage full-save identity and decoded BaseContext independently of live state.
    def _load_nms_snapshot(self, snapshot, live_folder, kind, archive_path=None, on_load_confirmed=None):
        if not live_folder or not os.path.isdir(live_folder):  # Never invent a future write target.
            raise ValueError("Pick a valid live save folder before loading or restoring a slot.")  # Recovery instructions.
        record = slot_ops.select_slot_file(snapshot, self._confirm_manual_tie)  # Only metadata timestamps count.
        if record is None:  # Equal-time Cancel is a no-op, not an Auto fallback.
            self._nms_trace("load_abandoned", kind=kind, slot=snapshot["slot"])  # Confirm unchanged state.
            return False  # No decode or commit.
        if on_load_confirmed is not None:  # Only OK, including any required tie confirmation, reaches this point.
            on_load_confirmed()  # Dismiss the selection dialog before slow decoding/tab population.
            self._nms_trace("selection_dialog_closed", kind=kind, slot=snapshot["slot"])  # Observe dismissal timing.
        was_enabled = self.isEnabled()  # Preserve the main window's current enabled state.
        self.setEnabled(False)  # Closing the modal picker must not allow edits during population.
        try:  # Keep loading isolated while existing tree helpers process Qt events.
            source = slot_ops.decode_record(record, live_folder)  # Retain the entire tree and original bytes.
            source["source_kind"] = kind  # ZIP is dirty even when its bytes happen to match live.
            source["archive_path"] = archive_path  # Diagnostic origin only; never derives the target slot.
            self._commit_nms_source(source)  # Transactional GUI/model replacement.
        finally:  # Errors must never leave the main window disabled.
            self.setEnabled(was_enabled)  # Resume interaction only after commit or rollback.
        self._nms_trace("load_complete", kind=kind, slot=source["slot"], file=source["file_name"], meta=source["meta_name"], target=source["data_path"], changed=self.nms_data_changed, model_hash=self._nms_baseline)  # Inspect under the hood.
        return True  # Allow the Open/Restore dialog to dismiss on success.

    # _capture_nms_editors: Capture raw text and tree-sync status for rollback, including unsynced edits.
    def _capture_nms_editors(self):
        return [(tab.text_edit.toPlainText(), tab.tree_synced) for tab in self._nms_tabs]  # Raw input may be invalid JSON.

    # _refresh_nms_tabs: Populate all views explicitly so rendering failures propagate into rollback.
    def _refresh_nms_tabs(self):
        for tab in self._nms_tabs:  # All four tabs share the same BaseContext model.
            tab.update_text_widget_from_model()  # Emit no editor signals during a load transaction.
            tab.update_tree_from_model()  # A schema error must abort rather than falsely mark green.
            tab.tree_widget.expand_tree_to_level(1)  # Follow the app's normal presentation.

    # _commit_nms_source: Preserve old data/targets until every tab renders the staged BaseContext.
    def _commit_nms_source(self, source):
        previous = copy.deepcopy(self.model.get_data())  # Model rollback must survive mutable shared references.
        editors = self._capture_nms_editors()  # Preserve unsynced user input too.
        blocked = [(widget, widget.blockSignals(True)) for tab in self._nms_tabs for widget in (tab.text_edit, tab.tree_widget)]  # Isolate population.
        model_blocked = self.model.blockSignals(True)  # Do not invoke slots that swallow render failures.
        self._nms_loading = True  # Also suppress any incidental row-40 dirty callbacks.
        try:  # The model and all tab views commit as one operation.
            self.model.set_data(copy.deepcopy(source["base_context"]))  # Keep the full save tree independent.
            self._refresh_nms_tabs()  # Explicit calls expose exceptions to this transaction.
            baseline = self._nms_fingerprint()  # Only compute baseline after successful rendering.
        except Exception:  # Restore model and raw editor input, never change source/LED on failure.
            self.model.set_data(previous)  # Reinstate original BaseContext.
            self._refresh_nms_tabs()  # Rebuild trees from the old model.
            for tab, (text, synced) in zip(self._nms_tabs, editors):  # Put unsynced text back exactly.
                tab.text_edit.setPlainText(text)  # Keep invalid/pending edits rather than losing them.
                tab.update_tree_synced_indicator(synced)  # Restore each original tree-sync LED.
            self._nms_trace("load_rollback", source_unchanged=True, changed=self.nms_data_changed)  # Observable rollback.
            raise  # Let the caller show the failure popup.
        finally:  # Restore Qt signal state even after rendering/rollback errors.
            self.model.blockSignals(model_blocked)  # Respect any earlier caller signal suppression.
            for widget, was_blocked in blocked:  # Do not blindly enable previously blocked widgets.
                widget.blockSignals(was_blocked)  # End transaction isolation.
            self._nms_loading = False  # Resume editing observations.
        self.nms_source = source  # Commit target identity only after successful model/UI rendering.
        self._nms_baseline = baseline  # Retain the semantic data fingerprint for consistency checks.
        self.nms_data_changed = source["source_kind"] != "live"  # ZIP Restore always marks data changed.
        self._update_nms_led()  # Live starts green; ZIP starts red.

    # confirm_legacy_json_write: Keep old JSON-copy saving separate from future live-file saving.
    def confirm_legacy_json_write(self):
        if self.nms_source is not None:  # Loaded NMS sources must not be exported over a live .hg as plaintext.
            QMessageBox.warning(self, "Live save not implemented", "Saving this loaded NMS context back to disk is deferred to row 50. File Save/Save As are legacy JSON operations, not live NMS saves.")  # Explicit boundary.
            self._nms_trace("legacy_save_blocked", slot=self.nms_source["slot"])  # Never falsely clear the LED.
            return False  # No JSON or live data write.
        reply = QMessageBox.warning(self, "Confirm JSON disk write", "About to write a JSON file and update its file-path preference. This is NOT an NMS live save. Continue?", QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)  # Consent before existing save dialog.
        return reply == QMessageBox.Ok  # Retain legacy placeholder/clipboard behavior after warning.

    # _nms_backup_directory: Use the same persistent directory every time without creating it here.
    def _nms_backup_directory(self):
        return os.path.join(os.environ.get("APPDATA", ""), "BBB NMS Save File Manipulator")  # No picker-time writes.

    # _checked_backup_snapshot: Gate Backup on current app/source consistency, not the popup's slot selection.
    def _checked_backup_snapshot(self):
        if self.nms_source is None or self.nms_data_changed:  # Startup, ZIP and raw unsaved text all fail.
            raise ValueError("Current app data must first be saved to its live save file before Backup Slot. Live saving is deferred to row 50.")  # Clear failure reason.
        if self._nms_fingerprint() != self._nms_baseline:  # Catch in-place mutations without signals.
            self._mark_nms_changed("backup_model_mismatch")  # Align authoritative state and visible LED.
            raise ValueError("Current app data has unsaved changes; save it live before backing up.")  # No ZIP creation.
        source = self.nms_source  # The active app slot is authoritative, not a browsing selection.
        snapshot = slot_ops.read_live_slot(source["live_folder"], source["slot"])  # Fresh read-only bytes.
        record = next(item for item in snapshot["files"] if item["file_name"] == source["file_name"])  # Same loaded file, no extra selection rule.
        hashes = (hashlib.sha256(record["data_bytes"]).hexdigest(), hashlib.sha256(record["meta_bytes"]).hexdigest())  # Detect game/external changes.
        if hashes != (source["data_hash"], source["meta_hash"]):  # A stale app cannot be called consistent.
            self._mark_nms_changed("live_source_changed")  # Require reload rather than archive unexpected data.
            raise ValueError("The loaded live file changed outside the app. Reload it before backing up.")  # No active-at-backup guarantee imposed.
        self._nms_trace("backup_gate_pass", slot=source["slot"], file=source["file_name"], model_hash=self._nms_baseline)  # Inspect consistent state.
        return snapshot  # Backup preserves these four original files, without re-encoding.

    # backup_nms_slot: Ask for a filename and a separate disk-write warning before any ZIP/directory creation.
    def backup_nms_slot(self):
        if self._nms_loading:  # Existing render helpers process Qt events; prevent a nested load/backup transaction.
            self._nms_trace("request_ignored_during_load", action="backup_nms_slot")  # Keep the current commit isolated.
            return False  # No second warning, picker, read or write.
        try:  # Every failure produces an explanation and no successful-backup report.
            snapshot = self._checked_backup_snapshot()  # Fail before opening Save As if unsaved.
            suggested = os.path.join(self._nms_backup_directory(), slot_ops.backup_name(snapshot))  # Required initial directory/name.
            path, unused = QFileDialog.getSaveFileName(self, "Backup Slot", suggested, "Slot backups (*.zip)", options=QFileDialog.DontConfirmOverwrite)  # Separate warning below.
            if not path:  # Selecting a path is not disk-write consent.
                self._nms_trace("backup_picker_cancel")  # No output file or mkdir occurs.
                return False  # Complete no-op.
            path = os.path.abspath(path if path.lower().endswith(".zip") else path + ".zip")  # Preserve explicit ZIP extension.
            overwrite = os.path.exists(path)  # Consent must mention replacing an existing ZIP.
            action = "OVERWRITE the existing ZIP" if overwrite else "CREATE a backup ZIP"  # Plain-language effect.
            message = f"About to {action}:\n{path}\nAny missing destination directories will be created.\nNo live saves will be written. Continue?"  # Explicit disk warning.
            reply = QMessageBox.warning(self, "Confirm backup disk write", message, QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)  # Separate from Save As.
            self._nms_trace("backup_write_confirmation", accepted=reply == QMessageBox.Ok, path=path, overwrite=overwrite)  # Audit consent.
            if reply != QMessageBox.Ok:  # Decline cannot cause mkdir, temporary output or ZIP writes.
                return False  # Preserve app data and source.
            snapshot = self._checked_backup_snapshot()  # Recheck after dialogs so unsaved/external changes fail.
            result = slot_ops.write_backup(path, snapshot, confirmed=True, overwrite=overwrite)  # Helper verifies exact members and bytes.
            QMessageBox.information(self, "Slot backed up", f"Backup complete:\n{result}")  # Required full output path.
            return True  # A backup does not clear/change any dirty state.
        except Exception as exc:  # Never silently suppress a failed gate or failed filesystem write.
            self._nms_error("Backup Slot failed", exc)  # Always visible and logged.
            self._nms_trace("backup_failed", reason=str(exc), changed=self.nms_data_changed)  # Under-the-hood context.
            return False  # No claim that an archive was created successfully.
