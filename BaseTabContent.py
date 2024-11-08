from imports import *

class BaseTabContent(QWidget):
    def __init__(self, model, text_edit):
        super().__init__()
        self.model = model
        self.text_edit = text_edit

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

        ###
        # Create the text label and indicator widget for Background Processing status
        self.status_label = QLabel("Background Processing:", self)  # Create a text label for "Status"
        self.status_label.setFixedWidth(self.button_width - 25)

        self.status_indicator = QWidget(self)  # Create a widget to represent the LED
        self.status_indicator.setFixedSize(10, 10)  # Set size to small (like an LED)
        self.status_indicator.setToolTip("Heavy Background Processing Occurring? Green=No. Yellow=Yes.")

        # Initially set the indicator to red (off) and make it circular
        self.status_indicator.setStyleSheet(f"background-color: {GREEN_LED_COLOR}; border-radius: 4px;")

    def update_text_widget_from_model(self):
        pass

    def text_changed_signal(self):
        logger.debug("1st Tab text_changed_signal() enter")        
        self.update_tree_synced_indicator(False)
        logger.debug("1st Tab text_changed_signal() exit") 
        
    def blockSignals(self):
        pass
        
    def unblockSignals(self):
        pass  

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
                parentWindow.sync_from_text_window()
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

    # Function to update the indicator color (red or green)
    def update_status_indicator_to_green(self, green_if_true, context):
        logger.debug(f"update_status_indicator_to_green() ENTER, green?: {green_if_true}, context: {context}")
        palette = self.status_indicator.palette()
        
        if green_if_true:
            logger.verbose("green")
            self.status_indicator.setStyleSheet(f"background-color: {GREEN_LED_COLOR}; border-radius: 4px;")
        else:
            logger.verbose("yellow")
            self.status_indicator.setStyleSheet(f"background-color: {YELLOW_LED_COLOR}; border-radius: 4px;")
            
        self.status_indicator.setPalette(palette)
        self.status_indicator.update()
        logger.verbose("update_status_indicator_to_green() EXIT")  

    def set_led_based_on_app_thread_load(self, max_threads = 3, context="none"):
        logger.debug(f"set_led_based_on_app_thread_load() ENTER, max_threads: {max_threads}, context: {context}")
        
        def run():
            nonlocal max_threads
            logger.verbose("1st tab set_led_based_on_app_thread_load() ENTER")
            
            #4 comes from testing the idle state of the app informally:
            num_threads = get_num_app_child_threads()
            logger.verbose(f"max_threads: {max_threads}, num_threads: {num_threads}")
                
            if num_threads > max_threads:
                #set the led yellow:
                self.update_status_indicator_to_green(False, context)
                
                QTimer.singleShot(2000, run)
                logger.verbose("1st tab set_led_based_on_app_thread_load() EXIT, yellow\n")
            else:    
                #set the led green:        
                self.update_status_indicator_to_green(True,context)
                logger.verbose("1st tab set_led_based_on_app_thread_load() EXIT, green\n")            
        
        #wait 2 seconds on the first run:
        QTimer.singleShot(2000, run)
        logger.verbose("set_led_based_on_app_thread_load() EXIT")

    def update_tree_from_model(self):
        logger.debug("1st tab update_tree_from_model() called")

        json_data = self.load_json_from_model()
        if json_data is not None:
            self.blockSignals()
            self.clear_tree_view()
            self.populate_tree_from_json(json_data)
            self.unblockSignals()
            self.update_tree_synced_indicator(True)

            logger.debug("1st tab Tree view updated with model data.")


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

        