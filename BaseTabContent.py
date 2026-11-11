from imports import *
from DataViews import *
from init_text import INIT_TEXT
from NodeViewSyncDialog import node_view_sync_progress  # Outermost operation owns the shared processing notice.

class BaseTabContent(QWidget):


    def __init__(self, parent, model_context, text_edit):
        super().__init__()
        self.parent = parent
        self.model = parent.model
        self.text_edit = text_edit
        self.model_context = model_context
        self.view = JsonArrayView(self, self.model, self.model_context)

        # Set static width for buttons
        self.button_width = 140

        ###
        # Create the text label and indicator widget for Tree sync status
        self.tree_synced_label = QLabel("Synched to Node View)", self)  # The Raw JSON heading now supplies the context.
        sync_font = self.tree_synced_label.font()  # Keep the status text separate from the bold pane title.
        sync_font.setBold(False)  # Only Raw JSON remains bold.
        self.tree_synced_label.setFont(sync_font)  # Apply normal weight to the existing status label.
        self.tree_synced_label.setFixedWidth(self.tree_synced_label.sizeHint().width())  # Fit the full label instead of clipping it.

        self.tree_synced = True
        self.tree_synced_indicator = QWidget(self)  # Create a widget to represent the LED
        self.tree_synced_indicator.setFixedSize(10, 10)  # Set size to small (like an LED)
        self.tree_synced_indicator.setToolTip("Is tree synced from Text Window? Green=yes. Red=no.")

        # Initially set the indicator to red (off) and make it circular
        self.tree_synced_indicator.setStyleSheet(f"background-color: {GREEN_LED_COLOR}; border-radius: 4px;")

    # make_pane_heading: Build a small left-aligned visual label without altering either pane's data logic.
    def make_pane_heading(self, title):
        heading = QLabel(title, self)  # Each pane receives its own explicitly named label.
        font = heading.font()  # Preserve the application font while emphasizing both pane headings.
        font.setBold(True)  # Node View and Raw JSON use the same bold heading helper.
        heading.setFont(font)
        heading.setAlignment(Qt.AlignLeft)  # Align the heading to the pane's left content edge.
        return heading  # The tab places this above its existing pane controls and content.

    # make_raw_json_heading: Place the existing live sync LED beside the bold Raw JSON pane title.
    def make_raw_json_heading(self):
        heading = QHBoxLayout()  # Keep title, punctuation, LED and status on one line.
        heading.setAlignment(Qt.AlignLeft)  # Retain the existing heading position at the pane edge.
        heading.setSpacing(4)  # Keep the inline status compact without changing the button row.
        heading.addWidget(self.make_pane_heading("Raw JSON"))  # Only the title uses the bold helper.
        opening = QLabel("(", self)  # Match the opening parenthesis in the requested display.
        font = opening.font()  # Preserve the application font for the punctuation.
        font.setBold(False)  # Parenthesis and sync status are not bold.
        opening.setFont(font)  # Apply normal-weight punctuation.
        heading.addWidget(opening)  # Place the parenthesis before the live LED.
        heading.addWidget(self.tree_synced_indicator)  # Reuse the indicator so its state behavior is unchanged.
        heading.addWidget(self.tree_synced_label)  # Use the shorter normal-weight status label.
        return heading  # Each tab installs this above its existing right-pane controls.

    def text_changed_signal(self):
        logger.debug("1st Tab text_changed_signal() enter")        
        self.update_tree_synced_indicator(False)
        logger.debug("1st Tab text_changed_signal() exit")

    def handle_text_edit_changed_signal(self):
        self.blockSignals()
        self.sync_tree_from_text_window()
        self.unblockSignals()

    def handle_tree_changed_signal(self):
        self.blockSignals()
        self.sync_text_from_tree_window()
        self.unblockSignals()

    def blockSignals(self):
        logger.debug("blockSignals() ENTER")
        self.text_edit.blockSignals(True)
        self.tree_widget.blockSignals(True)
        self.model.blockSignals(True)
        logger.debug("blockSignals() ENTER")

    def unblockSignals(self):
        logger.debug("unblockSignals() ENTER")
        self.text_edit.blockSignals(False)
        self.tree_widget.blockSignals(False)
        self.model.blockSignals(False)
        logger.debug("unblockSignals() ENTER")

    def copy_to_clipboard(self, parentWindow = None):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.text_edit.toPlainText())
        QMessageBox.information(parentWindow, "Copied", "Text copied to clipboard!")

    def paste_to_text_window(self, parentWindow=None):
        # Show confirmation dialog
        reply = QMessageBox.question(
            parentWindow,
            "Confirm Overwrite",
            "About to OVERWRITE All Data In The Text Window! Continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        # If user chooses 'Yes', proceed to paste from clipboard
        if reply == QMessageBox.Yes:
            clipboard = QApplication.clipboard()
            clipboard_text = clipboard.text()
            if clipboard_text:
                self.text_edit.setPlainText(clipboard_text)
                parentWindow.sync_tree_from_text_window()
                QMessageBox.information(parentWindow, "Pasted", "Text pasted from clipboard!")
            else:
                QMessageBox.warning(parentWindow, "Clipboard Empty", "No text found in the clipboard!")

    def pretty_print_text_widget(self, model, parentWindow=None):
        logger.debug("pretty_print_text_widget() ENTER")

        #grab the current data from the text window in case any changes were made:
        if not parentWindow.update_model_from_text_edit():  # Invalid or refused text: keep it and the red light.
            return  # Do not overwrite the user's text with older app data.
        #reload the text window from the model, which will result in the pretty print reformatting:
        parentWindow.update_text_widget_from_model()
        #now update the tree window to make sure allviews are consistent:
        parentWindow.update_tree_from_model()

        logger.debug("pretty_print_text_widget() EXIT")

    # set_led_based_on_app_thread_load: Retain legacy callers without inferring user-facing tasks from thread counts.
    def set_led_based_on_app_thread_load(self, max_threads=3, context="none"):
        return  # Real operation boundaries now own Current Task Info; no polling or LED remains.

    def model_changed(self, tab):
        logger.debug(f"Model Changed.")

        if tab:
            #we only want to go on if we have passed in ourself:
            if(tab is not self):
                return

        # Set tree from text
        try:
            self.blockSignals()
            try:
                self.update_text_widget_from_model()
                self.update_tree_from_model()
                self.tree_widget.expand_tree_to_level(1)
            finally:
                self.unblockSignals()  # Never leave this tab's signals blocked after an unexpected error.
            self.update_tree_synced_indicator(True)

        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Error", f"Failed to parse JSON from text window: {e}")

        logger.verbose(f"Now: {self.view.get_text()}")

    # sync_tree_from_text_window: Reuse an outer delete popup or own one for a standalone sync request.
    def sync_tree_from_text_window(self):
        if getattr(self, '_node_sync_active', False):  # Existing helpers dispatch Qt events; refuse a nested sync on this tab.
            return False  # Do not restart an already running sync; this call did not sync.
        self._node_sync_active = True  # Set before the shared popup helper dispatches events.
        try:
            with node_view_sync_progress(self.main_window):  # Only the outermost operation owns popup dismissal.
                self.main_window.background_processing_signal.emit(4, self.model_context)  # Preserve task reporting.
                self.update_tree_synced_indicator(False)  # Preserve the existing processing order.
                if not self.update_model_from_text_edit():  # Row 450: a failed parse or refusal stops the sync.
                    return False  # Keep the text and the red light; Node View still shows the app data.
                self.update_tree_from_model()  # Preserve the final tree rebuild.
                self.tree_widget.expand_tree_to_level(1)  # Preserve final node expansion.
                self.update_tree_synced_indicator(True)  # Finish status updates before releasing the popup scope.
                return True  # The edited text reached the app data.
        finally:
            self._node_sync_active = False  # Permit another sync even after an exception.

    def sync_text_from_tree_window(self):
        logger.debug("sync from Tree Window ENTER")
        self.update_model_from_tree()
        self.update_text_widget_from_model()
        logger.debug("sync from Tree Window EXIT")

    def update_model_from_text_edit(self):
        logger.debug("update_model_from_text_edit() enter")
        self.update_tree_synced_indicator(False)
        new_text = self.text_edit.toPlainText()
        applied = self.view.set_text(new_text)  # False when the text was invalid or refused; data unchanged.
        logger.debug("update_model_from_text_edit() exit")
        return applied  # Callers stop on False so the text and red light are kept.

    def clear_tree_view(self):
        logger.debug("1st tab clear_tree_view() Called.")
        self.tree_widget.clear()

    def update_tree_from_model(self):
        logger.debug("update_tree_from_model() called")
        json_data = self.view.get_json()

        if json_data is not None:
            self.clear_tree_view()
            self.populate_tree_from_json(json_data)
            self.update_tree_synced_indicator(True)

            logger.debug("Tree view updated with model data.")
        else:
            logger.error("no data from model")

    # Function to update the indicator color (red or green)
    def update_tree_synced_indicator(self, green_if_true):
        logger.debug("update_tree_synced_indicator() ENTER")
        self.tree_synced = green_if_true
        palette = self.tree_synced_indicator.palette()

        if green_if_true:
            logger.debug("1st tab green")
            self.tree_synced_indicator.setStyleSheet(f"background-color: {GREEN_LED_COLOR}; border-radius: 4px;")
        else:
            logger.debug("1st tab red")
            self.tree_synced_indicator.setStyleSheet(f"background-color: red; border-radius: 4px;")

        self.tree_synced_indicator.setPalette(palette)
        self.tree_synced_indicator.update()
        QApplication.processEvents()
        logger.debug("update_tree_synced_indicator() EXIT")

    def populate_tree(self, data, parent=None):
        logger.debug("populate_tree() ENTER")
        if parent is None:
            parent = self.tree_widget.invisibleRootItem()

        if isinstance(data, dict):
            for key, value in data.items():
                item = QTreeWidgetItem([key])
                parent.addChild(item)
                self.populate_tree(value, item)
        elif isinstance(data, list):
            for index, value in enumerate(data):
                item = QTreeWidgetItem([f"Item {index}"])
                parent.addChild(item)
                self.populate_tree(value, item)

        logger.debug("populate_tree() EXIT")

    def update_text_widget_from_model(self):
        logger.debug("update_text_widget_from_model() enter")
        self.main_window.background_processing_signal.emit(4, self.model_context)
        self.text_edit.setPlainText(self.view.get_text())
        logger.debug("update_text_widget_from_model() exit")

    # update_model_from_tree: Apply Node View's structure to the app data; refuse and restore Node View if unusable.
    def update_model_from_tree(self):
        logger.debug("update_model_from_tree() ENTER")
        self.main_window.background_processing_signal.emit(4, self.model_context)

        tree_data = self.tree_widget_data_to_json()
        logger.verbose(f"tree string: {tree_data}")
        problem = self.view.tree_data_problem(tree_data)  # Row 510: same app-integrity rules as Raw JSON.
        if problem:  # Unusable result: refuse before anything is applied.
            self.view.warn_rejected_text(problem + ' Nothing was changed; Node View has been restored.',
                                         NODE_VIEW_REJECTED_TITLE)
        applied = not problem and self.view.set_json(tree_data)  # Inventory also applies its count/order rule there.
        if not applied:  # Refused here or by set_json: show the unchanged app data again.
            self.update_tree_from_model()  # Rebuild Node View from the unchanged data.
            self.tree_widget.expand_tree_to_level(1)  # Same expansion as a normal rebuild.
        logger.debug("update_model_from_tree() EXIT")
        return applied  # True only when Node View's structure reached the app data.


# Copyright (C) 2024-2026 BigBuffaloBill - Bill Ryder <me@billryder.com>
#
# This file is part of BBB NMS Save File Manipulator.
#
# BBB NMS Save File Manipulator is free software: you can redistribute it and/or modify it under the terms of
# the GNU General Public License as published by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# BBB NMS Save File Manipulator is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details. You should have received a copy of the GNU General Public License along with
# this program (see the LICENSE file). If not, see <https://www.gnu.org/licenses/>.
