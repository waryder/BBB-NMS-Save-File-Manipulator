# File: StarshipDeleteController.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\StarshipDeleteController.py
# Purpose: Safely route whole-starship Delete Node requests to one memory-only model transaction.
import copy  # Preserve original model/context throughout modal confirmation and rollback.
from PyQt5.QtWidgets import QDialog, QMessageBox  # Reuse the application's confirmation and OK-only notice toolkit.
from JsonTextNavigation import QT_DATA_JSON_LOCATION, same_json  # Use verified structural identities, never decorated labels.
from StarshipDelete import LAST_SHIP_NOTICE, LastShipDeletionError, plan_starship_deletions  # Shared pure deletion policy.


# selected_ship_indices: Accept complete ownership nodes, coalescing their selected descendants without guessing indices.
def selected_ship_indices(tree, ships):
    navigation = tree.json_navigation  # A completed structural capture is invalidated by every tree mutation.
    if not navigation.valid or not same_json(navigation.snapshot, ships):  # Reject stale trees after model/text changes.
        raise ValueError("The starship tree is out of date; sync/rebuild it before deleting.")  # Nothing is changed.
    paths = []  # Validate every selected node before choosing any target.
    for item in tree.right_button_selected_nodes:  # Preserve the current right-click/drag multi-selection behavior.
        if item.treeWidget() is not tree:  # Detached/foreign nodes cannot identify a current ownership position.
            raise ValueError("A selected starship node no longer belongs to this tree.")  # Atomic refusal.
        location = item.data(0, QT_DATA_JSON_LOCATION)  # Metadata records a typed root-relative JSON path.
        path = location.get("path") if isinstance(location, dict) else None  # Do not parse visible names or line counts.
        if not isinstance(path, list) or not path or type(path[0]) is not int or not 0 <= path[0] < len(ships):  # Root/unknown paths.
            raise ValueError("Select individual complete starship-slot nodes, not the ownership-list root.")  # Prevent array removal.
        paths.append(path)  # Whole ship nodes have exactly one integer path segment.
    indices = sorted({path[0] for path in paths if len(path) == 1})  # Dedupe repeated selected descendants.
    if any(path[0] not in indices for path in paths):  # A selected child alone must not imply deleting its entire ship.
        raise ValueError("Select complete starship-slot nodes; nested-node deletion is not supported by safe ship deletion.")  # No surprise loss.
    return indices  # An empty selection becomes a no-op.


# _checked_context: Refuse pending text edits before publishing any change that would refresh shared views.
def _checked_context(window):
    if any(not tab.tree_synced for tab in window._nms_tabs):  # A different tab may hold unsynchronized user work.
        raise ValueError("Use Sync to Node View in each changed tab before deleting a starship.")  # No implicit synchronization.
    context = window.model.get_data()  # The selected editable Main/Expedition branch, not the full retained codec tree.
    if not isinstance(context, dict) or not isinstance(context.get("PlayerStateData"), dict):  # Refuse unloaded/placeholder data.
        raise ValueError("No valid starship save context is loaded.")  # Leave source identity and editors untouched.
    return copy.deepcopy(context)  # Independent snapshot supports stale-selection checks and transaction rollback.


# _restore_editors: Restore exact synchronized raw formatting and sync status after a failed publication.
def _restore_editors(window, editors):
    for tab, (text, synced) in zip(window._nms_tabs, editors):  # All widgets remain signal-blocked during rollback.
        tab.text_edit.setPlainText(text)  # Do not lose the user's synchronized formatting.
        tab.update_tree_synced_indicator(synced)  # Restore both state and LED through the real tab's required boolean argument.


