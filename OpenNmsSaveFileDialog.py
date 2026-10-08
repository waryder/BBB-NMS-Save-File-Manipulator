# File: OpenNmsSaveFileDialog.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\OpenNmsSaveFileDialog.py
# Purpose: Popup launched by the main window's "Open NMS Save File" button (project row 10, "bones").
#          Shows the save path, a Game Slot dropdown and a Save File dropdown populated READ-ONLY from
#          the save folder's mf_ meta files. Pick Folder persists preferences; row 40 loads/restores/backs up slots.

# Pull in the shared PyQt5 widgets, Qt namespace and logger used across the app
from imports import *
# Local time formatting for the mf_ Unix timestamps
import datetime
# Read-only slot/meta scanner from the in-repo codec
from nms_save_codec.meta_info import list_save_slots
# Reuse the shared preferences manager rather than creating a competing config instance.
from IniFileManager import ini_file_manager
import NmsSlotOperations as slot_ops  # One globally switched stdout trace for row-40 logic.

# Project/file prefix for debug output, per Bill's code standards
DEBUG_PREFIX = "[BBB-NMS-SFM/OpenNmsSaveFileDialog]"
# Non-error row-40 traces use NmsSlotOperations.DEBUG_ENABLED, the single shared stdout switch.

# Root that holds the Steam st_<id> save folders
NMS_SAVE_ROOT = os.path.join(os.environ.get("APPDATA", ""), "HelloGames", "NMS")
# Shown in every not-yet-built action
NOT_IMPLEMENTED_TEXT = "is not implemented yet."


# find_default_save_folder
# Returns the first st_* folder under %APPDATA%\HelloGames\NMS, or "" when none exists.
def find_default_save_folder():
    # No NMS root means no Steam saves on this machine
    if not os.path.isdir(NMS_SAVE_ROOT):
        return ""
    # Steam save folders are named st_<steamid64>
    for entry in sorted(os.listdir(NMS_SAVE_ROOT)):
        # Take the first matching directory
        full_path = os.path.join(NMS_SAVE_ROOT, entry)
        if entry.lower().startswith("st_") and os.path.isdir(full_path):
            return full_path
    # Nothing matched
    return ""


# format_timestamp
# Turns an mf_ Unix timestamp into local "YYYY-MM-DD HH:MM:SS", or "(unknown)" when absent.
def format_timestamp(timestamp):
    # Zero means the meta format had no timestamp field
    if not timestamp:
        return "(unknown)"
    # Convert to local time for display
    return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


