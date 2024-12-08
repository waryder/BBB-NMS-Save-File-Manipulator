from PyQt5.QtWidgets import QApplication, QWidget
import sys, os

#Qt debug output:
#os.environ["QT_DEBUG_PLUGINS"] = "1"  # Enable debug logging for Qt plugins
#os.environ["QT_LOGGING_RULES"] = "*.debug=true"  # Enable debug logs for all Qt components

# needed so that after formal install, python can find all the files:
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from NMSHelpMenu import NMSHelpMenu
from FirstTabContent import FirstTabContent
from SecondTabContent import SecondTabContent
from ThirdTabContent import ThirdTabContent
from ForthTabContent import ForthTabContent
from DataModels import *
from DataViews import *
from IniFileManager import *
from LoadDataDialog import LoadDataDialog
from init_text import INIT_TEXT

def global_exception_handler(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        # Let KeyboardInterrupt exceptions pass through without logging
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

        # Print the error and traceback
    logger.error(f"Unhandled exception: {exc_value}")
    traceback.print_exception(exc_type, exc_value, exc_traceback)

# Set the global exception handler
sys.excepthook = global_exception_handler

class MainWindow(QMainWindow):
    background_processing_signal = pyqtSignal(int, str)
    text_edit_changed_signal     = pyqtSignal()
    tree_changed_signal          = pyqtSignal()

    def __init__(self):
        logger.debug("MainWindow(QMainWindow).__init__ ENTER")
        super().__init__()

        self.thinking_dialog = TextOnlyLoadingDialog("Loading data, please wait...", self)
        self.ini_file_manager = ini_file_manager
        self.model = None
        self.view = None
        # Set static width for buttons
        self.button_width = 140

        loaded_text = False
        load_dialog = LoadDataDialog()

        if load_dialog.exec_() == QDialog.Accepted:  # Only proceed if "Load" button was clicked (dialog accepted)
            if load_dialog.is_skip_data_load_checked():
                loaded_text = INIT_TEXT
            else:
                loaded_text = load_dialog.get_text()

        if loaded_text:
            self.start_thinking_window()

            self.model = JsonArrayModel(INIT_TEXT = loaded_text)
            self.view = JsonArrayView(self, self.model)

            self.thinking_dialog.close()
        else:
            QMessageBox.information(None, "Notification", "No JSON data received; Application will exit!")
            QApplication.quit()  # Uncomment to clean up QT
            sys.exit()  # Immediately exit the program

        self.import_button = QPushButton("Import 'BaseContext' Json from Clipboard")
        self.import_button.setFixedWidth(250)

        self.export_button = QPushButton("Export 'BaseContext' Json to Clipboard")
        self.export_button.setFixedWidth(250)

        ###
        # Create the text label and indicator widget for Background Processing status
        self.status_label = QLabel("Background Processing:", self)  # Create a text label for "Status"
        self.status_label.setFixedWidth(self.button_width - 25)

        self.status_indicator = QWidget(self)  # Create a widget to represent the LED
        self.status_indicator.setFixedSize(10, 10)  # Set size to small (like an LED)
        self.status_indicator.setToolTip("Heavy Background Processing Occurring? Green=No. Yellow=Yes.")

        # Initially set the indicator to red (off) and make it circular
        self.status_indicator.setStyleSheet(f"background-color: {GREEN_LED_COLOR}; border-radius: 4px;")

        # Create the tab widget
        self.tabs = QTabWidget()

        # Create and add tabs
        self.tab1 = FirstTabContent(self)
        self.tab2 = SecondTabContent(self)
        self.tab3 = ThirdTabContent(self)
        self.tab4 = ForthTabContent(self)
        self.background_processing_signal.connect(self.tab1.set_led_based_on_app_thread_load)
        self.background_processing_signal.connect(self.tab2.set_led_based_on_app_thread_load)
        self.background_processing_signal.connect(self.tab3.set_led_based_on_app_thread_load)
        self.background_processing_signal.connect(self.tab4.set_led_based_on_app_thread_load)
        self.text_edit_changed_signal.connect(self.tab1.handle_text_edit_changed_signal)
        self.text_edit_changed_signal.connect(self.tab2.handle_text_edit_changed_signal)
        self.text_edit_changed_signal.connect(self.tab3.handle_text_edit_changed_signal)
        self.text_edit_changed_signal.connect(self.tab4.handle_text_edit_changed_signal)
        self.tree_changed_signal.connect(self.tab1.handle_tree_changed_signal)
        self.tree_changed_signal.connect(self.tab2.handle_tree_changed_signal)
        self.tree_changed_signal.connect(self.tab3.handle_tree_changed_signal)
        self.tree_changed_signal.connect(self.tab4.handle_tree_changed_signal)

        self.tabs.addTab(self.tab1, 'Base Processing')
        self.tabs.addTab(self.tab2, 'Starship Processing')
        self.tabs.addTab(self.tab3, 'Inventory Processing')
        self.tabs.addTab(self.tab4, 'Teleport Endpoints')

        self.tabs.tabBarClicked.connect(self.before_tab_change)
        self.tabs.currentChanged.connect(self.after_tab_change)

        # Create a main layout and central widget
        main_layout = QVBoxLayout()
        central_widget = QWidget(self)

        # Create a horizontal layout for the buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.import_button)
        button_layout.addWidget(self.export_button)
        ###
        status_layout = QHBoxLayout()
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.status_indicator)

        button_layout.addLayout(status_layout)
        button_layout.setAlignment(Qt.AlignLeft)

        # Add the button layout to the main layout
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.tabs)  # Add the tab widget below the buttons

        # Set the layout for the central widget and set it as the central widget of the main window
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Set up window properties
        self.setWindowTitle('BBB NMS Save File Manipulator')
        self.setGeometry(400, 250, 1500, 800)

        # Create menu bar
        self.create_menu_bar()

        self.import_button.clicked.connect(self.import_button_clicked)
        self.export_button.clicked.connect(self.export_button_clicked)

        # Emit signal for background processing
        self.background_processing_signal.emit(5, "Main Window")
        self.thinking_dialog.close()

        logger.debug("MainWindow(QMainWindow).__init__ EXIT")

    def start_thinking_window(self):
        # Show the custom text-only loading dialog
        self.thinking_dialog.show()

        # Process events to ensure it renders fully
        QApplication.processEvents()

        # Create a custom event loop
        loop = QEventLoop()

        # Use QTimer to give a slight delay to ensure UI renders completely
        QTimer.singleShot(100, loop.quit)  # 100 ms delay to ensure the dialog shows
        loop.exec_()  # This will block until `loop.quit()` is called

    def import_button_clicked(self):
        # Show confirmation dialog
        reply = QMessageBox.question(
            self,
            "Confirm Overwrite",
            "About to OVERWRITE All Current Json Data! Continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        # If user chooses 'Yes', proceed to paste from clipboard
        if reply == QMessageBox.Yes:
            clipboard = QApplication.clipboard()
            clipboard_text = clipboard.text()
            if clipboard_text:
                self.start_model_load_indicators()
                result = self.view.set_text(clipboard_text)
                self.stop_model_load_indicators()

                if(result):
                    QMessageBox.information(self, "Pasted", "Json Data Imported from clipboard!")
                else:
                    #if we got here, the set_text above already threw an error dialog. Just do nothing more here.
                    pass

            else:
                QMessageBox.warning(self, "Clipboard Empty", "No data found in the clipboard!")

    def export_button_clicked(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.view.get_text())
        QMessageBox.information(self, "Copied", "Json Data copied to clipboard!")

    def on_loading_complete(self, model):
        # Close the dialog and set the model once loading is complete
        self.thinking_dialog.close()
        self.model = model

    def start_model_load_indicators(self):
        # need to set them all since we are in a main level context:
        self.tab1.update_tree_synced_indicator(False)
        self.tab2.update_tree_synced_indicator(False)
        self.tab3.update_tree_synced_indicator(False)
        self.background_processing_signal.emit(4, "tab1")
        self.start_thinking_window()

    def stop_model_load_indicators(self):
        self.tab1.update_tree_synced_indicator(True)
        self.tab2.update_tree_synced_indicator(True)
        self.tab3.update_tree_synced_indicator(True)
        self.thinking_dialog.close()

    def create_menu_bar(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu('File')

        open_action = QAction('Open', self)
        save_action = QAction('Save', self)
        save_as_action = QAction('Save As', self)
        
        open_action.triggered.connect(self.open_file)
        save_action.triggered.connect(self.save_file)
        save_as_action.triggered.connect(self.save_file_as)
        
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(save_as_action)
                
        self.help_menu = NMSHelpMenu(self)  # Create an instance of the HelpMenu
        self.help_menu.create_help_menu(menu_bar)  # Add the Help menu to the menu bar
                
    def open_file(self):
        result = self.ini_file_manager.open_file()

        if(result):
            self.start_model_load_indicators()
            self.model.set_data(self.model.json_loads_with_exception_check(result))
            self.stop_model_load_indicators()

    def save_file(self):
        active_tab = self.tabs.currentWidget()
        if not active_tab.tree_synced:
            active_tab.sync_tree_from_text_window()

        self.ini_file_manager.save_file(self.view.get_text())
        
    def save_file_as(self):
        active_tab = self.tabs.currentWidget()
        if not active_tab.tree_synced:
            active_tab.sync_tree_from_text_window()
        
        self.ini_file_manager.save_file_as(self.view.get_text())

    def before_tab_change(self, index):
        logger.debug(f"before_tab_changed() enter, index: {index}")
        self.tab1.blockSignals() 
        self.tab2.blockSignals()
        self.tab3.blockSignals()

        logger.debug("before_tab_changed() exit")

    def after_tab_change(self, index):
        logger.debug(f"after_tab_changed() enter, index: {index}")
        self.tab1.unblockSignals() 
        self.tab2.unblockSignals()
        self.tab3.unblockSignals()

        logger.debug("after_tab_changed() exit")        
        
    def update_tabs_from_model(self):
        self.tab1.update_text_widget_from_model()
        self.tab2.update_text_widget_from_model()
        self.tab3.update_text_widget_from_model()

def main():
    app = QApplication(sys.argv)
    logger.debug("main enter")
    main_window = MainWindow()
    main_window.show()

    QApplication.processEvents()
    logger.debug("main exit")
    
    return app.exec_()

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)  # Ensure the program terminates correctly


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
    
   
    
    
    