class StarshipDeletionTransaction:  # Own only model publication, view rollback and temporary UI/signal guards.
    # __init__: Capture the exact pre-publication editor and guard state without changing any widget.
    def __init__(self, window, original):
        self.window, self.original = window, original  # The source/baseline identity stays owned by the existing main window.
        self.editors = window._capture_nms_editors()  # Preserve synchronized raw formatting for failure recovery.
        self.enabled, self.loading, self.dirty = window.isEnabled(), window._nms_loading, window.nms_data_changed  # Prior flags.
        self.widgets = [window.model] + [widget for tab in window._nms_tabs for widget in (tab.text_edit, tab.tree_widget)]  # Shared views.
        self.blocked = []  # Track only signal guards this transaction actually acquired.

    # __enter__: Acquire temporary signal/loading/enabled guards, restoring even a partial acquisition on failure.
    def __enter__(self):
        try:  # Record each previous signal state immediately after acquiring it.
            for widget in self.widgets:  # Block recursive callbacks on the shared model and all four tabs.
                self.blocked.append((widget, widget.blockSignals(True)))  # Preserve another caller's pre-existing blocked state.
            self.window._nms_loading = True  # Timers/load/upgrade actions must not observe an incomplete refresh.
            self.window.setEnabled(False)  # Prevent interaction while candidate or rollback views are rebuilding.
        except Exception:  # Do not strand previously acquired guards if another widget refuses acquisition.
            self._restore_guards()  # Release only the guards acquired by this object.
            raise  # The request owns reporting the actual failure.
        return self  # A with-block owns the publication lifetime.

    # _restore_guards: Return loading, interaction and signal states to their exact prior values.
    def _restore_guards(self):
        self.window._nms_loading = self.loading  # Restore the guard owner, not an assumed false default.
        try:  # Signal restoration must still run if re-enabling a window fails.
            self.window.setEnabled(self.enabled)  # Preserve a previously disabled window.
        finally:
            for widget, previous in reversed(self.blocked):  # Unwind in reverse acquisition order.
                widget.blockSignals(previous)  # Do not emit a generic shortened-array model update.
            self.blocked.clear()  # A released transaction must not release somebody else's later guards.

    # __exit__: Always release temporary guards without swallowing publication or rollback errors.
    def __exit__(self, error_type, error, traceback):
        self._restore_guards()  # Success and failure share the same guard cleanup.
        return False  # The outer request reports exceptions honestly.

    # _commit: Publish one whole candidate and explicitly refresh every view before marking it unsaved.
    def _commit(self, candidate):
        self.window.model.set_data(candidate)  # No live-save API is called.
        self.window._refresh_nms_tabs()  # Direct calls propagate rendering errors rather than hiding them inside Qt signals.
        self.window._mark_nms_changed("starship_delete")  # The retained source and successful-save baseline remain unchanged.

    # _rollback: Restore the original model, exact raw editors and previous dirty state after a failed commit.
    def _rollback(self):
        self.window.model.set_data(self.original)  # Restore every ownership/appearance/build/reference change together.
        try:  # Restore semantic trees before putting exact prior raw formatting back.
            self.window._refresh_nms_tabs()  # Rebuild from the original active context.
        finally:
            try:  # Dirty-state recovery must still happen if editor restoration fails.
                _restore_editors(self.window, self.editors)  # Use the real tab method's explicit boolean signature.
            finally:
                self.window.nms_data_changed = self.dirty  # A failed delete must not count as a successful edit.
                self.window._update_nms_led()  # Restore the original saved/unsaved display.

    # publish: Keep commit, rollback and guard lifetimes visible as separate purpose-specific methods.
    def publish(self, candidate):
        with self:  # Restore all temporary guards on every exit.
            try:
                self._commit(candidate)  # One complete in-memory publication.
            except Exception:  # Rendering/schema/status failures must not leave a partial deletion.
                self._rollback()  # Restore original data and presentation before reporting failure.
                raise  # No fabricated success or silent fallback to generic tree deletion.


# _publish: Preserve the controller's existing publication entry point while delegating transaction ownership.
def _publish(window, original, candidate):
    StarshipDeletionTransaction(window, original).publish(candidate)  # Saving remains a separate user action.


