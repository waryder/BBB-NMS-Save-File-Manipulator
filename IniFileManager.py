from imports import *

class IniFileManager:
    def __init__(self, ini_file=None):
        """
        Initializes the IniFileManager class.
        :param ini_file: The path to the .ini file.
        """
        # Set the ini file path to be in the same directory as the script
        self.ini_file = os.path.join(os.path.dirname(__file__), ini_file)
        self.config = configparser.ConfigParser()
        
        #config = configparser.ConfigParser(allow_no_value=True)

        # Check if ini file exists, if not create a new one
        if os.path.exists(self.ini_file):
            self.config.read(self.ini_file)
        else:
            self.create_empty_ini_file()

        # Initialize the working file path from the ini file if it exists
        self.tab1_working_file_path = self.config.get('Preferences', 'tab1_working_file_path', fallback='')
        self.tab2_working_file_path = self.config.get('Preferences', 'tab2_working_file_path', fallback='')        
        

    def create_empty_ini_file(self):
        """Creates an empty ini file if it doesn't exist."""
        self.config['Preferences'] = {'tab1_working_file_path': ''}
        self.config['Preferences'] = {'tab2_working_file_path': ''}
        with open(self.ini_file, 'w') as configfile:
            self.config.write(configfile)

    def store_current_tab1_working_file_path(self, file_path):
        """
        Stores the given file path in the ini file.
        :param file_path: The full path of the working file to store.
        """
        if 'Preferences' not in self.config:
            self.config['Preferences'] = {}
        
        self.config['Preferences']['tab1_working_file_path'] = file_path
        with open(self.ini_file, 'w') as configfile:
            self.config.write(configfile)
        self.working_file_path = file_path
        
    def store_current_tab2_working_file_path(self, file_path):
        """
        Stores the given file path in the ini file.
        :param file_path: The full path of the working file to store.
        """
        if 'Preferences' not in self.config:
            self.config['Preferences'] = {}
        
        self.config['Preferences']['tab2_working_file_path'] = file_path
        with open(self.ini_file, 'w') as configfile:
            self.config.write(configfile)
        self.working_file_path = file_path        

    def get_last_tab1_working_file_path(self):
        """
        Retrieves the last stored working file path from the ini file.
        :return: The last working file path or an empty string if not found.
        """
        return self.tab1_working_file_path
        
    def get_last_tab2_working_file_path(self):
        """
        Retrieves the last stored working file path from the ini file.
        :return: The last working file path or an empty string if not found.
        """
        return self.tab2_working_file_path        

    def get_last_tab1_working_file_directory(self):
        """
        Retrieves the directory of the last stored working file path.
        :return: The directory of the working file, or an empty string if the path is not set.
        """
        if self.tab1_working_file_path:
            return os.path.dirname(self.tab1_working_file_path)
        return ''
        
    def get_last_tab2_working_file_directory(self):
        """
        Retrieves the directory of the last stored working file path.
        :return: The directory of the working file, or an empty string if the path is not set.
        """
        if self.tab2_working_file_path:
            return os.path.dirname(self.tab2_working_file_path)
        return ''        

    def get_last_tab1_working_file_name(self):
        """
        Retrieves the file name of the last stored working file path.
        :return: The file name of the working file, or an empty string if the path is not set.
        """
        if self.tab1_working_file_path:
            return os.path.basename(self.tab1_working_file_path)
        return ''
        
    def get_last_tab2_working_file_name(self):
        """
        Retrieves the file name of the last stored working file path.
        :return: The file name of the working file, or an empty string if the path is not set.
        """
        if self.tab2_working_file_path:
            return os.path.basename(self.tab2_working_file_path)
        return ''    

    def open_file(self, tab):
        options = QFileDialog.Options()
        
        initial_directory = ""
        # Get the last working directory from the ini manager
        if tab == "tab1":
            initial_directory = self.get_last_tab1_working_file_directory() or os.getcwd()
        elif tab == "tab2":
            initial_directory = self.get_last_tab2_working_file_directory() or os.getcwd()
        
        # Open file dialog starting from the last working directory
        file_name, _ = QFileDialog.getOpenFileName(QApplication.instance().activeWindow(), 
                                                   "Open File", 
                                                   initial_directory,  # Set the initial directory
                                                   "JSON Files (*.json);;All Files (*)", 
                                                   options=options)
        
        output = ""
        if file_name:
            try:
                # Open the selected file and read its contents
                with open(file_name, 'r') as file:
                    output = file.read()
                    #self.model.set_text(file.read())
                    #self.update_tabs_from_model()

                # Store the new file path in the ini manager
                if tab == "tab1":
                    self.store_current_tab1_working_file_path(file_name)
                elif tab == "tab2":
                    self.store_current_tab2_working_file_path(file_name)
                #self.ini_file_manager.store_current_working_file_path(file_name)
                
            except Exception as e:
                QMessageBox.critical(QApplication.instance().activeWindow(), "Error", f"Failed to open file: {e}")
        
        return output        
                

    def save_file(self, tab, data):
        """Saves the file using the last saved path, or prompts if no path is set."""
        # Get the last working file path from the ini manager
        last_file_path = ""
        if tab == "tab1":
            last_file_path = self.get_last_tab1_working_file_path()
        elif tab == "tab2":
            last_file_path = self.get_last_tab2_working_file_path()
        #last_file_path = self.ini_file_manager.get_last_working_file_path()
        
        if last_file_path and os.path.exists(last_file_path):
            # If there's a valid path, save directly
            try:
                with open(last_file_path, 'w') as f:
                    f.write(data)
                    #f.write(self.model.get_text())

                # Show a confirmation message
                QMessageBox.information(QApplication.instance().activeWindow(), 'File Saved', f'File saved at: {last_file_path}')
            except Exception as e:
                QMessageBox.critical(QApplication.instance().activeWindow(), "Error", f"Failed to save file: {e}")
        else:
            # If no path is set or the file doesn't exist, use "Save As" behavior
            self.save_file_as(tab, data)  # Fallback to "Save As" behavior if no previous file path


    def save_file_as(self, tab, data):
        """Implements the Save As functionality allowing the user to specify a file location."""
        # Get the preferences from the ini manager for the default save path
        last_working_path = ""
        if tab == "tab1":
            last_working_path = self.get_last_tab1_working_file_path()
        elif tab == "tab2":
            last_working_path = self.get_last_tab2_working_file_path()
                
        save_file_name = QFileDialog.getSaveFileName(
            QApplication.instance().activeWindow(),
            'Save As', 
            last_working_path
        )

        if save_file_name[0]:
            try:
                # Save the file content
                with open(save_file_name[0], 'w') as f:
                    f.write(data)
                    #f.write(self.model.get_text())

                # Show a confirmation message
                QMessageBox.information(QApplication.instance().activeWindow(), 'File Saved As', f'File saved at: {save_file_name[0]}')

                # Store the file path in the ini manager after saving
                if tab == "tab1":
                    self.store_current_tab1_working_file_path(save_file_name[0])
                elif tab == "tab2":
                    self.store_current_tab2_working_file_path(save_file_name[0])
            
            except Exception as e:
                QMessageBox.critical(QApplication.instance().activeWindow(), "Error", f"Failed to save file: {e}") 

ini_file_manager = IniFileManager('app_preferences.ini')                

      
      
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