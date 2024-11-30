from imports import *
from IniFileManager import *
from pympler import asizeof

class JsonArrayView(QObject):
    def __init__(self, model, model_context = 'main'):
        self.model = model

        #should come in 'main', 'tab1', 'tab2', 'tab3' ...
        self.model_context = model_context

    def get_text(self):
        return json.dumps(self.get_json(), indent=4)

    def set_text(self, text):
        json_array = json_loads_with_exception_check(text)

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
            if isinstance(data, list):
                print(f"The number of items in the list is: {len(data)}")
            return data["PlayerStateData"]["PersistentPlayerBases"]

        elif (self.model_context == 'tab2'):
            return data["PlayerStateData"]["ShipOwnership"]

        elif (self.model_context == 'tab3'):
            containers = []

            #I believe this is the exosuit inventory:
            if not data["PlayerStateData"][f"Inventory"]["Name"]:
                data["PlayerStateData"][f"Inventory"]["Name"] = "ExoSuit Inventory"
            containers.append(data["PlayerStateData"][f"Inventory"])

            #Storage containers only right now:
            for i in range(0, 10):
                containers.append(data["PlayerStateData"][f"Chest{i + 1}Inventory"])

                if not containers[i]['Name']:
                    containers[i]['Name'] = f"No Name Provided In Data; Storage {i + 1}"

            data["PlayerStateData"][f"FreighterInventory"]["Name"] = "Freighter Inventory"
            containers.append(data["PlayerStateData"][f"FreighterInventory"])

            # print("\n\n***get_json")
            #
            #
            # for index, item in enumerate(containers):
            #     # Check if the item has a 'Name' key
            #     if 'Name' in item:
            #         print(f"Name at index {index}: {item['Name']}")
            #     else:
            #         print(f"Missing 'Name' at index {index}")

            return containers
        else:
            return #error

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
            data = self.model.get_data()

            # for index, item in enumerate(json_array):
            #     # Check if the item has a 'Name' key
            #     if 'Name' in item:
            #         print(f"Name at index {index}: {item['Name']}")
            #     else:
            #         print(f"Missing 'Name' at index {index}")

            data["PlayerStateData"][f"Inventory"]['Name'] = ""
            data["PlayerStateData"][f"Inventory"] = json_array[0]

            for i in range(1, 11):
                if "No Name Provided In Data" in json_array[i]['Name']:
                    json_array[i]['Name'] = ""

                data["PlayerStateData"][f"Chest{i}Inventory"] = json_array[i]

                #print(f"""{data["PlayerStateData"][f"Chest{i}Inventory"]['Name']}:
                #{len(data["PlayerStateData"][f"Chest{i}Inventory"]['Slots'])}
                #""")

            data["PlayerStateData"][f"FreighterInventory"]['Name'] = ""
            data["PlayerStateData"][f"FreighterInventory"] = json_array[11]
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