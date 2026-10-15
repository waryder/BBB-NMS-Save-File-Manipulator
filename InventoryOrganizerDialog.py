# File: InventoryOrganizerDialog.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\InventoryOrganizerDialog.py
# Purpose: Separate single-screen organizer with explicit preview and memory-only Apply.
from imports import *  # Match the application's dialog conventions.

from PyQt5.QtCore import Qt, QEventLoop
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
                             QPushButton, QLabel, QListWidget, QListWidgetItem, QComboBox,
                             QCheckBox, QTextBrowser, QMessageBox, QAbstractItemView)
from InventoryOrganizer import CATEGORIES, CHESTS, inventory_roster
from InventoryOrganizerReview import CATEGORY_NAMES, review_html
from InventoryOrganizerPreferences import organizer_settings, settings_payload
from NmsLoadController import NmsLoadingDialog
from InventoryOrganizerController import InventoryOrganizerController, checked_context


OVERFLOW_LABEL = "Overflow: if destination is full, overflow to other 'Container' type storages."
OVERFLOW_HELP = 'Unassigned containers only, working backward from Container 10. Otherwise items stay where they are.'
EXPAND_LABEL = 'Expand all Destination storages to 120 cells.'

class InventoryOrganizerDialog(QDialog):
    # __init__: Stage a separate candidate without touching the legacy Inventory Sorter dialog.
    def __init__(self, parent):
        super().__init__(parent)
        self.window = parent.main_window
        self.controller = InventoryOrganizerController(self.window)
        self.entries = inventory_roster(checked_context(self.window))
        self.labels = {entry.path: entry.label for entry in self.entries}
        self.setWindowTitle('Inventory Organizer')
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.resize(1120, 850)
        self._review_running = False
        self._settings = organizer_settings(self.window.ini_file_manager.get_inventory_organizer_settings())
        self._build()
        self._restore_settings()  # Restore before connecting signals or invalidating any review.
        self._connect()
        self._invalidate()

    # _build: Keep sources and destinations side by side with review and actions below.
    def _build(self):
        layout = QVBoxLayout(self)
        note = QLabel('Gather whole Parts by game category. Review Moves proposes changes; Apply changes app data only. File Save remains separate.')
        note.setWordWrap(True)
        layout.addWidget(note)
        columns = QHBoxLayout()
        columns.addWidget(self._sources(), 1)
        columns.addWidget(self._destinations(), 1)
        layout.addLayout(columns, 3)
        layout.addWidget(self._options())
        layout.addWidget(QLabel('Review Summary'))
        self.review = QTextBrowser()
        self.review.setOpenExternalLinks(False)
        layout.addWidget(self.review, 2)
        layout.addLayout(self._actions())

    # _sources: List real loaded names and true paths with no mock capacity controls.
    def _sources(self):
        group = QGroupBox('Gather from these sources')
        layout = QVBoxLayout(group)
        tools = QHBoxLayout()
        for label, selection in (('Select all', 'all'), ('Mobile Storages', 'carried'),
                                 ('Stationary Storages', 'stationary'), ('Clear', 'clear')):
            button = QPushButton(label)
            button.clicked.connect(lambda checked=False, choice=selection: self._select_group(choice))
            tools.addWidget(button)
        layout.addLayout(tools)
        self.sources = QListWidget()
        self.sources.setSelectionMode(QAbstractItemView.NoSelection)
        for entry in self.entries:
            item = QListWidgetItem(entry.label, self.sources)
            item.setData(Qt.UserRole, entry.path)
            item.setToolTip(entry.label)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if entry.carried else Qt.Unchecked)
        layout.addWidget(self.sources)
        return group

    # _destinations: Offer one real inventory or leave-in-place for each of six game categories.
    def _destinations(self):
        group = QGroupBox('One destination per category')
        layout = QGridLayout(group)
        self.routes = {}
        for index, category in enumerate(CATEGORIES):
            label = QLabel(CATEGORY_NAMES[index])
            combo = QComboBox()
            combo.setMinimumContentsLength(25)
            combo.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
            combo.addItem('Leave where they are', None)
            for entry in self.entries:
                combo.addItem(entry.label, entry.path)
                combo.setItemData(combo.count() - 1, entry.label, Qt.ToolTipRole)
            default = next((i for i in range(combo.count()) if combo.itemData(i) == CHESTS[index]), 0)
            combo.setCurrentIndex(default)
            layout.addWidget(label, index, 0)
            layout.addWidget(combo, index, 1)
            self.routes[category] = combo
        return group

    # _options: Default overflow on only when no valid saved preference exists.
    def _options(self):
        group = QGroupBox('Optional')
        layout = QVBoxLayout(group)
        self.overflow = QCheckBox(OVERFLOW_LABEL)
        self.overflow.setChecked(True)
        helper = QLabel(OVERFLOW_HELP)
        helper.setWordWrap(True)
        self.expand = QCheckBox(EXPAND_LABEL)
        self.expand.setChecked(True)
        layout.addWidget(self.overflow)
        layout.addWidget(helper)
        layout.addWidget(self.expand)
        return group

    # _actions: Separate explicit Review Moves, Apply to app data, and cancel-safe Close.
    def _actions(self):
        layout = QHBoxLayout()
        layout.addStretch()
        self.preview_button = QPushButton('Review Moves')
        self.apply_button = QPushButton('Apply to app data')
        self.close_button = QPushButton('Close')
        for button in (self.preview_button, self.apply_button, self.close_button):
            button.setAutoDefault(False)
            layout.addWidget(button)
        return layout

    # _connect: Any changed choice invalidates the exact preview before Apply can be used.
    def _connect(self):
        self.sources.itemChanged.connect(self._choices_changed)
        for combo in self.routes.values():
            combo.currentIndexChanged.connect(self._choices_changed)
        self.overflow.toggled.connect(self._choices_changed)
        self.expand.toggled.connect(self._choices_changed)
        self.preview_button.clicked.connect(self._preview)
        self.apply_button.clicked.connect(self._apply)
        self.close_button.clicked.connect(self.reject)

    # _restore_settings: Reuse stable paths and leave unavailable targets safely unassigned.
    def _restore_settings(self):
        for index in range(self.sources.count()):
            item = self.sources.item(index)
            checked = self._settings['sources'].get(tuple(item.data(Qt.UserRole)))
            if checked is not None:
                item.setCheckState(Qt.Checked if checked else Qt.Unchecked)
        for category, combo in self.routes.items():
            if category in self._settings['routes']:
                target = self._settings['routes'][category]
                match = next((index for index in range(combo.count())
                              if combo.itemData(index) == target), 0)
                combo.setCurrentIndex(match)
        self._restored_routes = self._routing()  # Retain absent saved routes until deliberately changed.
        self.overflow.setChecked(self._settings['overflow'])
        self.expand.setChecked(self._settings['expand'])

    # _save_settings: Merge visible choices with stored identities missing from the current context.
    def _save_settings(self):
        for index in range(self.sources.count()):
            item = self.sources.item(index)
            self._settings['sources'][tuple(item.data(Qt.UserRole))] = item.checkState() == Qt.Checked
        for category, target in self._routing().items():
            if category not in self._settings['routes'] or target != self._restored_routes[category]:
                self._settings['routes'][category] = target
        self._restored_routes = self._routing()  # Track later reversions as deliberate changes too.
        self._settings.update(overflow=self.overflow.isChecked(), expand=self.expand.isChecked())
        try:
            self.window.ini_file_manager.store_inventory_organizer_settings(settings_payload(self._settings))
        except Exception as error:
            # Do not claim persistence or prevent closing/applying when preferences cannot be written.
            QMessageBox.warning(self, 'Inventory Organizer preferences', 'Settings could not be saved: ' + str(error))

    # _choices_changed: Invalidate immediately and persist even without Review Moves or Apply.
    def _choices_changed(self, *unused):
        self._invalidate()
        self._save_settings()

    # done: Persist Close, Escape, window-close and successful Apply without publishing a candidate.
    def done(self, result):
        if self._review_running:
            return  # Event processing cannot dismiss an in-progress organizer.
        self._save_settings()
        super().done(result)

    # _selected: Return true paths, not row indices in the filtered roster.
    def _selected(self):
        return [tuple(self.sources.item(index).data(Qt.UserRole)) for index in range(self.sources.count())
                if self.sources.item(index).checkState() == Qt.Checked]

    # _routing: Read exactly one destination per category; several categories may share one.
    def _routing(self):
        return {category: tuple(combo.currentData()) if combo.currentData() else None
                for category, combo in self.routes.items()}

    # _select_group: Apply source-only bulk selection without repeatedly regenerating the review.
    def _select_group(self, selection):
        old = self.sources.blockSignals(True)
        try:
            carried = {entry.path for entry in self.entries if entry.carried}
            for index in range(self.sources.count()):
                item = self.sources.item(index)
                path = tuple(item.data(Qt.UserRole))  # Match exact available source identities.
                checked = (selection == 'all' or (selection == 'carried' and path in carried)
                           or (selection == 'stationary' and path not in carried))
                item.setCheckState(Qt.Checked if checked else Qt.Unchecked)
        finally:
            self.sources.blockSignals(old)
        self._choices_changed()

    # _invalidate: Retain live transfer rows without counts and prevent applying an obsolete review.
    def _invalidate(self, *unused):
        self.controller.invalidate()
        self.apply_button.setEnabled(False)
        selected = self._selected()
        self.review.setHtml(review_html(self.window.model.get_data(), selected, self._routing(), self.labels))
        self.preview_button.setEnabled(bool(selected) or self.expand.isChecked())

    # _render: Add whole-record counts to the same plain-text route rows; never list individual items.
    def _render(self, plan):
        self.review.setHtml(review_html(self.controller.original, self._selected(),
                                            self._routing(), self.labels, plan))

    # _review_plan: Paint non-cancellable progress before synchronous snapshotting and planning.
    def _review_plan(self):
        enabled, window_enabled = self.isEnabled(), self.window.isEnabled()
        progress = None
        self._review_running = True  # Guard nested callbacks before processing any events.
        try:
            self.window.setEnabled(False)
            self.setEnabled(False)
            progress = NmsLoadingDialog('Reviewing inventory moves, please wait…', self)
            progress.setEnabled(True)  # Keep the modal child paintable while its parents are disabled.
            progress.show()
            progress.repaint()
            QApplication.processEvents(QEventLoop.ExcludeUserInputEvents)
            return self.controller.preview(self._selected(), self._routing(),
                                           self.overflow.isChecked(), self.expand.isChecked())
        finally:
            try:
                if progress is not None:
                    progress.accept()  # User close is suppressed; only completion owns dismissal.
            finally:
                self.window.setEnabled(window_enabled)
                self.setEnabled(enabled)
                self._review_running = False

    # _preview: Render the exact proposal, retaining Apply even when all review rows are filtered out.
    def _preview(self):
        if self._review_running:
            return
        self.apply_button.setEnabled(False)
        try:
            plan = self._review_plan()
            self._render(plan)
            self.apply_button.setEnabled(plan.changed)
        except Exception as error:
            self._invalidate()
            self.review.append('Review unavailable. Check the selected inventories and try Review Moves again.')
            QMessageBox.warning(self, 'Inventory Organizer', str(error))

    # _apply: Publish only the reviewed snapshot; successful changes remain unsaved in the app.
    def _apply(self):
        self.apply_button.setEnabled(False)
        try:
            changed = self.controller.apply()
            if changed:
                self.accept()  # Close after success so source names/counts cannot remain stale in this dialog.
        except Exception as error:
            self._invalidate()
            self.review.append('Apply failed. Use Review Moves again before retrying.')
            QMessageBox.warning(self, 'Inventory Organizer', str(error))
