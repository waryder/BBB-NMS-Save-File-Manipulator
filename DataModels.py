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
    modelChanged = pyqtSignal()

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
            new_model_data = json_loads_with_exception_check(self.INIT_TEXT)

            if not new_model_data:
                sys.exit(1)

            self.set_data(new_model_data)
        else:
            print("self.INIT_TEXT empty")

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

        """
        traceback.print_stack()
        
        print("####################")
        print(f"json_array is of type: {type(json_array)}")
        print(f"The size of the variable is: {sys.getsizeof(json_array)} bytes")
        #if isinstance(json_array, list):
        print(f"The number of items in the list is: {len(json_array)}")
        print("####################")
        """

        DataModel.model_data = json_array

        self.modelChanged.emit()
        logger.debug("set_data() EXIT")


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