class OpenNmsSaveFileDialog(QDialog):
    # __init__
    # Builds the popup, then fills it from the remembered or default save folder.
    def __init__(self, parent=None):
        # Initialize the base QDialog with the main window as parent
        super().__init__(parent)
        # Window title matches the button that opens it
        self.setWindowTitle("Open NMS Save File")
        # Wide enough for the full Steam save path
        self.setMinimumSize(640, 260)
        # Remove the "?" context-help button, matching LoadDataDialog
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        # Prefer the main window's shared manager when the dialog has a parent.
        self.ini_file_manager = getattr(parent, 'ini_file_manager', ini_file_manager)
        # Restore a usable remembered folder, otherwise discover the Steam default.
        self.save_folder = self._get_initial_save_folder()
        # Build all widgets and layouts
        self._build_ui()
        # Populate dropdowns from the folder
        self._populate_slots()

    # _get_initial_save_folder
    # Restores an existing remembered directory without overwriting an unavailable saved path.
    def _get_initial_save_folder(self):
        # A malformed preference should not prevent the dialog from opening.
        try:
            # Read the folder from the application's persistent preferences.
            remembered = self.ini_file_manager.get_nms_save_folder()
            # A disconnected or deleted folder falls back to normal discovery.
            if remembered and os.path.isdir(remembered):
                return remembered
        except Exception as exc:
            # Report preference read errors without suppressing them behind the debug gate.
            logger.error(f"{DEBUG_PREFIX} _get_initial_save_folder: {exc}")
            QMessageBox.warning(self, "Open NMS Save File", f"Could not read saved folder preference:\n{exc}")
        # Discovery itself may fail on an inaccessible NMS root.
        try:
            return find_default_save_folder()
        except OSError as exc:
            # Let the user recover with Pick Folder rather than failing construction.
            logger.error(f"{DEBUG_PREFIX} _get_initial_save_folder: discovery failed: {exc}")
            return ""

    # _build_ui
    # Creates the File Details grid and the button row, then applies the layout.
    def _build_ui(self):
        # Main vertical stack: details grid on top, buttons below
        layout = QVBoxLayout()
        # Grid of label/value rows like goatfungus's Main tab
        layout.addLayout(self._build_details_grid())
        # Action buttons (stubs for now)
        layout.addLayout(self._build_button_row())
        # Apply to the dialog
        self.setLayout(layout)

    # _build_details_grid
    # Builds Storage / Save Path / Game Slot / Save File / Modified / Save Name / Description rows.
    def _build_details_grid(self):
        # Two-column grid plus a third column for the Pick Folder button
        grid = QGridLayout()
        # Value labels that get updated later
        self.save_path_label = QLabel(self.save_folder or "(no NMS save folder found)")
        self.modified_label = QLabel("(no file selected)")
        self.save_name_label = QLabel("(no file selected)")
        self.description_label = QLabel("(no file selected)")
        # The two dropdowns
        self.slot_combo = QComboBox()
        self.file_combo = QComboBox()
        self.file_combo.setEnabled(False)  # Display metadata only; Load Slot selects by row 35, never by manual dropdown choice.
        self.file_combo.setToolTip("Display only. Load Slot uses metadata timestamps; equal times require Manual-or-Cancel confirmation.")  # Explain selection.
        # Pick Folder changes and remembers the directory shown beside it.
        self.pick_folder_button = QPushButton("Pick Folder...")
        self.pick_folder_button.clicked.connect(self._on_pick_folder_clicked)
        # Lay out each labeled row
        rows = [("Storage:", QLabel("Steam")), ("Save Path:", self.save_path_label),
                ("Game Slot:", self.slot_combo), ("Save File:", self.file_combo),
                ("Modified:", self.modified_label), ("Save Name:", self.save_name_label),
                ("Description:", self.description_label)]
        for row, (caption, widget) in enumerate(rows):
            grid.addWidget(QLabel(caption), row, 0)
            grid.addWidget(widget, row, 1)
        # Button goes on the Save Path row
        grid.addWidget(self.pick_folder_button, 1, 2)
        # React to selection changes
        self.slot_combo.currentIndexChanged.connect(self._on_slot_changed)
        self.file_combo.currentIndexChanged.connect(self._on_file_changed)
        return grid

    # _build_button_row
    # Builds the Slot Backup / Open / Close buttons.
    def _build_button_row(self):
        # Horizontal row, right-aligned via a leading stretch
        row = QHBoxLayout()
        row.addStretch()
        # Backup the app's active slot only after consistency checks and explicit disk-write consent.
        self.backup_button = QPushButton("Backup Slot")
        self.backup_button.clicked.connect(self._on_slot_backup_clicked)
        # Restore ZIP into app memory only; the ZIP filenames supply its original slot.
        self.restore_button = QPushButton("Restore Slot")
        self.restore_button.clicked.connect(self._on_restore_clicked)  # Use the main window's transaction.
        # Live loading is part of row 40, not the later live-save placeholder.
        self.open_button = QPushButton("Load Slot")
        self.open_button.clicked.connect(self._on_open_clicked)
        # Close dismisses the dialog as rejected
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.reject)
        grid = QGridLayout()  # A right-aligned 2x2 block, with Backup/Restore on its second row.
        grid.addWidget(self.open_button, 0, 0)  # Load Slot at the upper left.
        grid.addWidget(self.close_button, 0, 1)  # Close at the upper right.
        grid.addWidget(self.backup_button, 1, 0)  # Backup Slot at the lower left.
        grid.addWidget(self.restore_button, 1, 1)  # Restore Slot at the lower right.
        for button in (self.open_button, self.close_button, self.backup_button, self.restore_button):  # Match all block widths.
            button.setFixedWidth(130)  # Equal sizes keep both columns aligned.
        row.addLayout(grid)  # Leading stretch keeps the block in the lower right.
        return row

    # _populate_slots
    # Reads the save folder (read-only) and fills the Game Slot dropdown.
    def _populate_slots(self):
        # Start empty every time
        self.slot_combo.clear()
        # Explicitly clear dependent fields even when the slot combo was already empty.
        self.file_combo.clear()
        self._on_file_changed(-1)
        # Nothing to scan without a folder
        if not self.save_folder:
            return
        # Scan; a failure is reported but does not crash the app
        try:
            slots = list_save_slots(self.save_folder)
        except Exception as exc:
            logger.error(f"{DEBUG_PREFIX} _populate_slots: scan failed for {self.save_folder}: {exc}")
            QMessageBox.warning(self, "Open NMS Save File", f"Could not read save folder:\n{exc}")
            return
        # One entry per slot; the slot dict rides along as item data
        for slot in slots:
            self.slot_combo.addItem(self._slot_label(slot), slot)
        slot_ops.trace("OpenNmsSaveFileDialog", "slots_populated", folder=self.save_folder, count=len(slots))  # Shared stdout switch.

    # _slot_label
    # Builds "Slot N - <save name>" from the newest readable file in the slot.
    def _slot_label(self, slot):
        # Only files whose mf_ decrypted successfully have a name
        readable = [f for f in slot["files"] if f["meta"]]
        # No readable meta at all
        if not readable:
            return f"Slot {slot['slot']} - (unreadable)"
        # Newest metadata labels the slot; this is Bill's app policy, not proven game behavior.
        newest = max(readable, key=lambda f: f["meta"]["timestamp"])
        return f"Slot {slot['slot']} - {newest['meta']['name'] or '(no name)'}"

    # _on_slot_changed
    # Fills the Save File dropdown with the slot's live files; newest is pre-selected.
    def _on_slot_changed(self, index):
        # Rebuild the file list from scratch
        self.file_combo.clear()
        slot = self.slot_combo.itemData(index)
        # Empty dropdown (e.g. after clear) has no data
        if not slot:
            return
        # One entry per live file
        for record in slot["files"]:
            stamp = format_timestamp(record["meta"]["timestamp"]) if record["meta"] else "(unreadable)"
            self.file_combo.addItem(f"{record['file_name']} ({record['save_type']}) - {stamp}", record)
        # Pick the newest readable file
        stamps = [r["meta"]["timestamp"] if r["meta"] else -1 for r in slot["files"]]
        self.file_combo.setCurrentIndex(stamps.index(max(stamps)))

    # _on_file_changed
    # Shows the selected file's Modified / Save Name / Description from its mf_ meta.
    def _on_file_changed(self, index):
        # Selected file record (None when the list is empty)
        record = self.file_combo.itemData(index)
        # Reset the labels when nothing is selected
        if not record:
            for label in (self.modified_label, self.save_name_label, self.description_label):
                label.setText("(no file selected)")
            return
        # Meta could not be read: show the reason
        if not record["meta"]:
            self.modified_label.setText("(unreadable)")
            self.save_name_label.setText("(unreadable)")
            self.description_label.setText(record["error"] or "")
            return
        # Normal case
        self.modified_label.setText(format_timestamp(record["meta"]["timestamp"]))
        self.save_name_label.setText(record["meta"]["name"])
        self.description_label.setText(record["meta"]["summary"])

    # _show_not_implemented
    # Common message for every stubbed action.
    def _show_not_implemented(self, feature):
        # Plain info box; nothing is changed anywhere
        QMessageBox.information(self, "Open NMS Save File", f"{feature} {NOT_IMPLEMENTED_TEXT}")

    # _on_pick_folder_clicked
    # Selects a save directory; cancellation leaves the current path and preferences unchanged.
    def _on_pick_folder_clicked(self):
        # Start in the current folder, or the NMS root when no folder was discovered.
        folder = QFileDialog.getExistingDirectory(self, "Pick NMS Save Folder",
                self.save_folder or NMS_SAVE_ROOT, QFileDialog.ShowDirsOnly)
        # Cancel is a no-op, including no preference writes or dropdown resets.
        if not folder:
            return
        # Validate and normalize before committing a new preference.
        folder = os.path.normpath(folder)
        if not os.path.isdir(folder):
            # The directory may have disappeared while the picker was open.
            QMessageBox.warning(self, "Open NMS Save File", "The selected folder no longer exists.")
            return
        # Commit the new folder only if its persistent preference was written successfully.
        self._apply_save_folder(folder)

    # _apply_save_folder
    # Persists the selection before changing the displayed folder and repopulating dropdowns.
    def _apply_save_folder(self, folder):
        # Remembering a folder writes preferences, so choosing the directory alone is not consent.
        reply = QMessageBox.warning(self, "Confirm preference disk write",
                f"About to write the remembered NMS save-folder preference:\n{folder}\nContinue?",
                QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)  # Explicit warning before persistence.
        slot_ops.trace("OpenNmsSaveFileDialog", "folder_write_confirmation", accepted=reply == QMessageBox.Ok, folder=folder)  # Audit consent.
        if reply != QMessageBox.Ok:  # Cancel leaves dropdowns, path and preferences unchanged.
            return  # No disk write.
        # A failed preference write leaves the current selection untouched.
        try:
            self.ini_file_manager.store_nms_save_folder(folder)
        except Exception as exc:
            # Show the failure and retain both the previous folder and dropdowns.
            logger.error(f"{DEBUG_PREFIX} _apply_save_folder: persistence failed: {exc}")
            QMessageBox.warning(self, "Open NMS Save File", f"Could not remember save folder:\n{exc}")
            return
        # Update the displayed path only after persistence succeeds.
        self.save_folder = folder
        self.save_path_label.setText(folder)
        # Existing read-only scanning refreshes slots, files and metadata labels.
        self._populate_slots()

    # _on_slot_backup_clicked
    # Backup the active app slot, not a different slot being browsed in this popup.
    def _on_slot_backup_clicked(self):
        slot_ops.trace("OpenNmsSaveFileDialog", "backup_requested", browsing_slot=self.slot_combo.currentIndex())  # Inspect action origin.
        self.parent().backup_nms_slot()  # Main window applies consistency and disk-warning gates.

    # _on_restore_clicked
    # Restore a validated ZIP into app memory while retaining the selected live-folder context.
    def _on_restore_clicked(self):
        if self.parent().restore_nms_slot(self.save_folder):  # No extraction, live writes or automatic backup.
            self.accept()  # Dismiss only after a fully committed load.

    # _on_open_clicked
    # Load the selected slot using metadata-only selection, ignoring the display-only file dropdown.
    def _on_open_clicked(self):
        slot = self.slot_combo.currentData()  # Slot identity comes from the read-only scan.
        if not slot:  # Empty/unavailable folders cannot supply a slot.
            QMessageBox.warning(self, "Load Slot", "Choose a readable game slot first.")  # Explain recovery.
            return  # Preserve data, LED and target.
        self.parent().load_nms_live_slot(self.save_folder, slot["slot"], on_load_confirmed=self.accept)  # OK closes this dialog before processing; Cancel never calls accept.
