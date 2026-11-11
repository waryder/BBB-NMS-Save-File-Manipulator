from imports import *
from IniFileManager import *
from pympler import asizeof

global INIT_BASE_TEXT
global INIT_STARSHIP_TEXT

# Parent Class: DataModel
class DataModel(QObject):
    model_data = None

    # Define the signal to be emitted when text changes (can be inherited)
    # (Dude I don't know. Python wants this out here even though it is treated like an instance variable
    # when declared this way. ChatGPT couldn't explain it to me. Just know: this thing is treated like
    # an instance variable for the life of the app:
    modelChanged = pyqtSignal(object)

    def __init__(self):
        logger.debug("DataModel(QObject).__init__ ENTER")
        super().__init__()

        logger.debug("DataModel(QObject).__init__ EXIT")

    # Accessor stubs
    def get_data(self):
        raise NotImplementedError("Subclasses must implement 'get_data'")

    def set_data(self, json_array):
        raise NotImplementedError("Subclasses must implement 'set_data'")

class JsonArrayModel(DataModel):
    def __init__(self, model_context = 'main', INIT_TEXT = None):
        logger.debug("JsonArrayModel(DataModel).__init__ ENTER")

        #should come in 'main', 'tab1', 'tab2', 'tab3' ...
        self.model_context = model_context

        self.INIT_TEXT=INIT_TEXT
        super().__init__()

        #leave blank for now at start. Wait for user to load something:
        self.init_model_data()
        logger.debug("JsonArrayModel(DataModel).__init__ EXIT")
        
    def init_model_data(self):
        logger.debug("init_model_data() ENTER")

        # Fall back to INIT_TEXT if no file path is found or the file doesn't exist
        if(self.INIT_TEXT):
            new_model_data = self.json_loads_with_exception_check(self.INIT_TEXT)

            if not new_model_data:
                sys.exit(1)

            self.set_data(new_model_data)
        else:
            pass

        #print(f"model_context: {self.model_context}, Size of data: {asizeof.asizeof(self.model_data)}")

        logger.debug("init_model_data() EXIT")

    def get_data(self):
        logger.debug("get_json() ENTER")

        if not DataModel.model_data:
            return None

        return DataModel.model_data

        logger.debug("get_json() EXIT")

    def set_data(self, json_array):
        logger.debug("set_data() ENTER")

        # traceback.print_stack()
        #
        # print("####################")
        # print(f"json_array is of type: {type(json_array)}")
        # print(f"The size of the variable is: {sys.getsizeof(json_array)} bytes")
        # #if isinstance(json_array, list):
        # print(f"The number of items in the list is: {len(json_array)}")
        # print("####################")

        DataModel.model_data = json_array

        self.modelChanged.emit(None)
        logger.debug("set_data() EXIT")

    def json_loads_with_exception_check(self, text):
        try:
            json_array = json.loads(text)
        except Exception as e:
            QMessageBox.critical(
                None,  # No parent for the dialog
                "Error",  # Title of the dialog
                f"Text Input was not valid JSON data. Data Load failed and has been aborted. Check your data format and try again! ({str(e)})"
                # Message to display
            )

            return False
        return json_array


"""
def _getInventoryIds():
    return [
        "Inventory",  # Exosuit, I think
        "FreighterInventory",
        "ShipOwnership",
        "VehicleOwnership",
        "FishBaitBoxInventory",
        "CookingIngredientsInventory",
        "Chest1Inventory",
        "Chest2Inventory",
        "Chest3Inventory",
        "Chest4Inventory",
        "Chest5Inventory",
        "Chest6Inventory",
        "Chest7Inventory",
        "Chest8Inventory",
        "Chest9Inventory",
        "Chest10Inventory"
    ]
"""


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
