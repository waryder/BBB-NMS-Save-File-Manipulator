from imports import *
from DataViews import *
from init_text import INIT_TEXT

class BaseTabContent(QWidget):
    timer_running = False

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
        self.tree_synced_label = QLabel("Tree Synced:", self)  # Create a text label for "Status"
        self.tree_synced_label.setFixedWidth(self.button_width - 75)

        self.tree_synced = True
        self.tree_synced_indicator = QWidget(self)  # Create a widget to represent the LED
        self.tree_synced_indicator.setFixedSize(10, 10)  # Set size to small (like an LED)
        self.tree_synced_indicator.setToolTip("Is tree synced from Text Window? Green=yes. Red=no.")

        # Initially set the indicator to red (off) and make it circular
        self.tree_synced_indicator.setStyleSheet(f"background-color: {GREEN_LED_COLOR}; border-radius: 4px;")

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
        parentWindow.update_model_from_text_edit()
        #reload the text window from the model, which will result in the pretty print reformatting:
        parentWindow.update_text_widget_from_model()
        #now update the tree window to make sure allviews are consistent:
        parentWindow.update_tree_from_model()

        logger.debug("pretty_print_text_widget() EXIT")

    # def is_status_indicator_green(self):
    #     if self.parent.status_indicator.styleSheet() == f"background-color: {GREEN_LED_COLOR}; border-radius: 4px;":
    #         return True
    #     else:
    #         return False

    # Function to update the indicator color (red or green)
    def update_status_indicator_to_green(self, green_if_true):
        logger.debug(f"update_status_indicator_to_green() ENTER, green?: {green_if_true}")
        palette = self.parent.status_indicator.palette()
        
        if green_if_true:
            logger.verbose("green")
            self.parent.status_indicator.setStyleSheet(f"background-color: {GREEN_LED_COLOR}; border-radius: 4px;")
        else:
            logger.verbose("yellow")
            self.parent.status_indicator.setStyleSheet(f"background-color: {YELLOW_LED_COLOR}; border-radius: 4px;")
            
        self.parent.status_indicator.setPalette(palette)
        self.parent.status_indicator.update()

        logger.verbose("update_status_indicator_to_green() EXIT")

    def set_led_based_on_app_thread_load(self, max_threads = 3, context="none"):
        logger.debug(f"set_led_based_on_app_thread_load() ENTER, max_threads: {max_threads}, context: {context}")

        # Check if a timer is already running
        if BaseTabContent.timer_running:
            logger.debug("Timer is already running, exiting")
            return  # Prevent multiple loops from starting

        BaseTabContent.timer_running = True  # Set the flag to indicate the timer is running

        def run():
            nonlocal max_threads
            logger.verbose("1st tab set_led_based_on_app_thread_load() ENTER")
            
            #4 comes from testing the idle state of the app informally:
            num_threads = get_num_app_child_threads()
            logger.verbose(f"max_threads: {max_threads}, num_threads: {num_threads}")
                
            if num_threads > max_threads:
                #set the led yellow:
                self.update_status_indicator_to_green(False)
                QTimer.singleShot(2000, run)

                logger.verbose("1st tab set_led_based_on_app_thread_load() EXIT, yellow\n")
            else:    
                # Set the LED to green and stop the timer:
                self.update_status_indicator_to_green(True)
                BaseTabContent.timer_running = False  # Reset the flag
                logger.verbose("1st tab set_led_based_on_app_thread_load() EXIT, green\n")
        
        #wait 2 seconds on the first run:
        QTimer.singleShot(2000, run)
        logger.verbose("set_led_based_on_app_thread_load() EXIT")

    def model_changed(self, tab):
        logger.debug(f"Model Changed.")

        if tab:
            #we only want to go on if we have passed in ourself:
            if(tab is not self):
                return

        # Set tree from text
        try:
            self.blockSignals()
            self.update_text_widget_from_model()
            self.update_tree_from_model()
            self.tree_widget.expand_tree_to_level(1)
            self.unblockSignals()
            self.update_tree_synced_indicator(True)

        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Error", f"Failed to parse JSON from text window: {e}")

        logger.verbose(f"Now: {self.view.get_text()}")

    def sync_tree_from_text_window(self):
        self.main_window.background_processing_signal.emit(4, self.model_context)
        self.update_tree_synced_indicator(False)
        self.update_model_from_text_edit()
        self.update_tree_from_model()
        self.tree_widget.expand_tree_to_level(1)
        self.update_tree_synced_indicator(True)

    def sync_text_from_tree_window(self):
        logger.debug("sync from Tree Window ENTER")
        self.update_model_from_tree()
        self.update_text_widget_from_model()
        logger.debug("sync from Tree Window EXIT")

    def update_model_from_text_edit(self):
        logger.debug("update_model_from_text_edit() enter")
        self.update_tree_synced_indicator(False)
        new_text = self.text_edit.toPlainText()
        self.view.set_text(new_text)
        logger.debug("update_model_from_text_edit() exit")

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

    def update_model_from_tree(self):
        logger.debug("update_model_from_tree() ENTER")
        self.main_window.background_processing_signal.emit(4, self.model_context)

        tree_data = self.tree_widget_data_to_json()
        logger.verbose(f"tree string: {tree_data}")
        self.view.set_json(tree_data)
        logger.debug("update_model_from_tree() EXIT")



    # MIT License
#
# Copyright (c) 2024 BigBuffaloBill - Bill Ryder <me@billryder.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# 1. The above copyright notice and this permission notice shall be included
#    in all copies or substantial portions of the Software.
#
# 2. Attribution Requirement: Any use of this code, in whole or in part,
#    must retain the following attribution notice in the source code comments:
#    
#    This code includes portions of the software originally developed by
#    BigBuffaloBill - Bill Ryder <me@billryder.com>, available under the MIT License.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# This software makes use of PyQt5, which is licensed under the GPL v3 License.
# The PyQt5 library is a third-party library that is not covered under the 
# MIT License governing this software. As required by the GPL v3 License, 
# the source code for this software is made available, and you are free to
# modify and redistribute it under the terms of the GPL v3 License.
#
# You can find more details on the PyQt5 license here: https://www.riverbankcomputing.com/software/pyqt/license
# To comply with the GPL v3 License, you must include the full source code and this 
# license notice with any redistributions of this software that include PyQt5.        

        