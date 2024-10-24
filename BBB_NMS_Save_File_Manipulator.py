import sys, os

# needed so that after formal install, python can find all the files:
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from imports import *

from NMSHelpMenu import NMSHelpMenu  
from FirstTabContent import FirstTabContent
from SecondTabContent import SecondTabContent
from IniFileManager import *

def global_exception_handler(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        # Let KeyboardInterrupt exceptions pass through without logging
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return        
    
    # Print the error and traceback
    print(f"Unhandled exception: {exc_value}")
    traceback.print_exception(exc_type, exc_value, exc_traceback)
    
# Set the global exception handler
sys.excepthook = global_exception_handler 


class MainWindow(QMainWindow):    
    background_processing_signal = pyqtSignal(int, str)    
    def __init__(self):
        logger.debug("MainWindow(QMainWindow).__init__ ENTER")
        self.ini_file_manager = ini_file_manager 
        super().__init__()
        
        #self.ini_file_manager = ini_file_manager #global
        
        self.tabs = QTabWidget()

        self.tab1 = FirstTabContent(self)
        self.tab2 = SecondTabContent(self)
        self.background_processing_signal.connect(self.tab1.set_led_based_on_app_thread_load)
        self.background_processing_signal.connect(self.tab2.set_led_based_on_app_thread_load)        

        self.tabs.addTab(self.tab1, 'Base Processing')
        self.tabs.addTab(self.tab2, 'Starship Processing')

        self.tabs.tabBarClicked.connect(self.before_tab_change)
        self.tabs.currentChanged.connect(self.after_tab_change)

        self.setCentralWidget(self.tabs)
        self.setWindowTitle('BBB NMS Save File Manipulator')
        self.setGeometry(400, 250, 1500, 800)

        self.create_menu_bar()
        
        self.background_processing_signal.emit(5, "Main Window")
        logger.debug("MainWindow(QMainWindow).__init__ EXIT")        

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
        active_tab = self.tabs.currentWidget()
        result = ""
        if active_tab == self.tab1:
            result = self.ini_file_manager.open_file("tab1")
        elif active_tab == self.tab2:
            result = self.ini_file_manager.open_file("tab2")
           
        active_tab.blockSignals()   
        active_tab.text_edit.setPlainText(result) 
        active_tab.sync_from_text_window()
        active_tab.unblockSignals()
        
    
    def save_file(self):
        active_tab = self.tabs.currentWidget()
        if not active_tab.tree_synced:
                active_tab.sync_from_text_window()
        
        if active_tab == self.tab1:
            self.ini_file_manager.save_file("tab1", self.tab1.model.get_text())
        elif active_tab == self.tab2:
            self.ini_file_manager.save_file("tab2", self.tab2.model.get_text())
        
    def save_file_as(self):
        active_tab = self.tabs.currentWidget()
        if not active_tab.tree_synced:
            active_tab.sync_from_text_window()
        
        if active_tab == self.tab1:
            self.ini_file_manager.save_file_as("tab1", self.tab1.model.get_text())
        elif active_tab == self.tab2:
            self.ini_file_manager.save_file_as("tab2", self.tab2.model.get_text())

    """
    def open_file(self):
        options = QFileDialog.Options()
        
        # Get the last working directory from the ini manager
        initial_directory = self.ini_file_manager.get_last_working_file_directory() or os.getcwd()
        
        # Open file dialog starting from the last working directory
        file_name, _ = QFileDialog.getOpenFileName(self, 
                                                   "Open File", 
                                                   initial_directory,  # Set the initial directory
                                                   "JSON Files (*.json);;All Files (*)", 
                                                   options=options)
        
        if file_name:
            try:
                # Open the selected file and read its contents
                with open(file_name, 'r') as file:
                    self.model.set_text(file.read())
                    self.update_tabs_from_model()

                # Store the new file path in the ini manager
                self.ini_file_manager.store_current_working_file_path(file_name)
            
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open file: {e}")
                
    def save_file(self):
        #Saves the file using the last saved path, or prompts if no path is set.
        # Get the last working file path from the ini manager
        last_file_path = self.ini_file_manager.get_last_working_file_path()
        
        if last_file_path and os.path.exists(last_file_path):
            # If there's a valid path, save directly
            try:
                with open(last_file_path, 'w') as f:
                    f.write(self.model.get_text())

                # Show a confirmation message
                QMessageBox.information(self, 'File Saved', f'File saved at: {last_file_path}')
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {e}")
        else:
            # If no path is set or the file doesn't exist, use "Save As" behavior
            self.save_file_as()  # Fallback to "Save As" behavior if no previous file path


    def save_file_as(self):
        #Implements the Save As functionality allowing the user to specify a file location.
        # Get the preferences from the ini manager for the default save path
        save_file_name = QFileDialog.getSaveFileName(
            self, 'Save As', 
            self.ini_file_manager.get_last_working_file_path()
        )

        if save_file_name[0]:
            try:
                # Save the file content
                with open(save_file_name[0], 'w') as f:
                    f.write(self.model.get_text())

                # Show a confirmation message
                QMessageBox.information(self, 'File Saved As', f'File saved at: {save_file_name[0]}')

                # Store the file path in the ini manager after saving
                self.ini_file_manager.store_current_working_file_path(save_file_name[0])
            
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {e}")
    """

    def before_tab_change(self, index):
        logger.debug(f"before_tab_changed() enter, index: {index}")
        self.tab1.blockSignals() 
        self.tab2.blockSignals()
        logger.debug("before_tab_changed() exit")

    def after_tab_change(self, index):
        logger.debug(f"after_tab_changed() enter, index: {index}")
        self.tab1.unblockSignals() 
        self.tab2.unblockSignals()
        logger.debug("after_tab_changed() exit")        
        
    def update_tabs_from_model(self):
        self.tab1.update_text_widget_from_model()
        self.tab2.update_text_widget_from_model()
        
    #def closeEvent(self, event):
    #    """Handle app close event and stop Yappi profiling."""
    #    yappi.stop()
    #    print("Application closed. Printing Yappi profiling stats...")
    #    yappi.get_func_stats().print_all()
    #    yappi.get_thread_stats().print_all()
    #    event.accept()  # Proceed with closing the window    
        
 
def main():
    init_galaxies()
    logger.debug("main enter")
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    logger.debug("main exit")
    
    return app.exec_()
    

if __name__ == '__main__':
    #yappi.start() 
    
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
    
   
    
    
    
