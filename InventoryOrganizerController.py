# File: InventoryOrganizerController.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\InventoryOrganizerController.py
# Purpose: Qt-independent preview identity checks and atomic memory-only inventory publication.
import copy  # Preserve exact pre-publication context and candidate ownership.
from InventoryOrganizer import InventoryPlanner, same_context  # Pure planner; no GUI or save dependencies.

# checked_context: Refuse busy operations and pending raw JSON before any shared-view refresh.
def checked_context(window):
    busy = ('_nms_loading', '_starship_upgrade_running', '_starship_delete_running')
    if any(getattr(window, name, False) for name in busy):
        raise ValueError('Another save-data operation is running; try again when it finishes.')
    if any(not tab.tree_synced for tab in window._nms_tabs):
        raise ValueError('Use Sync to Node View in every changed tab before organizing inventories.')
    context = window.model.get_data()
    if not isinstance(context, dict) or not isinstance(context.get('PlayerStateData'), dict):
        raise ValueError('No valid editable save context is loaded.')
    return context  # Never synchronize implicitly or switch Main/Expedition contexts.

class InventoryTransaction:
    # __init__: Capture exact formatting, dirty and guard state before publication.
    def __init__(self, window, original):
        self.window, self.original = window, original
        self.editors = window._capture_nms_editors()
        self.enabled, self.loading, self.dirty = window.isEnabled(), window._nms_loading, window.nms_data_changed
        self.widgets = [window.model] + [widget for tab in window._nms_tabs
                                         for widget in (tab.text_edit, tab.tree_widget)]
        self.blocked = []  # Track only guards this transaction actually acquired.

    # _acquire: Protect complete-context publication from callbacks and user interaction.
    def _acquire(self):
        for widget in self.widgets:
            self.blocked.append((widget, widget.blockSignals(True)))
        self.window._nms_loading = True
        self.window.setEnabled(False)

    # _release: Restore prior loading, enabled and signal states, not assumed defaults.
    def _release(self):
        self.window._nms_loading = self.loading
        try:
            self.window.setEnabled(self.enabled)
        finally:
            for widget, previous in reversed(self.blocked):
                widget.blockSignals(previous)
            self.blocked.clear()

    # _commit: Replace the entire active context and render all four views before dirtying.
    def _commit(self, candidate):
        self.window.model.set_data(candidate)  # Memory-only; DataViews.set_json is deliberately not used.
        self.window._refresh_nms_tabs()
        self.window._mark_nms_changed('inventory_organizer')  # File Save is a separate existing action.

    # _restore_editors: Recover synchronized user formatting and each tab's sync indicator.
    def _restore_editors(self):
        for tab, (text, synced) in zip(self.window._nms_tabs, self.editors):
            tab.text_edit.setPlainText(text)
            tab.update_tree_synced_indicator(synced)

    # _rollback: Recover the complete data, semantic trees, exact editors and dirty state.
    def _rollback(self):
        self.window.model.set_data(self.original)
        try:
            self.window._refresh_nms_tabs()
        finally:
            try:
                self._restore_editors()
            finally:
                self.window.nms_data_changed = self.dirty
                self.window._update_nms_led()

    # publish: Own commit/rollback and always unwind partial or complete guard acquisition.
    def publish(self, candidate):
        try:
            self._acquire()
            try:
                self._commit(candidate)
            except Exception:
                self._rollback()
                raise  # Never report a rolled-back operation as successful.
        finally:
            self._release()

# source_identity: Snapshot routing metadata only, never deepcopy/serialize the retained codec or full save tree.
def source_identity(source):
    keys = ('source_kind', 'context_key', 'slot', 'file_name', 'meta_name', 'live_folder',
            'data_path', 'meta_path', 'data_hash', 'meta_hash')
    return copy.deepcopy({key: source.get(key) for key in keys}) if isinstance(source, dict) else None

class InventoryOrganizerController:
    # __init__: Retain the existing window interface without importing or constructing Qt.
    def __init__(self, window):
        self.window, self._plan = window, None

    # invalidate: Consume outdated choices or cancel a preview without touching application state.
    def invalidate(self):
        self._plan = None

    # preview: Capture exact active model/source identities and produce a private deep-copy candidate.
    def preview(self, sources, routes, overflow=False, expand=False):
        self.invalidate()  # A failed replacement preview must not leave an old Apply available.
        current = checked_context(self.window)
        self.context_identity = current
        self.source = self.window.nms_source
        self.source_snapshot = source_identity(self.source)  # Detect in-place target/context metadata changes too.
        self.original = copy.deepcopy(current)
        self._plan = InventoryPlanner(self.original).plan(sources, routes, overflow, expand)
        return copy.deepcopy(self._plan)  # UI code cannot mutate the private exact preview candidate.

    # _validate: Refuse stale models, source replacements/in-place context changes, or pending text.
    def _validate(self):
        current = checked_context(self.window)
        source = self.window.nms_source
        if source is not self.source or source_identity(source) != self.source_snapshot:
            raise ValueError('The loaded save source changed; preview again.')
        if current is not self.context_identity or not same_context(current, self.original):
            raise ValueError('The loaded data changed; preview again before applying.')

    # apply: Publish only the exact retained preview, never re-plan behind the review screen.
    def apply(self):
        if self._plan is None:
            raise ValueError('Preview the current choices before applying.')
        self._validate()
        plan, self._plan = self._plan, None  # Every publication attempt consumes its reviewed preview.
        if not plan.changed:
            return False  # No-op/cancel cannot mark data dirty or reformat editors.
        InventoryTransaction(self.window, self.original).publish(copy.deepcopy(plan.candidate))
        return True
