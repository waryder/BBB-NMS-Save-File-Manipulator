from imports import *
from IniFileManager import *
from pympler import asizeof

class JsonArrayView(QObject):
    def __init__(self, model, model_context = 'main'):
        self.model = model

        #should come in 'main', 'tab1', 'tab2', 'tab3' ...
        self.model_context = model_context
        self.inventory_source_list = self.init_inventory_source_list()

    def get_text(self):
        return json.dumps(self.get_json(), indent=4)

    def set_text(self, text):
        json_array = self.model.json_loads_with_exception_check(text)

        if json_array:
            # print("####################")
            # print(f"json_array is of type: {type(json_array)}")
            # print(f"The size of the variable is: {sys.getsizeof(json_array)} bytes")
            # #if isinstance(json_array, list):
            # print(f"The number of items in the list is: {len(json_array)}")
            # print(f"Keys: {json_array[0].keys()}")
            #
            # print("####################")

            return self.set_json(json_array)
        else:
            return False

    def get_json(self):
        data = self.model.get_data()

        if not data:
            return None

        if (self.model_context == 'main'):
            return data

        elif (self.model_context == 'tab1'):
            return data["PlayerStateData"]["PersistentPlayerBases"]

        elif (self.model_context == 'tab2'):
            return data["PlayerStateData"]["ShipOwnership"]

        elif (self.model_context == 'tab3'):
            return self.get_inventory_sources()
        else:
            return #error

    # Helper function to access nested keys
    def get_nested_value(self, keys):
        model_data = self.model.get_data()

        """Retrieve a nested value from a dictionary using a list of keys.
        Returns None if any key is missing or any exception occurs."""
        try:
            for key in keys:
                model_data = model_data[key]  # Optimized: no key existence check
            return model_data
        except Exception:
            return None

    def get_inventory_source_list(self):
        return self.inventory_source_list

    def init_inventory_source_list(self):
        inventory_source_list = [
           ['PlayerStateData', 'Inventory'],
           ['PlayerStateData', 'Chest1Inventory'],
           ['PlayerStateData', 'Chest2Inventory'],
           ['PlayerStateData', 'Chest3Inventory'],
           ['PlayerStateData', 'Chest4Inventory'],
           ['PlayerStateData', 'Chest5Inventory'],
           ['PlayerStateData', 'Chest6Inventory'],
           ['PlayerStateData', 'Chest7Inventory'],
           ['PlayerStateData', 'Chest8Inventory'],
           ['PlayerStateData', 'Chest9Inventory'],
           ['PlayerStateData', 'Chest10Inventory'],
           ['PlayerStateData', 'FreighterInventory'],
           ['PlayerStateData', 'FishPlatformInventory'],
           ['PlayerStateData', 'FishBaitBoxInventory'],
           ['PlayerStateData', 'CookingIngredientsInventory'],
           ['PlayerStateData', 'ShipOwnership', 0],
           ['PlayerStateData', 'ShipOwnership', 1],
           ['PlayerStateData', 'ShipOwnership', 2],
           ['PlayerStateData', 'ShipOwnership', 3],
           ['PlayerStateData', 'ShipOwnership', 4],
           ['PlayerStateData', 'ShipOwnership', 5],
           ['PlayerStateData', 'ShipOwnership', 6],
           ['PlayerStateData', 'ShipOwnership', 7],
           ['PlayerStateData', 'ShipOwnership', 8],
           ['PlayerStateData', 'ShipOwnership', 9],
           ['PlayerStateData', 'ShipOwnership', 10],
           ['PlayerStateData', 'ShipOwnership', 11]
        ]

        return inventory_source_list


    def get_inventory_sources(self, inv_id=None): #if id, we'll return just the object with the same id if found:
        model_data = self.model.get_data()
        inventory_sources = []

        inventory_source_list = self.get_inventory_source_list()

        for item in inventory_source_list:
            inv = self.get_nested_value(item)
            if inv:
                if not inv_id:
                    inventory_sources.append(inv)
                elif inv_id == id(inv):
                    return inv

        return inventory_sources

    def get_storage_label_name_deep_copy(self, idx, json_data, prepend='', append=''):
        inventory_source_list = self.get_inventory_source_list()
        storage_container_name = copy.deepcopy(json_data['Name'])

        if not storage_container_name:
            storage_container_name = "No name provided"

        if inventory_source_list[idx][1] == 'Inventory':
            storage_container_name = prepend + "Exosuit" + append + ': ' + storage_container_name

        if inventory_source_list[idx][1] == 'Chest1Inventory':
            storage_container_name = prepend + "Storage Container 1" + append + ': ' + storage_container_name

        if inventory_source_list[idx][1] == 'Chest2Inventory':
            storage_container_name = prepend + "Storage Container 2" + append + ': ' + storage_container_name

        if inventory_source_list[idx][1] == 'Chest3Inventory':
            storage_container_name = prepend + "Storage Container 3" + append + ': ' + storage_container_name

        if inventory_source_list[idx][1] == 'Chest4Inventory':
            storage_container_name = prepend + "Storage Container 4" + append + ': ' + storage_container_name

        if inventory_source_list[idx][1] == 'Chest5Inventory':
            storage_container_name = prepend + "Storage Container 5" + append + ': ' + storage_container_name

        if inventory_source_list[idx][1] == 'Chest6Inventory':
            storage_container_name = prepend + "Storage Container 6" + append + ': ' + storage_container_name

        if inventory_source_list[idx][1] == 'Chest7Inventory':
            storage_container_name = prepend + "Storage Container 7" + append + ': ' + storage_container_name

        if inventory_source_list[idx][1] == 'Chest8Inventory':
            storage_container_name = prepend + "Storage Container 8" + append + ': ' + storage_container_name

        if inventory_source_list[idx][1] == 'Chest9Inventory':
            storage_container_name = prepend + "Storage Container 9" + append + ': ' + storage_container_name

        if inventory_source_list[idx][1] == 'Chest10Inventory':
            storage_container_name = prepend + "Storage Container 10" + append + ': ' + storage_container_name

        if inventory_source_list[idx][1] == 'FishPlatformInventory':
            storage_container_name = prepend + "Fish Platform" + append + ': ' + storage_container_name

        if inventory_source_list[idx][1] == 'FishBaitBoxInventory':
            storage_container_name = prepend + "Fish Bait Box" + append + ': ' + storage_container_name

        if inventory_source_list[idx][1] == 'CookingIngredientsInventory':
            storage_container_name = prepend + "Cooking Ingredients" + append + ': ' + storage_container_name

        if inventory_source_list[idx][1] == 'FreighterInventory':
            storage_container_name = prepend + "Freighter" + append + ': ' + storage_container_name

        if inventory_source_list[idx][1] == 'ShipOwnership':
            storage_container_name = prepend + f"Starship {inventory_source_list[idx][2] + 1}" + append + ': ' + storage_container_name

        return storage_container_name

    def set_json(self, json_array):
        if (self.model_context == 'main'):
            #need to pass this in rather than use get_data and modify, because resetting the entire data structure would change the reference instead of the model internal data:
            self.model.set_data(json_array)

        elif (self.model_context == 'tab1'):
            data = self.model.get_data()
            #data was provided as a reference here so its modifying the original structure:
            data["PlayerStateData"]["PersistentPlayerBases"] = json_array
            self.model.modelChanged.emit()

        elif (self.model_context == 'tab2'):
            data = self.model.get_data()
            # data was provided as a reference here so its modifying the original structure:
            data["PlayerStateData"]["ShipOwnership"] = json_array
            self.model.modelChanged.emit()

        elif (self.model_context == 'tab3'):
            # data was provided as a reference here so its modifying the original structure:
            #data = self.model.get_data()

            for i, data in enumerate(self.get_inventory_sources()):
                data[i] = json_array[i]

            self.model.modelChanged.emit()

        return True

    def add_base(self, nms_base_json_array):
        # only valid for the base tab:
        if (self.model_context == 'tab1'):
            data = self.model.get_data()

            data["PlayerStateData"]["PersistentPlayerBases"].insert(0, nms_base_json_array)
            self.model.modelChanged.emit()

            return True
        else:
            return False

    def replace_inventory(self, nms_inventory_json_array, node_to_be_replaced):
        # only valid for the inventory tab; sanity check:
        if (self.model_context == 'tab3'):
            model_data = self.model.get_data()
            #we know we are in a tab3 context:
            existing_inventories = self.get_json()

            #get the index of the node within it's parent which mimics the position index within the json:
            parent = node_to_be_replaced.parent()
            index = parent.indexOfChild(node_to_be_replaced)

            # we need to sanity check that this inventory has been expanded here since our moves assume we have
            # at least 100 slots:

            #print(len(existing_inventories[index]['ValidSlotIndices']))

            if(len(existing_inventories[index]['ValidSlotIndices']) < 100):
                self.resetValidSlotIndices(existing_inventories[index]['ValidSlotIndices'])

            #print(len(existing_inventories[index]['ValidSlotIndices']))


            #print(f"before: len(existing_inventories[index]['Slots']): {len(existing_inventories[index]['Slots'])}, len(nms_inventory_json_array['Slots']): {len(nms_inventory_json_array['Slots'])}")

            #use that index to know which json item we need to replace with the new inv data.
            #Just replace the items, not the whole array:
            existing_inventories[index]['Slots'] = nms_inventory_json_array['Slots']

            #print(
            #    f"after: len(existing_inventories[index]['Slots']): {len(existing_inventories[index]['Slots'])}, len(nms_inventory_json_array['Slots']): {len(nms_inventory_json_array['Slots'])}")

            #shouldn't be needed since we have already
            self.set_json(existing_inventories)

        else:
            return  # error

    #utility functions:
    def resetValidSlotIndices(self, target_game_inventory_validSlotIndices):
        # reset the validSlotIndices:
        target_game_inventory_validSlotIndices.clear()
        target_game_inventory_validSlotIndices.extend(self.genExpandedValidSlotIndices())

    def genExpandedValidSlotIndices(self):
        output = []
        for i in range(10):
            for j in range(10):
                item = {"X": i, "Y": j}
                output.append(item)

        return output


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