class StarshipDeleteRequest:  # Own one menu request's selection, confirmation, stale-data checks and policy/error notices.
    # __init__: Retain only the current tree, its shared window and the existing confirmation dialog factory.
    def __init__(self, tree, confirmation_class):
        self.tree, self.confirmation_class = tree, confirmation_class  # No UI or model mutation during construction.
        self.window = tree.parent.main_window  # All tabs edit this one selected whole-context branch.

    # _is_busy: Refuse overlapping load/save, upgrade or nested deletion requests.
    def _is_busy(self):
        return (self.window._nms_loading or getattr(self.window, "_starship_upgrade_running", False)
                or getattr(self.window, "_starship_delete_running", False))  # Do not acquire a guard owned by another request.

    # _prepare: Snapshot current context/source and stage the combined complete deletion without publication.
    def _prepare(self):
        self.context = _checked_context(self.window)  # Reject pending unsynchronized user work first.
        self.source = self.window.nms_source  # Source object identity also guards an identical-data load during confirmation.
        indices = selected_ship_indices(self.tree, self.context["PlayerStateData"].get("ShipOwnership"))  # Exact typed whole-slot paths.
        self.candidate, self.deleted = plan_starship_deletions(self.context, indices)  # Last-ship protection runs before confirmation.

    # _confirmed: Preserve existing confirmation while treating empty-slot/empty selections as true no-ops.
    def _confirmed(self):
        if not self.deleted:  # Do not inflate counts with empty positions or selected descendants.
            return False  # No confirmation, dirty transition or publication.
        return self.confirmation_class(len(self.deleted)).exec_() == QDialog.Accepted  # Cancel changes nothing.

    # _validate_selection: Refuse stale modal requests without overwriting a newer loaded context or raw edit.
    def _validate_selection(self):
        if self.window.nms_source is not self.source or not same_json(self.window.model.get_data(), self.context):  # Identity plus content.
            raise ValueError("Loaded data changed during confirmation; review it and try again.")  # Preserve the newer context.
        _checked_context(self.window)  # Another tab's pending raw text must also remain intact.
        if not self.tree.json_navigation.valid:  # Tree-only edits/reorders invalidate captured ownership positions.
            raise ValueError("The starship tree changed during confirmation; rebuild it and try again.")  # No guessing.

    # _execute: Sequence preparation, confirmation, validation and publication without mixing their responsibilities.
    def _execute(self):
        self._prepare()  # No model mutation or live-save read.
        if not self._confirmed():  # Empty selections and Cancel are complete no-ops.
            return False  # Preserve all prior model/editor/dirty state.
        self._validate_selection()  # Check again after processing the modal dialog.
        try:  # A refresh destroys the old QTreeWidgetItems on success or rollback.
            _publish(self.window, self.context, self.candidate)  # The transaction alone owns publication and recovery.
        finally:
            self.tree.right_button_selected_nodes.clear()  # Do not retain pointers to destroyed items after a rebuild.
        return True  # Changes remain unsaved until File > Save.

    # run: Own the request guard and exact user-facing policy/failure notices, not the cleanup algorithms.
    def run(self):
        if self._is_busy():  # Ignore nested requests without altering another operation's guard.
            return False  # No dialog, planning or mutation during an incompatible operation.
        self.window._starship_delete_running = True  # This request now owns the guard.
        try:
            return self._execute()  # Each request stage remains independently traceable by method/line.
        except LastShipDeletionError:  # Bill's policy refusal has an exact OK-only informational notice.
            QMessageBox.information(self.window, "Cannot delete last starship", LAST_SHIP_NOTICE, QMessageBox.Ok, QMessageBox.Ok)  # Exact approved text/buttons.
            return False  # Never offer an override or partially delete a combined request.
        except Exception as error:  # Preflight/transaction failures must not reach unsafe generic removal.
            QMessageBox.warning(self.window, "Starship deletion failed", str(error))  # Report the real failure.
            return False  # No claim that rolled-back changes succeeded.
        finally:
            self.window._starship_delete_running = False  # Release the guard owned by this request.


# run_starship_delete: Preserve the existing menu integration while delegating request lifecycle to its object.
def run_starship_delete(tree, confirmation_class):
    return StarshipDeleteRequest(tree, confirmation_class).run()  # Single and multi-node menu actions share this entry point.
