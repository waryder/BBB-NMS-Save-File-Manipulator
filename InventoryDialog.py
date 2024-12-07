from imports import *

from PyQt5.QtWidgets import QApplication, QComboBox, QCheckBox, QListWidget, QListWidgetItem, QStyledItemDelegate, QVBoxLayout, QWidget
from MultiSelectComboBox import MultiSelectComboBox

class InventoryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        self.MAX_INVENTORY_CAPACITY = 120
        self.MAX_INVENTORY_SLOT_INDEX = {'X': 9, 'Y': 11}

        self._source_storage_container_inv_names = {"NAME1" : "Storage Container 1", "NAME2" : "Storage Container 2",
            "NAME3" : "Storage Container 3", "NAME4" : "Storage Container 4", "NAME5" : "Storage Container 5",
            "NAME6" : "Storage Container 6", "NAME7" : "Storage Container 7", "NAME8" : "Storage Container 8",
            "NAME9" : "Storage Container 9", "NAME10" : "Storage Container 10"}

        #just for readability later, actual names are copies:
        self._target_storage_container_inv_names = self._source_storage_container_inv_names

        self.inventory_source_list = self.parent.view.get_inventory_source_list()
        self.inventory_sources = self.parent.view.get_inventory_sources()

        self.categories = {
            "Product (Crafted or Special Items)":"Product", "Substance (Organic Resources)":"Substance", "Technology (Tech Upgrades)": "Technology",
            "Consumable (Food and One Use Items)": "Consumable", "Trade (Commodities)": "Trade", "Special (Specialty Items)": "Special"
        }

        self.category_names = list(self.categories.keys())

        self.parent = parent
        self.setWindowTitle("Inventory Sorter")
        self.setMinimumSize(1075, 800)

        # Remove the question mark button from the dialog
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        # Store references to checkboxes and combo boxes
        self.source_checkboxes = {}  # To store source checkboxes
        self.target_checkboxes = {}  # To store target checkboxes
        self.target_combo_boxes = {}  # To store combo boxes

        # Layouts for Inventory Sources and Targets
        main_layout = QVBoxLayout(self)
        lists_layout = QHBoxLayout()
        button_layout = QHBoxLayout()

        lists_layout.addWidget(self.create_left_scroll_area(), stretch=43)
        lists_layout.addWidget(self.create_right_scroll_area(), stretch=57)

        # Buttons at the bottom
        execute_button = QPushButton("Execute Sort")
        execute_button.setFixedWidth(175)
        execute_button.clicked.connect(self.execute_sort)  # Connect to execute_sort handler

        cancel_button = QPushButton("Cancel")
        cancel_button.setFixedWidth(175)
        cancel_button.clicked.connect(self.cancel_dialog)  # Connect to cancel_dialog handler

        # Align buttons to the left
        button_layout.addWidget(execute_button)
        button_layout.addWidget(cancel_button)
        button_layout.addStretch()  # Push buttons to the left

        # Add to main layout
        main_layout.addLayout(lists_layout)
        main_layout.addWidget(self.create_bottom_section())
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        self.parent.ini_file_manager.apply_inventory_sorter_defaults_to_checkboxes(
            self.source_checkboxes,
            self.target_checkboxes,
            self.target_combo_boxes)

    def create_left_scroll_area(self):
        # Left pane (Inventory Sources)
        left_pane_layout = QVBoxLayout()
        inv_label = QLabel("<b>Source Inventories</b>")
        inv_label.setFixedSize(200, 20)
        left_pane_layout.addWidget(inv_label)

        # Load the left_pane_layout with checkboxes
        for idx, inventory in enumerate(self.inventory_sources):
            label = self.parent.view.get_storage_label_name_deep_copy(idx, inventory)
            checkbox = QCheckBox(label)  # Use the dictionary key as the checkbox label
            checkbox.setProperty("inventory_id", id(inventory))

            checkbox.setFixedSize(400, 18)
            left_pane_layout.addWidget(checkbox)
            self.source_checkboxes[idx] = checkbox

        left_scroll_area = QScrollArea()
        left_widget = QWidget()
        left_widget.setLayout(left_pane_layout)
        left_scroll_area.setWidget(left_widget)
        left_scroll_area.setWidgetResizable(False)

        return left_scroll_area

    def create_right_scroll_area(self):
        # Right pane (Inventory Targets)
        right_pane_layout = QGridLayout()

        # Add "Inventory Targets" title
        inv_label = QLabel("<b>Target Inventories</b>")
        cats_label = QLabel("<b>Categories</b>")
        inv_label.setFixedSize(200, 20)
        cats_label.setFixedSize(200, 20)
        right_pane_layout.addWidget(inv_label, 0, 0)
        right_pane_layout.addWidget(cats_label, 0, 1)

        row = 1
        # Add checkboxes and dropdowns in right pane
        for idx, inventory in enumerate(self.inventory_sources):
            label = self.parent.view.get_storage_label_name_deep_copy(idx, inventory)
            checkbox = QCheckBox(label)  # Use the dictionary key as the checkbox label
            checkbox.setProperty("inventory_id", id(inventory))

            checkbox.setFixedSize(305, 18)
            combo_box = MultiSelectComboBox()  # QComboBox()
            combo_box.addItems(list(self.categories.keys()))
            combo_box.setFixedSize(250, 18)

            combo_box.setToolTip(
"""Substance\t- Represents a resource or material, such as Oxygen, Ferrite Dust, etc.
Product\t- Represents crafted items or special items, such as Warp Cells, Starship Launch Fuel, etc.
Technology\t- Represents technology upgrades, such as suit or ship technology modules (e.g., a Shield upgrade or Hyperdrive).
Consumable\t- Represents items that can be consumed directly by the player, such as food items or other one-time-use items.
Trade\t\t- Represents trade commodities that are specifically for buying and selling, usually for profit.
Special\t\t- Represents unique items or those used for quests. These could be items that don’t quite fall under other categories."""
            )

            right_pane_layout.addWidget(checkbox, row, 0)
            right_pane_layout.addWidget(combo_box, row, 1)
            self.target_checkboxes[idx] = checkbox  # Store the checkbox
            self.target_combo_boxes[idx] = combo_box
            row += 1

        right_scroll_area = QScrollArea()
        right_widget = QWidget()
        right_widget.setLayout(right_pane_layout)
        right_scroll_area.setWidget(right_widget)
        right_scroll_area.setWidgetResizable(False)

        return right_scroll_area

    def create_bottom_section(self):
        # Create a new horizontal layout
        overflow_section_layout = QHBoxLayout()

        # Add the checkbox to the layout
        overflow_checkbox = QCheckBox("Use All Unselected Storage Containers For Overflow")
        overflow_checkbox.setToolTip(
            "If checked, any storage containers\n"
            "that you have not actually checked will be used\n"
            "in case checked storage containers become full.\n\n"
            "If unchecked, it is more likely some items may\n"
            "not be moved since processing stops when all\n"
            "indicated storages are full."
        )

        #we may want to save of the last state of this after the sort is done later.
        #not sure about that yet at this time so we'll default to this for now:
        overflow_checkbox.setChecked(True)

        # Align the checkbox to the left
        overflow_section_layout.addWidget(overflow_checkbox)
        overflow_section_layout.addStretch()  # Push the checkbox to the left and add space to the right

       # Create a container widget for the layout
        overflow_section_widget = QWidget()
        overflow_section_widget.setLayout(overflow_section_layout)

        overflow_section_widget.setObjectName("overflowSectionWidget")
        overflow_section_widget.setStyleSheet("""
            #overflowSectionWidget {
                border: 1px solid black;
            }
        """)

        # Store a reference to the checkbox if needed later
        self.overflow_checkbox = overflow_checkbox

        return overflow_section_widget

    def execute_sort(self): #Entry point for button:
        print("Execute Sort button clicked, execute_sort() Enter", "w")
        checkedValues = self.getcheckedValues()

        print(f"Checked boxes: {checkedValues}")
        #parent with be tab3 here:
        self.parent.update_tree_synced_indicator(False)

        #save off the last used settings for reuse next time around:
        self.parent.ini_file_manager.store_configfile_inventory_sorter_defaults(
            self.source_checkboxes,
            self.target_checkboxes,
            self.target_combo_boxes)

        self.process_sort(checkedValues)

        #let everyone know the model has changed; updates all views:
        self.parent.model.modelChanged.emit()

        QMessageBox.information(None, "Info", "Inventory has been sorted!")

        print("execute_sort() Exit")
        self.close()

    """
    The process_sort function organizes items from source inventories into 
    target inventories based on matching categories, ensuring that items are 
    added in an orderly manner without exceeding capacity constraints. 

    The function performs the following steps:

    1. Check Capacity:
       - If a target inventory already contains 100 or more items, it skips 
         to the next target.

    2. Expand Inventory:
       - Ensures that the target inventory is correctly prepared for adding 
         items by resetting valid slot indices.

    3. Standardize Slot Order:
       - Reorganizes the target inventory slots to maintain a consistent structure.

    4. Match and Move Items:
       - Iterates through each source inventory and its slots to find items 
         matching the categories specified for the target.
       - Moves a matching item from the source to the target.
       - Updates the item's slot index to reflect its new position in the 
         target inventory.

    5. Stop on Full Inventory:
       - If a target inventory reaches 100 items while processing, the 
         function stops processing the current target and moves to the next.

    6. Log Operations:
       - Outputs detailed information about the process, including inventory 
         states before and after modifications, matched items, and slot index 
         adjustments.

    This function ensures that target inventories do not exceed their 
    capacity and that items are sorted in a logical and organized manner.
    """
    def process_sort(self, checkedValues):
        print("process_sort() Enter")
        checkedSources = checkedValues['sources']
        checkedTargets = checkedValues['targets']
        checkedCategories = checkedValues['categories']

        if not checkedTargets or not checkedSources or not checkedCategories:
            logger.error("Either No targets, no sources, or no categories were provided. Exiting process_sort.")
            QMessageBox.information(None, "Info", "Either No targets, no sources, or no categories were provided. Exiting process_sort.")
            return

        for checkedTarget in checkedTargets:
            break_for_next_target = False

            target_checkbox = checkedTarget[1]
            target_model_inventory = self.parent.view.get_inventory_sources(target_checkbox.property('inventory_id'))

            target_game_inventory_name = target_model_inventory['Name']
            #get categories at the same key into the current checkerTarget:
            target_game_categories = checkedCategories.get(checkedTarget[0], [])

            target_game_inventory_validSlotIndices = target_model_inventory['ValidSlotIndices']
            target_game_inventory_slots = target_model_inventory['Slots']

            print(f"\nTarget Start: '{checkedTarget}'")
            print(f"Target '{target_game_inventory_name}' Inventory Slot Count Before: {len(target_game_inventory_slots)}\n")

            # we need to have a standardized indexing of inventory here so we can add items in the right positions:
            self.reorder_slot_items(target_game_inventory_slots)
            #print(f"\nTarget {target_game_inventory_name} Inventory Slots After Reorder only!:\n{json.dumps(target_game_inventory_slots, indent=4)}\n")

            # Make sure the target inventory is expanded:
            self.parent.view.resetValidSlotIndices(target_game_inventory_validSlotIndices)

            for checkedSource in checkedSources:
                print(f"source Start: '{checkedSource}'")

                source_checkbox = checkedSource[1]
                source_model_inventory = self.parent.view.get_inventory_sources(source_checkbox.property('inventory_id'))

                source_game_inventory_name = source_model_inventory['Name']
                #source_game_inventory_validSlotIndices = source_model_inventory['ValidSlotIndices']

                if(target_model_inventory == source_model_inventory):
                    print(f"target ({target_game_inventory_name}) and source: ({source_game_inventory_name}) are the same. Iterating to next source...")
                    continue  # for source

                #Even though these were valid data before now, we first needed to do the last check before these next two:
                if (len(target_game_inventory_slots) >= self.MAX_INVENTORY_CAPACITY):
                    msg = (f"Target inventory '{target_game_inventory_name}' is full. Currently "
                           f"{len(target_game_inventory_slots)} items. Moving to next target inventory...")

                    print(msg)
                    QMessageBox.critical(None, "Info", msg)
                    break  # for source to go out to next target

                if (len(target_game_inventory_slots) and target_game_inventory_slots[-1]['Index'] == self.MAX_INVENTORY_SLOT_INDEX):
                    #we should never get here given the logic above. at this point we have reordered the target items AND checked
                    #the target is not full...but it's a sanity check...
                    msg = (f"Target inventory {target_game_inventory_name} already contains max items. "
                           "Skipping target inventory.")

                    print(msg)
                    QMessageBox.critical(None, "Info", msg)
                    break  # for source to go out to next target

                source_game_inventory_slots = source_model_inventory['Slots']

                print(
                    f"Source '{source_game_inventory_name}' Inventory Slot Count Before: {len(source_game_inventory_slots)}\n")

                ### within this source, move over any items that match each category:

                print(f"\n###len(target_game_categories): {len(target_game_categories)}")
                print(f"\ttarget_game_categories:\n{json.dumps(target_game_categories, indent=4)}\n")

                for category in target_game_categories:
                    #[:] causes iteration over a shallow copy:
                    for slot in source_game_inventory_slots[:]:
                        if category == slot['Type']['InventoryType']:
                            print(f"Got a match on inventory type: '{category}', Id: {slot['Id']}")

                            last_target_slot = None
                            if target_game_inventory_slots:  # target_game_inventory_slots not empty:
                                #get the slot index values for the last filled slot in the target:
                                last_target_slot = target_game_inventory_slots[-1]

                            # swap the slot data over to target and delete from source:
                            source_game_inventory_slots.remove(slot) # Remove the current slot from source
                            target_game_inventory_slots.append(slot)

                            if last_target_slot: #if we did have an existing, use it to set the moved item idx:
                                target_game_inventory_slots[-1]['Index'] = self.validSlotIndiciesNext(last_target_slot['Index'])
                            else: #new item is the first in the list. Assign idx manually:
                                target_game_inventory_slots[-1]['Index']['X'] = 0
                                target_game_inventory_slots[-1]['Index']['Y'] = 0

                            if(len(target_game_inventory_slots) == self.MAX_INVENTORY_CAPACITY):
                                break_for_next_target = True
                                break #for slot

                    if(break_for_next_target):
                        print(
                            f"Target is full; Target End, '{target_game_inventory_name}' Inventory Slot Count: {len(target_game_inventory_slots)}")
                        break #for category

                if(break_for_next_target):
                    print(
                        f"\nSource End {source_game_inventory_name} due to full target; Inventory Slot Count: {len(source_game_inventory_slots)}\n")
                    break  # for source

                print(
                    f"\nSource End {source_game_inventory_name} Inventory Slot Count After Sort: {len(source_game_inventory_slots)}. Going up to get next source if there is one...\n")

            print(
                f"Target End, '{target_game_inventory_name}' Inventory Slot Count After Target: {len(target_game_inventory_slots)}\n")


        print("process_sort() Exit")

    def reorder_slot_items(self, target_game_inventory_slots):
        if not target_game_inventory_slots: #this could be fine. Just an empty inventory list:
            return

        target_game_inventory_slots[0]['Index']['X'] = 0
        target_game_inventory_slots[0]['Index']['Y'] = 0
        last_idx = target_game_inventory_slots[0]['Index']

        for i in range(1, len(target_game_inventory_slots)):
            target_game_inventory_slots[i]['Index'] = self.validSlotIndiciesNext(last_idx)
            last_idx = target_game_inventory_slots[i]['Index']

    def getcheckedValues(self):
        print( f"\ngetcheckedValues() ENTER\n")

        # Get checked sources
        checked_sources = [(key, checkbox) for key, checkbox in self.source_checkboxes.items() if checkbox.isChecked()]
        checked_targets = [(key, checkbox) for key, checkbox in self.target_checkboxes.items() if checkbox.isChecked()]
        checked_categories = {}

        for key, _ in checked_targets:
            checked_categories[key] = self.target_combo_boxes[key].lineEdit().text().split(',')

        # If overflow checkbox is checked, process storage containers in reverse order:
        if self.overflow_checkbox.isChecked():
            storage_container_idx_range = range(1, 11)

            target_checkboxes_list = list(self.target_checkboxes.items())
            for idx in storage_container_idx_range:
                # Access storage containers in reverse order (10 to 1)
                reverse_idx = 11 - idx

                #Counting backwards, if unchecked, add checkbox object to checked_targets and continue the loop:
                if not target_checkboxes_list[reverse_idx][1].isChecked():
                    #the line before accesses a checkbox in the structure. The next line steps out to a
                    #tuple that has a key and then the checkbox and is what is expected in checked_targets:
                    checked_targets.append(target_checkboxes_list[reverse_idx])
                    #now we need to add a record for "all categories" for this target:
                    checked_categories[target_checkboxes_list[reverse_idx][0]] = list(self.categories.values())
                    continue  # Skip to the next iteration

                #We get here when an unchecked box is found, and exit the loop:
                break

        for key in checked_categories:
            checked_categories[key] = [
                re.sub(r'\s*\(.*?\)\s*', '', item).strip()  # Remove parentheses and trim
                for item in checked_categories[key]
            ]

        return {"sources": checked_sources, "targets": checked_targets, "categories": checked_categories}

    def cancel_dialog(self):
        # Close the dialog when Cancel is clicked
        self.reject()

    def validSlotIndiciesNext(self, current_item):
        MAX_X = 9
        MAX_Y = 11

        # Extract current X and Y values
        x, y = current_item["X"], current_item["Y"]

        # Increment Y first to move across the row
        if y < MAX_Y:
            y += 1
        else:
            # If Y is at the end of the row, reset Y and increment X
            y = 0
            x += 1

        # Check if both X and Y are within grid limits
        if x > MAX_X or y > MAX_Y:
            logger.error("Attempted to request the next valid slot index beyond the row or column max count.")
            return None  # Return None if there’s no next item in the grid

        return {"X": x, "Y": y}


# MIT License
#
# Copyright (c) [Year] [Your Name or Your Company] <youremail@example.com>
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
#    [Your Name or Your Company] <youremail@example.com>, available under the MIT License.
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


    
        