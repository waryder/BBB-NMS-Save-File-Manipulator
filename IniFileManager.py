from imports import *

class IniFileManager:
    def __init__(self, ini_file=None):
        """
        Initializes the IniFileManager class.
        :param ini_file: The path to the .ini file.
        """
        INI_FILE_NAME = "app_preferences.ini"
        self.ensure_persistent_file(INI_FILE_NAME)
        self.ini_file = os.path.join(self.get_persistent_dir(), INI_FILE_NAME)

        self.config = configparser.ConfigParser(delimiters='=')
        self.config.read(self.ini_file, encoding='utf-8')

        # Initialize the working file path from the ini file if it exists
        # self.tab1_working_file_path = self.config.get('Preferences', 'tab1_working_file_path', fallback='')
        # self.tab2_working_file_path = self.config.get('Preferences', 'tab2_working_file_path', fallback='')
        self.last_file_path = False
        
    # def store_current_tab1_working_file_path(self, file_path):
    #     """
    #     Stores the given file path in the ini file.
    #     :param file_path: The full path of the working file to store.
    #     """
    #     if 'Preferences' not in self.config:
    #         self.config['Preferences'] = {}
    #
    #     self.config['Preferences']['tab1_working_file_path'] = file_path
    #     with open(self.ini_file, 'w') as configfile:
    #         self.config.write(configfile)
    #     self.working_file_path = file_path
    #
    # def store_current_tab2_working_file_path(self, file_path):
    #     """
    #     Stores the given file path in the ini file.
    #     :param file_path: The full path of the working file to store.
    #     """
    #     if 'Preferences' not in self.config:
    #         self.config['Preferences'] = {}
    #
    #     self.config['Preferences']['tab2_working_file_path'] = file_path
    #     with open(self.ini_file, 'w') as configfile:
    #         self.config.write(configfile)
    #     self.working_file_path = file_path

    # def get_last_tab1_working_file_path(self):
    #     """
    #     Retrieves the last stored working file path from the ini file.
    #     :return: The last working file path or an empty string if not found.
    #     """
    #     return self.tab1_working_file_path
    #
    # def get_last_tab2_working_file_path(self):
    #     """
    #     Retrieves the last stored working file path from the ini file.
    #     :return: The last working file path or an empty string if not found.
    #     """
    #     return self.tab2_working_file_path

    def init_configfile_inventory_sorter_defaults(
            self,
            source_checkboxes,
            target_checkboxes,
            target_combo_boxes):

        for key, checkbox in source_checkboxes.items():


            # print(f"\n\nSource checkbox label:\n{key}_source_checkbox\n\n")
            #
            # print("Keys in Preferences section:")
            # for k in self.config['Preferences'].keys():
            #     print(repr(k))
            #
            # print("\n\n")

            # Check if the key is already stored in the INI
            if f"{key}_source_checkbox" not in self.config['Preferences'].keys():
                # Save the current state (checked/unchecked) of the checkbox
                #if "Exosuit" in f"{key}_source_checkbox":
                    # print(f"AAAAA {key}_source_checkbox")
                
                self.config['Preferences'][f"{key}_source_checkbox"] = str(checkbox.isChecked())

        for key, checkbox in target_checkboxes.items():
            # Check if the key is already stored in the INI
            if f"{key}_target_checkbox" not in self.config['Preferences']:
                # Save the current state (checked/unchecked) of the checkbox
                self.config['Preferences'][f"{key}_target_checkbox"] = str(checkbox.isChecked())

        for key, combobox in target_combo_boxes.items():
            #Check if the key is already stored in the INI
            if f"{key}_target_combobox" not in self.config['Preferences']:
                # Save the current state (checked/unchecked) of the checkbox
                self.config['Preferences'][f"{key}_target_combobox"] = combobox.lineEdit().text()


        #print("init_configfile_inventory_sorter_defaults(): writing to config file")
        #print("".join(traceback.format_stack()))

        with open(self.ini_file, 'w', encoding='utf-8') as configfile:
            self.config.write(configfile)

    def store_configfile_inventory_sorter_defaults(
        self,
        source_checkboxes,
        target_checkboxes,
        target_combo_boxes):

        #make sure all values have been initialized:
        self.init_configfile_inventory_sorter_defaults(
            source_checkboxes,
            target_checkboxes,
            target_combo_boxes)

        for key, checkbox in source_checkboxes.items():
            if "exosuit" in f"{key}_source_checkbox":
                print(f"BBBBB {key}_source_checkbox")


            self.config['Preferences'][f"{key}_source_checkbox"] = str(checkbox.isChecked())

        for key, checkbox in target_checkboxes.items():
            self.config['Preferences'][f"{key}_target_checkbox"] = str(checkbox.isChecked())

        for key, combobox in target_combo_boxes.items():
            self.config['Preferences'][f"{key}_target_combobox"] = combobox.lineEdit().text()

        print("store_configfile_inventory_sorter_defaults(): writing to config file")
        with open(self.ini_file, 'w', encoding='utf-8') as configfile:
            self.config.write(configfile)

    def apply_inventory_sorter_defaults_to_checkboxes(
            self,
            source_checkboxes,
            target_checkboxes,
            target_combo_boxes):

        #make sure all values have been initialized
        #we don't really need this here since we have fallbacks, but I just
        #want to make sure at every opportunity the ini file has what
        #it should in it in case an end user has messed with it:
        self.init_configfile_inventory_sorter_defaults(
            source_checkboxes,
            target_checkboxes,
            target_combo_boxes)

        for key, checkbox in source_checkboxes.items():
            checkbox.setChecked(self.config.getboolean('Preferences', f"{key}_source_checkbox", fallback='False'))

        for key, checkbox in target_checkboxes.items():
            checkbox.setChecked(self.config.getboolean('Preferences', f"{key}_target_checkbox", fallback='False'))

        for key, combobox in target_combo_boxes.items():
            combobox.setCheckedItemsFromText(self.config.get('Preferences', f"{key}_target_combobox", fallback='Product (Crafted or Special Items)'))

        # with open(self.ini_file, 'w') as configfile:
        #     self.config.write(configfile)

    # def get_last_tab1_working_file_directory(self):
    #     """
    #     Retrieves the directory of the last stored working file path.
    #     :return: The directory of the working file, or an empty string if the path is not set.
    #     """
    #     if self.tab1_working_file_path:
    #         return os.path.dirname(self.tab1_working_file_path)
    #     return ''
    #
    # def get_last_tab2_working_file_directory(self):
    #     """
    #     Retrieves the directory of the last stored working file path.
    #     :return: The directory of the working file, or an empty string if the path is not set.
    #     """
    #     if self.tab2_working_file_path:
    #         return os.path.dirname(self.tab2_working_file_path)
    #     return ''

    # def get_last_tab1_working_file_name(self):
    #     """
    #     Retrieves the file name of the last stored working file path.
    #     :return: The file name of the working file, or an empty string if the path is not set.
    #     """
    #     if self.tab1_working_file_path:
    #         return os.path.basename(self.tab1_working_file_path)
    #     return ''
    #
    # def get_last_tab2_working_file_name(self):
    #     """
    #     Retrieves the file name of the last stored working file path.
    #     :return: The file name of the working file, or an empty string if the path is not set.
    #     """
    #     if self.tab2_working_file_path:
    #         return os.path.basename(self.tab2_working_file_path)
    #     return ''

    def open_file(self):
        options = QFileDialog.Options()
        initial_directory = self.get_persistent_dir()

        # Open file dialog starting from the last working directory
        file_name, _ = QFileDialog.getOpenFileName(
            QApplication.instance().activeWindow(),
            "Open File",
            f"{initial_directory}/*.nms_sfm_BaseContext.json",  # Set the initial directory with the default file name
            "JSON Files (*.json);;All Files (*)",
            options=options
        )

        output = ""
        if file_name:
            try:
                # Try opening the file with UTF-8 encoding
                with open(file_name, 'r', encoding='utf-8') as file:
                    output = file.read()
            except UnicodeDecodeError:
                # If UTF-8 fails, fall back to CP1252
                try:
                    with open(file_name, 'r', encoding='cp1252') as file:
                        output = file.read()
                except Exception as e:
                    QMessageBox.critical(QApplication.instance().activeWindow(), "Error", f"Failed to open file: {e}")
                    output = None
            except Exception as e:
                QMessageBox.critical(QApplication.instance().activeWindow(), "Error", f"Failed to open file: {e}")
                output = None
        else:
            QMessageBox.critical(QApplication.instance().activeWindow(), "Error", f"No File Selected!")

        self.last_file_path = file_name
        return output

    def save_file(self, tab, data):
        """Saves the file using the last saved path, or prompts if no path is set."""
        # Get the last working file path from the ini manager
        last_file_path = self.last_file_path

        if last_file_path and os.path.exists(last_file_path):
            # If there's a valid path, save directly
            try:
                with open(last_file_path, 'w') as f:
                    f.write(data)

                # Show a confirmation message
                QMessageBox.information(QApplication.instance().activeWindow(), 'File Saved', f'File saved at: {last_file_path}')
            except Exception as e:
                QMessageBox.critical(QApplication.instance().activeWindow(), "Error", f"Failed to save file: {e}")
        else:
            # If no path is set or the file doesn't exist, use "Save As" behavior
            self.save_file_as(tab, data)  # Fallback to "Save As" behavior if no previous file path

    def save_file_as(self, data):
        """Implements the Save As functionality allowing the user to specify a file location."""
        # Get the preferences from the ini manager for the default save path
        last_working_path = self.get_persistent_dir()

        save_file_name, _ = QFileDialog.getSaveFileName(
            QApplication.instance().activeWindow(),
            'Save As',
            f"{last_working_path}/default.nms_sfm_BaseContext.json",  # Set the initial directory with default file name
            "JSON Files (*.json);;All Files (*)"  # File filters
        )

        if save_file_name:
            try:
                # Save the file content
                with open(save_file_name, 'w') as f:
                    f.write(data)

                self.last_file_path = save_file_name

                # Show a confirmation message
                QMessageBox.information(QApplication.instance().activeWindow(), 'File Saved As', f'File saved at: {save_file_name}')

                # Store the file path in the ini manager after saving
                # if tab == "tab1":
                #     self.store_current_tab1_working_file_path(save_file_name[0])
                # elif tab == "tab2":
                #     self.store_current_tab2_working_file_path(save_file_name[0])
            
            except Exception as e:
                QMessageBox.critical(QApplication.instance().activeWindow(), "Error", f"Failed to save file: {e}")

    def get_persistent_dir(self):
        """Get the persistent directory based on the OS."""
        if sys.platform == "win32":
            return os.path.join(os.getenv("APPDATA"), APP_NAME)
        elif sys.platform == "darwin":
            return os.path.join(os.path.expanduser("~"), "Library", "Application Support", APP_NAME)
        else:
            return os.path.join(os.path.expanduser("~"), f".{APP_NAME}")

    def ensure_persistent_file(self, filename):
        """Ensure the data file is copied to a persistent directory."""
        persistent_dir = self.get_persistent_dir()
        if not os.path.exists(persistent_dir):
            os.makedirs(persistent_dir)

        persistent_file = os.path.join(persistent_dir, filename)

        # Determine source file
        if hasattr(sys, "_MEIPASS"):
            source_file = os.path.join(sys._MEIPASS, filename)
        else:
            source_file = os.path.join(os.path.dirname(__file__), filename)

        # Copy file if it doesn't exist
        if not os.path.exists(persistent_file):
            shutil.copy(source_file, persistent_file)

        return persistent_file

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