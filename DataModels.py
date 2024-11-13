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

    def __init__(self, last_working_file_path):
        logger.debug("DataModel(QObject).__init__ ENTER")
        super().__init__()

        self.last_file_path = last_working_file_path
        
        logger.debug("DataModel(QObject).__init__ EXIT")

    # Accessor stubs
    def init_model_data(self):
        raise NotImplementedError("Subclasses must implement 'get_text'")
    
    def get_text(self):
        raise NotImplementedError("Subclasses must implement 'get_text'")

    def set_text(self, text):
        raise NotImplementedError("Subclasses must implement 'set_text'")

    def get_json(self):
        raise NotImplementedError("Subclasses must implement 'get_json'")

    def set_json(self, json_array):
        raise NotImplementedError("Subclasses must implement 'set_json'")        
            

class JsonArrayModel(DataModel):
    def __init__(self, last_working_file_path, model_context = 'main', INIT_TEXT = None):
        logger.debug("JsonArrayModel(DataModel).__init__ ENTER")

        #should come in 'main', 'tab1', 'tab2', 'tab3' ...
        self.model_context = model_context

        self.INIT_TEXT=INIT_TEXT
        super().__init__(last_working_file_path)

        #leave blank for now at start. Wait for user to load something:
        self.init_model_data()
        logger.debug("JsonArrayModel(DataModel).__init__ EXIT")
        
    def init_model_data(self):
        logger.debug("init_model_data() ENTER")
        new_model_data = None
        
#for now we're going to just assume start with demo data:
#        if self.last_file_path and os.path.exists(self.last_file_path):
#            # If the file exists, load its contents
#            try:
#                with open(self.last_file_path, 'r') as file:
#                    new_model_data = json.loads(file.read())
#            except Exception as e:
#                print(f"Failed to load text from {self.last_file_path}: {e}")
#                new_model_data = json.loads(self.INIT_TEXT)
#        else:
            # Fall back to INIT_TEXT if no file path is found or the file doesn't exist
        if(self.INIT_TEXT):
            print("self.INIT_TEXT NOT empty")
            new_model_data = json.loads(self.INIT_TEXT)
            self.set_json(new_model_data)
        else:
            print("self.INIT_TEXT empty")

        print(f"model_context: {self.model_context}, Size of data: {asizeof.asizeof(self.model_data)}")

        logger.debug("init_model_data() EXIT")

    # Override the stubbed accessor functions
    def get_text(self):
        logger.debug("get_text() ENTER")

        if not DataModel.model_data:
            return ""

        return json.dumps(self.get_json(), indent=4)

    def set_text(self, text):
        logger.debug("set_text() ENTER")

        json_loads = json.loads(text)
        self.set_json(json_loads)
            
        logger.debug("set_text EXIT")    

    def get_json(self):
        logger.debug("get_json() ENTER")

        if not DataModel.model_data:
            return ""

        if (self.model_context == 'main'):
            return DataModel.model_data
        elif (self.model_context == 'tab1'):
            return DataModel.model_data["PlayerStateData"]["PersistentPlayerBases"]
        elif (self.model_context == 'tab2'):
            return DataModel.model_data["PlayerStateData"]["ShipOwnership"]
        elif (self.model_context == 'tab3'):
            containers = []
            for i in range(1, 11): #generates 1 - 10
                containers.append(DataModel.model_data["PlayerStateData"][f"Chest{i}Inventory"])

            #These seem to be unnamed. Let's give them a name just for display within the app here. We'll undo this on the way out:
            containers.append(DataModel.model_data["PlayerStateData"][f"CookingIngredientsInventory"])
            containers[10]['Name'] = 'Cooking Ingredients'
            containers.append(DataModel.model_data["PlayerStateData"][f"FishPlatformInventory"])
            containers[11]['Name'] = 'Fish Platform'

            return containers
        else:
            return #error

        logger.debug("get_json() EXIT")

    def set_json(self, json_array):
        logger.debug("set_json() ENTER")

        if (self.model_context == 'main'):
            DataModel.model_data = json_array

        elif (self.model_context == 'tab1'):
            DataModel.model_data["PlayerStateData"]["PersistentPlayerBases"] = json_array

        elif (self.model_context == 'tab2'):
            DataModel.model_data["PlayerStateData"]["ShipOwnership"] = json_array

        elif (self.model_context == 'tab3'):
            for i in range(1, 11):  # generates 1 - 10
                DataModel.model_data["PlayerStateData"][f"Chest{i}Inventory"] = json_array[i]

            # These seem to be unnamed. We gave them a name just for display within the app here.
            # We're undoing this on the way out now:
            DataModel.model_data["PlayerStateData"]["CookingIngredientsInventory"] = json_array[10]
            DataModel.model_data["PlayerStateData"]["CookingIngredientsInventory"]['Name'] = ""
            DataModel.model_data["PlayerStateData"]["FishPlatformInventory"] = json_array[11]
            DataModel.model_data["PlayerStateData"]["FishPlatformInventory"]['Name'] = ""

        DataModel.modelChanged.emit()
        logger.debug("set_json() EXIT")

    def add_base(self, nms_base_json_array):
        logger.debug("add_base() ENTER")

        # only valid for the base tab:
        if (model_context == 'tab1'):
            DataModel.model_data["PlayerStateData"]["PersistentPlayerBases"].insert(0, nms_base_json_array)
            DataModel.modelChanged.emit()
        else:
            return  # error

        logger.debug("add_base() EXIT")



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