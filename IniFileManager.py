from imports import *
# Temporary sibling files allow atomic preference updates without truncating the original.
import tempfile
import AppPersistentStorage as storage  # Share the startup-selected application data tree.

class IniFileManager:
    def __init__(self, ini_file=None):
        """
        Initializes the IniFileManager class.
        :param ini_file: The path to the .ini file.
        """
        self.ini_file = None  # Delay filesystem access until Qt and persistent storage are ready.

        self.config = configparser.ConfigParser(delimiters='=')


        # Initialize the working file path from the ini file if it exists
        # self.tab1_working_file_path = self.config.get('Preferences', 'tab1_working_file_path', fallback='')
        # self.tab2_working_file_path = self.config.get('Preferences', 'tab2_working_file_path', fallback='')
        self.last_file_path = False

    # initialize: Load the selected-tree preferences, seeding only a missing file.
    def initialize(self):
        self.ini_file = self.ensure_persistent_file('app_preferences.ini')  # Preserve migrated settings.
        self.config.read(self.ini_file, encoding='utf-8')  # Never fall back to an old data root.

    # get_nms_save_folder
    # Returns the remembered NMS folder, with an empty fallback for older preferences.
    def get_nms_save_folder(self):
        # Use normal interpolation to decode escaped literal percent signs in paths.
        return self.config.get('Preferences', 'nms_save_folder', fallback='')

    # store_nms_save_folder
    # Atomically persists a folder while preserving other preferences and failed-write state.
    def store_nms_save_folder(self, folder):
        # Stage changes separately so a failed write does not alter the shared config.
        updated = copy.deepcopy(self.config)
        # Older or user-edited preference files may have no Preferences section.
        if not updated.has_section('Preferences'):
            updated.add_section('Preferences')
        # ConfigParser requires literal percent signs to be escaped on assignment.
        updated.set('Preferences', 'nms_save_folder', folder.replace('%', '%%'))
        # Write and replace beside the original, on the same filesystem.
        self._write_nms_preferences(updated)
        # Publish the new in-memory state only after the file replacement succeeds.
        self.config = updated

    # get_inventory_organizer_settings: Read organizer JSON without touching legacy settings.
    def get_inventory_organizer_settings(self):
        try:
            value = self.config.get('InventoryOrganizer', 'settings', fallback='{}', raw=True)
            return json.loads(value)
        except (ValueError, TypeError, configparser.Error):
            return {}  # Individual malformed fields also receive safe dialog defaults.

    # store_inventory_organizer_settings: Atomically stage this dedicated section only.
    def store_inventory_organizer_settings(self, settings):
        updated = copy.deepcopy(self.config)  # Preserve the singleton on failed writes.
        if not updated.has_section('InventoryOrganizer'):
            updated.add_section('InventoryOrganizer')
        updated.set('InventoryOrganizer', 'settings', json.dumps(settings, ensure_ascii=True))
        self._write_nms_preferences(updated)  # Existing atomic sibling replacement.
        self.config = updated  # Publish only after successful replacement.

    # _write_nms_preferences
    # Writes a complete staged config through a temporary sibling, cleaning up on failure.
    def _write_nms_preferences(self, updated):
        if self.ini_file is None:  # Refuse preferences writes before startup selected and initialized storage.
            raise RuntimeError('Application preferences have not been initialized.')
        # Track the temporary filename for cleanup even if writing fails.
        temporary_path = None
        # Keep the existing preference file intact until the replacement is ready.
        try:
            # Close the temporary handle before replacing a file on Windows.
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8',
                    dir=os.path.dirname(self.ini_file), suffix='.tmp', delete=False) as handle:
                # Remember the sibling file before writing its contents.
                temporary_path = handle.name
                # Preserve all current preference sections and keys.
                updated.write(handle)
                # Flush buffered bytes before the atomic replacement.
                handle.flush()
                os.fsync(handle.fileno())
            # Replace the original only after the full file was successfully closed.
            os.replace(temporary_path, self.ini_file)
        finally:
            # Remove an uncommitted sibling without touching the original preferences.
            if temporary_path and os.path.exists(temporary_path):
                os.unlink(temporary_path)

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

    # get_hide_startup_disclaimer: Show the warning by default, including malformed preferences.
    def get_hide_startup_disclaimer(self):
        try:  # Invalid stored booleans must not silently suppress the warning.
            return self.config.getboolean('Preferences', 'hide_startup_disclaimer', fallback=False)
        except (ValueError, configparser.Error):
            return False  # Recover with a visible disclaimer instead of failing startup.

    # store_hide_startup_disclaimer: Persist only the disclaimer choice through atomic replacement.
    def store_hide_startup_disclaimer(self, hidden):
        updated = copy.deepcopy(self.config)  # Preserve unrelated preferences and failed-write state.
        if not updated.has_section('Preferences'):  # Support older or manually edited preference files.
            updated.add_section('Preferences')
        updated.set('Preferences', 'hide_startup_disclaimer', str(bool(hidden)))  # Store a valid boolean.
        self._write_nms_preferences(updated)  # Reuse the existing atomic sibling-file writer.
        self.config = updated  # Publish only after successful persistence.

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
        initial_directory = str(storage.data_path('Backups', 'Contexts'))

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
            except Exception as e:
                QMessageBox.critical(QApplication.instance().activeWindow(), "Error", f"Failed to open file: {e}")
                output = None
        else:
            QMessageBox.critical(QApplication.instance().activeWindow(), "Error", f"No File Selected!")

        self.last_file_path = file_name
        return output

    def save_file(self, data):
        """Saves the file using the last saved path, or prompts if no path is set."""
        # Get the last working file path from the ini manager
        last_file_path = self.last_file_path

        if last_file_path and os.path.exists(last_file_path):
            # If there's a valid path, save directly
            try:
                with open(last_file_path, 'w', encoding='utf-8') as f:
                    f.write(data)

                # Show a confirmation message
                QMessageBox.information(QApplication.instance().activeWindow(), 'File Saved', f'File saved at: {last_file_path}')
            except Exception as e:
                QMessageBox.critical(QApplication.instance().activeWindow(), "Error", f"Failed to save file: {e}")
        else:
            # If no path is set or the file doesn't exist, use "Save As" behavior
            self.save_file_as(data)  # Fallback to "Save As" behavior if no previous file path

    def save_file_as(self, data):
        """Implements the Save As functionality allowing the user to specify a file location."""
        # Get the preferences from the ini manager for the default save path
        default_file_name = self.get_full_file_path("default.nms_sfm_BaseContext.json")

        save_file_name, _ = QFileDialog.getSaveFileName(
            QApplication.instance().activeWindow(),
            'Save As',
            default_file_name,  # Set the initial directory with default file name
            "JSON Files (*.json);;All Files (*)"  # File filters
        )

        if save_file_name:
            try:
                # Save the file content
                with open(save_file_name, 'w', encoding='utf-8') as f:
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
        return str(storage.data_path())  # No environment-based guessing after startup selection.

    def ensure_persistent_file(self, filename):
        if os.path.basename(filename) != filename:  # Reject resource path traversal.
            raise ValueError('Expected a plain persistent resource filename.')
        category = 'Settings' if filename == 'app_preferences.ini' else 'Reference Data'
        persistent_file = storage.data_path(category, filename)  # Resource copies are not user backups.
        source_root = getattr(sys, '_MEIPASS', os.path.dirname(__file__))  # Bundled resources remain read-only.
        if not persistent_file.exists():  # Never overwrite migrated preferences or copied references.
            shutil.copy(os.path.join(source_root, filename), persistent_file)
        return str(persistent_file)  # Let startup report failures rather than silently continue.

    # get_starship_upgrade_reference_path: Resolve current donors using the existing source/frozen bundle roots.
    def get_starship_upgrade_reference_path(self, filename):
        # Accept only a plain reference filename, never a caller-controlled path.
        if os.path.basename(filename) != filename or not filename.startswith('reference_') or not filename.endswith('.json'):
            raise ValueError('Invalid starship upgrade reference filename.')
        # Reuse the same frozen/source root decision as ensure_persistent_file without copying stale legacy donors.
        source_root = getattr(sys, '_MEIPASS', os.path.dirname(__file__))
        # The dedicated bundle contains the current eleven approved references; runtime access is read-only.
        return os.path.join(source_root, 'starship_upgrade_references', filename)

    def get_full_file_path(self, file_name):
        category = ('Settings',) if file_name == 'app_preferences.ini' else ('Backups', 'Contexts')
        return str(storage.data_path(*category, file_name))  # Legacy JSON output defaults to Contexts.

ini_file_manager = IniFileManager('app_preferences.ini')


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
