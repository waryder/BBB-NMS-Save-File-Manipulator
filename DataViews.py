from imports import *
from IniFileManager import *
from pympler import asizeof

class JsonArrayView(QObject):
    def __init__(self, owner, model, model_context = 'main'):
        super().__init__()
        self.model = model
        self.owner = owner

        #should come in 'main', 'tab1', 'tab2', 'tab3' ...
        self.model_context = model_context
        self.inventory_source_list = self.init_inventory_source_list()

    def get_text(self):
        return json.dumps(self.get_json(), indent=4)

    def set_text(self, text):
        json_array = self.model.json_loads_with_exception_check(text)

        if json_array:
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

        elif (self.model_context == 'tab4'):
            return data["PlayerStateData"]["TeleportEndpoints"]

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
           ['PlayerStateData', 'ShipOwnership', 0, 'Inventory'],
           ['PlayerStateData', 'ShipOwnership', 1, 'Inventory'],
           ['PlayerStateData', 'ShipOwnership', 2, 'Inventory'],
           ['PlayerStateData', 'ShipOwnership', 3, 'Inventory'],
           ['PlayerStateData', 'ShipOwnership', 4, 'Inventory'],
           ['PlayerStateData', 'ShipOwnership', 5, 'Inventory'],
           ['PlayerStateData', 'ShipOwnership', 6, 'Inventory'],
           ['PlayerStateData', 'ShipOwnership', 7, 'Inventory'],
           ['PlayerStateData', 'ShipOwnership', 8, 'Inventory'],
           ['PlayerStateData', 'ShipOwnership', 9, 'Inventory'],
           ['PlayerStateData', 'ShipOwnership', 10, 'Inventory'],
           ['PlayerStateData', 'ShipOwnership', 11, 'Inventory']
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

    def set_json(self, json_array):
        if (self.model_context == 'main'):
            # need to pass this in rather than use get_data and modify, because resetting the entire data
            # structure would change the reference instead of the model internal data:
            self.model.set_data(json_array)

        elif (self.model_context == 'tab1'):
            data = self.model.get_data()
            #data was provided as a reference here so its modifying the original structure:
            data["PlayerStateData"]["PersistentPlayerBases"] = json_array

        elif (self.model_context == 'tab2'):
            data = self.model.get_data()
            # data was provided as a reference here so its modifying the original structure:
            data["PlayerStateData"]["ShipOwnership"] = json_array

        elif (self.model_context == 'tab3'):
            # data was provided as a reference here so it's modifying the original structure:
            #data = self.model.get_data()

            for i, data in enumerate(self.get_inventory_sources()):
                data[i] = json_array[i]

        elif (self.model_context == 'tab4'):
            data = self.model.get_data()
            data["PlayerStateData"]["TeleportEndpoints"] = json_array

        self.model.modelChanged.emit(None)
        return True

    def getTabObj(self):
        return self.owner

    def add_base(self, nms_base_json_array):
        # only valid for the base tab:
        if (self.model_context == 'tab1'):
            data = self.model.get_data()

            data["PlayerStateData"]["PersistentPlayerBases"].insert(0, nms_base_json_array)
            self.model.modelChanged.emit(self.getTabObj())

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
            if(len(existing_inventories[index]['ValidSlotIndices']) < 120):
                self.resetValidSlotIndices(existing_inventories[index]['ValidSlotIndices'])

            #use that index to know which json item we need to replace with the new inv data.
            #Just replace the items, not the whole array:
            existing_inventories[index]['Slots'] = nms_inventory_json_array['Slots']

            #shouldn't be needed since we have already
            #self.set_json(existing_inventories)
            self.model.modelChanged.emit(self.getTabObj())

        else:
            return  # error

    #utility functions:
    def resetValidSlotIndices(self, target_game_inventory_validSlotIndices):
        # reset the validSlotIndices:
        target_game_inventory_validSlotIndices.clear()
        target_game_inventory_validSlotIndices.extend(self.genExpandedValidSlotIndices())

    def genExpandedValidSlotIndices(self):
        MAX_X = 9
        MAX_Y = 11

        output = []
        for x in range(MAX_X + 1): #this will result in 0 to 9
            for y in range(MAX_Y + 1): #this will result in 0 to 11
                item = {"X": x, "Y": y}
                output.append(item)

        return output

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

    def get_teleport_endpoint_label_name_deep_copy(self, idx, json_data, prepend='', append=''):
        teleport_endpoint_name = copy.deepcopy(json_data['Name'])
        portal_address = self.convert_galactic_address_to_portal(json_data['UniverseAddress']['GalacticAddress'])

        if not teleport_endpoint_name:
            teleport_endpoint_name = "No name provided"

        teleport_endpoint_name = f"Teleport Endpoint {idx + 1}: {teleport_endpoint_name}, Galaxy: {self.convert_universe_addr_to_galaxy_value(json_data)}, Portal Addr: {portal_address}"
        return teleport_endpoint_name

    def convert_teleport_endpoint_position_to_lat_long(self, position):
        """
        Converts Cartesian coordinates from a save file position to in-game latitude and longitude.

        Args:
            position (list): A list containing [X, Y, Z] coordinates from the save file.

        Returns:
            dict: A dictionary with keys 'Latitude' and 'Longitude' in degrees.
        """
        x, y, z = position

        # Calculate the radius (distance from the planet center)
        r = math.sqrt(x ** 2 + y ** 2 + z ** 2)

        # Calculate latitude
        latitude = math.degrees(math.asin(y / r))

        # Calculate longitude
        longitude = math.degrees(math.atan2(z, x))

        return {'Latitude': latitude, 'Longitude': longitude}

    def convert_galactic_address_to_portal(self, galactic_address):
        """
        Converts a GalacticAddress dictionary (as from PlayerStateData->TeleportEndpoints) into a 12-glyph portal address and its corresponding galaxy value.

        Args:
            galactic_address (dict): A dictionary containing the GalacticAddress data.
                Example:
                    {
                        "VoxelX": 721,
                        "VoxelY": 4,
                        "VoxelZ": -1504,
                        "SolarSystemIndex": 365,
                        "PlanetIndex": 6
                    }

        Returns:
            tuple: A tuple containing the galaxy value (hex) and the full 12-glyph portal address (hex).
        """
        # Extract components
        voxel_x = galactic_address["VoxelX"]
        voxel_y = galactic_address["VoxelY"]
        voxel_z = galactic_address["VoxelZ"]
        solar_system_index = galactic_address["SolarSystemIndex"]
        planet_index = galactic_address["PlanetIndex"]

        # Convert components to hexadecimal, handling padding
        voxel_x_hex = f"{voxel_x & 0xFFF:03X}"  # Ensure 3 hex digits
        voxel_y_hex = f"{voxel_y & 0xFF:02X}"  # Ensure 2 hex digits
        voxel_z_hex = f"{(voxel_z & 0xFFF):03X}"  # Ensure 3 hex digits (2's complement for negatives)
        solar_system_index_hex = f"{solar_system_index & 0xFFF:03X}"  # Ensure 3 hex digits
        planet_index_hex = f"{planet_index & 0xF:X}"  # Ensure 1 hex digit

        # Combine components into the full 12-glyph portal address
        portal_address = f"{planet_index_hex}{solar_system_index_hex}{voxel_y_hex}{voxel_z_hex}{voxel_x_hex}"

        return portal_address

    def convert_universe_addr_to_galaxy_value(self, universe_data):
        """
        Extracts the galaxy value from a UniverseAddress dictionary.

        Args:
            universe_data (dict): A dictionary containing the UniverseAddress data.
                Example:
                    {
                        "UniverseAddress": {
                            "RealityIndex": 0,
                            "GalacticAddress": {
                                "VoxelX": 672,
                                "VoxelY": 15,
                                "VoxelZ": 207,
                                "SolarSystemIndex": 79,
                                "PlanetIndex": 1
                            }
                        }
                    }

        Returns:
            str: The galaxy value as a 2-digit hex string.
        """
        # Extract components from UniverseAddress
        universe_address = universe_data["UniverseAddress"]
        reality_index = universe_address["RealityIndex"]

        # Convert reality index to 2-digit hex value
        #galaxy_value = f"0x{reality_index & 0xFF:02X}"

        galaxy_value = GALAXIES[reality_index & 0xFF]
        return galaxy_value

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