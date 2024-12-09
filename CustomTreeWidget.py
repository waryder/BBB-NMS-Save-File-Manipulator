from imports import *

class DeleteTreeNodesSelectedDialog(QDialog):
    def __init__(self, num_nodes = 0):
        super().__init__()  # This calls the parent class's __init__ method (QDialog)

        # Set up the dialog layout
        self.setWindowTitle("Delete Nodes")
        self.setFixedSize(300, 100)
        
        # Create the layout and widgets
        layout = QVBoxLayout()

        # Add a label with red text
        label = QLabel(f"Delete ({num_nodes}) nodes from the Tree?")
                    
        # Set the text color to red using an explicit stylesheet for the QLabel
        #label.setStyleSheet("QLabel { color : red; }")
        label.setAlignment(Qt.AlignCenter)  # Center the text
        layout.addWidget(label)

        # Create OK and Cancel buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        
        # Connect buttons to their respective functions
        ok_button.clicked.connect(self.accept)  # Close the dialog with "OK"
        cancel_button.clicked.connect(self.reject)  # Close the dialog with "Cancel"
        
        # Add buttons to the button layout
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        # Add the button layout to the main layout
        layout.addLayout(button_layout)

        # Set the dialog layout
        self.setLayout(layout)

class CustomTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super(CustomTreeWidget, self).__init__(parent)
        
        #we expect parent to be the first tab object here:
        self.parent = parent

        if (type(parent).__name__ != "ThirdTabContent"):
            self.setDragDropMode(QAbstractItemView.InternalMove)
            self.setDragEnabled(True)
            self.setAcceptDrops(True)
            self.setDropIndicatorShown(True)

        # Enable the custom context menu on the tree widget
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        
        #handled in mousePressEvent()
        #self.customContextMenuRequested.connect(self.show_context_menu)
        
        #for scolling the tree view on drag outside of viewport:
        self.scroll_timer = QTimer(self)
        self.scroll_timer.timeout.connect(self.perform_smooth_scroll)
        self.scroll_direction = None
        
        self.right_button_selected_nodes = []
        self.right_button_dragging = False
        self.right_button_drag_start_position = None
        
    def mousePressEvent(self, event):
        # Capture the right mouse button press to start drag selection
        if event.button() == Qt.RightButton:
            self.right_button_drag_start_position = event.pos()
            self.right_button_dragging = False
            self.right_button_selected_nodes = []
            self.clearSelection()  # Clear previous selections

            # Temporarily disable drag so that right-click drag does not move the item
            self.setDragEnabled(False)
        
        super(CustomTreeWidget, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # Track hovered nodes when right mouse button is held and moved
        if event.buttons() & Qt.RightButton:
            # Check if mouse has moved a minimum distance to initiate dragging
            if (event.pos() - self.right_button_drag_start_position).manhattanLength() > QApplication.startDragDistance():
                self.right_button_dragging = True

            if self.right_button_dragging:
                # Get the item under the mouse cursor
                item = self.itemAt(event.pos())
                     
                if item and (not self.right_button_selected_nodes or item != self.right_button_selected_nodes[-1]): #if we have a new "last node" selected in the group
                    #go update the selection:
                    self.update_selected_nodes(event)
                    
        super(CustomTreeWidget, self).mouseMoveEvent(event)
       
    def update_selected_nodes(self, event):
        # Get the QModelIndex for the start and current positions
        start_nonvisual_idx = self.indexAt(self.right_button_drag_start_position)
        current_nonvisual_idx = self.indexAt(event.pos())
        
        # Ensure both positions are valid
        if not start_nonvisual_idx.isValid() or not current_nonvisual_idx.isValid():
            return
            
        top_visual_idx = self.get_visual_position_from_index(start_nonvisual_idx)
        bottom_visual_idx = self.get_visual_position_from_index(current_nonvisual_idx)

        if top_visual_idx > bottom_visual_idx:
            top_visual_idx, bottom_visual_idx = bottom_visual_idx, top_visual_idx
            #since we are flipping which node was is the top most node, we need to also do this for start_nonvisual_idx which is used later...
            start_nonvisual_idx = current_nonvisual_idx   
        
        # Initialize an empty list for the selected nodes
        self.right_button_selected_nodes = []
        self.clearSelection()
        
        item = self.itemFromIndex(start_nonvisual_idx)
        self.right_button_selected_nodes.append(item)
        item.setSelected(True)
                        
        #step through visually from the top most node, over the selected visual nodes range...        
        for idx in range(top_visual_idx, bottom_visual_idx):
            
            item = self.itemBelow(item) 
            self.right_button_selected_nodes.append(item)
            item.setSelected(True)
            
    def get_visual_position_from_index(self, nonvisual_target_idx):
        current_item = self.topLevelItem(0)  # Start from the topmost visible item
        visual_position = 0  # Initialize the visual position counter

        while current_item:
            # Get the QModelIndex of the current item
            current_index = self.indexFromItem(current_item)

            # If the current index matches the target index, return the visual position
            if current_index == nonvisual_target_idx:
                return visual_position

            # Move to the next item in visual order and increment the counter
            current_item = self.itemBelow(current_item)
            visual_position += 1

        return None  # Return None if the nonvisual_target_idx is not found in the tree 
            
    def get_qmodelindex_by_visual_position(self, visual_position):
        current_item = self.topLevelItem(0)  # Start at the first visible item
        index = 0  # Start at visual position 0

        # Traverse the tree in visual order
        while current_item:
            # When we've reached the desired visual position, return its QModelIndex
            if index == visual_position:
                return self.indexFromItem(current_item)  # Return the QModelIndex of the item
            
            # Move to the next item in visual order
            current_item = self.itemBelow(current_item)
            index += 1

        return None # Return None if the visual position exceeds the total number of items 

    def mouseReleaseEvent(self, event):
        # On right mouse release, show the appropriate context menu
        if event.button() == Qt.RightButton:
            if self.right_button_dragging:
                # Show custom context menu after drag selection
                self.show_right_button_DRAG_CONTEXT_menu(event.globalPos())
            else:
                # Always show custom right-click context menu
                self.show_right_button_DEFAULT_menu(event.globalPos())

            # Re-enable drag for left clicks
            self.setDragEnabled(True)
            self.right_button_dragging = False
            # Accept the event to prevent further processing (i.e., default context menu)
            event.accept()
            return  # Stop here to avoid calling the superclass and triggering default behavior
        
        super(CustomTreeWidget, self).mouseReleaseEvent(event)

    def show_right_button_DRAG_CONTEXT_menu(self, global_position):
        logger.debug("show_right_button_DRAG_CONTEXT_menu() ENTER")        
        
        # Show a custom context menu when dragging ends
        context_menu = QMenu(self)
        
        # Add action to display number of selected nodes
        count_action = context_menu.addAction(f"Delete {len(self.right_button_selected_nodes)} Nodes")
        count_action.triggered.connect(lambda: self.delete_tree_nodes_selected())
        
        # Show the context menu
        context_menu.exec_(global_position)
        logger.debug("show_right_button_DRAG_CONTEXT_menu() EXIT")

    def show_right_button_DEFAULT_menu(self, global_position):
        local_position = self.viewport().mapFromGlobal(global_position)
        
        # Get the item at the position of the right-click
        item = self.itemAt(local_position)

        if item is not None:
            # Create a context menu
            menu = QMenu(self)

            if (self.parent == self.parent.parent.tab4):
                if (self.count_parents(item) == 1):  # is top level
                    action = menu.addAction("Set Player Location to this Endpoint")
                    action.triggered.connect(lambda: self.set_player_location_to_this_system(item))

            if (self.parent == self.parent.parent.tab1):
                #if top level array we want to add a menu item:
                if(self.count_parents(item) == 0): #is top level
                    action = menu.addAction("Restore a Base")
                    action.triggered.connect(lambda: self.restore_a_base(item))

                is_a_base = item.data(0, QT_DATA_IS_BASE)
                if is_a_base:
                    action = menu.addAction("Backup a Base")
                    action.triggered.connect(lambda: self.backup_a_base(item))

            if (self.parent == self.parent.parent.tab3):
                if (self.count_parents(item) == 1):  # is top level
                    action = menu.addAction("Backup this Inventory")
                    action.triggered.connect(lambda: self.backup_an_inventory(item))

                    action = menu.addAction("Replace Items from Backup")
                    action.triggered.connect(lambda: self.replace_an_inventory(item))
            
            action = menu.addAction("Toggle Expansion 2 Levels")
            action.triggered.connect(lambda: self.toggle_node_expansion(item))

            action = menu.addAction("Highlight In Text Box")
            action.triggered.connect(lambda: self.highlight_in_text_box(item))

            action = menu.addAction("Copy This Node's Text")
            action.triggered.connect(lambda: self.copy_node_text(item))

            if(self.parent == self.parent.parent.tab1 or self.parent == self.parent.parent.tab2):
                action = menu.addAction("Delete Node")
                action.triggered.connect(lambda: self.delete_node(item))

            # Show the context menu at the position of the right-click
            menu.exec_(global_position)

    def set_player_location_to_this_system(self, item):
        item_label = item.text(0)
        tab = self.parent

        model_data = self.parent.model.get_data()
        endpoint_universal_address = self.parent.tree_widget_data_to_json(item)


        self.parent.main_window.background_processing_signal.emit(4, "tab1")
        tab.update_tree_synced_indicator(False)

        # print(f"endpoint_universal_address: {endpoint_universal_address}")
        # print()
        # print()
        # print(f"Model universeAddress before: {model_data['PlayerStateData']['UniverseAddress']}")

        model_data['PlayerStateData']['UniverseAddress'] = endpoint_universal_address['UniverseAddress']

        # print(f"Model universeAddress after: {model_data['PlayerStateData']['UniverseAddress']}")
        # print(f"PlayerPositionInSystem before: {model_data['SpawnStateData']['PlayerPositionInSystem']}")

        model_data['SpawnStateData']['PlayerPositionInSystem'][0] = endpoint_universal_address['Position'][0]

        model_data['SpawnStateData']['PlayerPositionInSystem'][1] = endpoint_universal_address['Position'][1]
        #needs more testing:
        #model_data['SpawnStateData']['PlayerPositionInSystem'][1] = (
        #    str(float(endpoint_universal_address['Position'][1]) + 3)) #we'll spawn him about 10 feet (3 meters) above the recorded spot to
        #                                                               #clear anything on the ground but not too high to cause damage

        model_data['SpawnStateData']['PlayerPositionInSystem'][2] = endpoint_universal_address['Position'][2]

        # print(f"PlayerPositionInSystem after: {model_data['SpawnStateData']['PlayerPositionInSystem']}")
        #
        # print(f"LastKnownPlayerState before: {model_data['SpawnStateData']['LastKnownPlayerState']}")
        model_data['SpawnStateData']['LastKnownPlayerState'] = 'OnFoot'
        # print(f"LastKnownPlayerState before: {model_data['SpawnStateData']['LastKnownPlayerState']}")

        #pass in current tab so we only execute against this tab:
        tab.model.modelChanged.emit(tab)

        print(item_label)

        QMessageBox.information(self, f"Set Player Location", f"Player has been moved to '{item_label}'!")
        
    def copy_node_text(self, item):
        # Get the text of the selected item
        node_text = item.text(0)  # Assuming we want to copy the text in the first column

        # Copy the text to the clipboard
        clipboard = QApplication.instance().clipboard()
        clipboard.setText(node_text, QClipboard.Clipboard)

        # Optionally, also copy to the selection clipboard (useful on Linux)
        clipboard.setText(node_text, QClipboard.Selection)

    def delete_tree_nodes_selected(self):
        logger.debug("delete_tree_nodes_selected() ENTER")
        
        dialog = DeleteTreeNodesSelectedDialog(len(self.right_button_selected_nodes))

        # Show the dialog and capture the response (OK or Cancel)
        if dialog.exec_() == QDialog.Accepted:
            logger.debug("OK button clicked")
            self.parent.update_tree_synced_indicator(False)
            self.parent.set_led_based_on_app_thread_load()

            self.parent.blockSignals()
            
            for item in self.right_button_selected_nodes:
                # Check if the item has a parent
                parent = item.parent()

                if parent is not None:
                    # If the item has a parent, remove it from the parent
                    
                    #parent.removeChild(item)
                    safe_remove_qtreewidget_node(item)
                else:
                    # If no parent, the item is a top-level node
                    index = self.indexOfTopLevelItem(item)
                    if index != -1:
                        self.takeTopLevelItem(index)

            # Clear the selection list after deletion
            self.right_button_selected_nodes.clear()

            self.tree_nodes_changed_emits()
            self.parent.unblockSignals()
            
        else:
            logger.debug("Cancel button clicked")

        logger.debug("delete_tree_nodes_selected() EXIT")
   
    def tree_nodes_changed_emits(self):
        QApplication.processEvents()
        # we need everything updated because otherwise the custom top node labels end up messed up:
        # parent is a tab
        # parent.parent is the main window
        # let's tell everyone the tree changed:





        self.parent.parent.tree_changed_signal.emit()

        # now we come back and say the text changed so that the tree widget is repopulated:
        self.parent.parent.text_edit_changed_signal.emit()

    def count_parents(self, node):
        count = 0
        parent = node.parent()
        
        while parent is not None:
            count += 1
            parent = parent.parent()  # Move up to the next parent
            
        return count
    
    def highlight_in_text_box(self, item):
        logger.verbose("highlight_in_text_box() ENTER") 
        text_edit = self.parent.text_edit
        line_num = item.data(0, QT_DATA_LINE_COUNT)
        logger.verbose(f"line_num: {line_num}")
        
        #QMessageBox.information(None, "Title", f"line number {line_num}")
      
        cursor = QTextCursor(text_edit.document())
        
        # Move cursor to the start of the desired line
        cursor.movePosition(QTextCursor.Start)
        cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, line_num - 1)

        # Select the entire line
        cursor.select(QTextCursor.LineUnderCursor)
        
        # Highlight the found occurrence and update the last cursor position
        text_edit.setTextCursor(cursor)
        text_edit.ensureCursorVisible()  # Scroll to make the found text visible
        
        logger.verbose("highlight_in_text_box() EXIT")
            
    def delete_node(self, item):
        logger.debug("delete_node() ENTER")
     
        self.right_button_selected_nodes = [item]
        self.delete_tree_nodes_selected()

        logger.debug("delete_node() EXIT")

    def toggle_node_expansion(self, item):
        logger.debug("toggle_node_expansion() ENTER")
        
        # Toggle expansion of the current node
        if item.isExpanded():
            item.setExpanded(False)
        else:
            #item.setExpanded(True)    
            self.expand_node_to_level(item, 2)
            
        logger.debug("toggle_node_expansion() EXIT")            
        
    def expand_node_to_level(self, item, level):
        if level < 0:
            return

        item.setExpanded(True)

        # Recursively expand child items
        for i in range(item.childCount()):
            self.expand_node_to_level(item.child(i), level - 1)
            
    # Call this function on the top-level items of the tree widget
    def expand_tree_to_level(self, level):
        self.expand_node_to_level(self.invisibleRootItem(), level)
        
    def backup_a_base(self, item):
        logger.debug("backup_a_base() ENTER")
        #QMessageBox.information(self, "Title", "Got request to save off a base!")
        
        json_data = self.parent.tree_widget_data_to_json(item)
        base_name = json_data['Name']
        text_data = json.dumps(json_data, indent=4)
        
        # Open the save file dialog
        options = QFileDialog.Options()
        
        #mainWindow is active window; path will include the name of the last 'bases' save file at this point:
        #assume we want to use the base name for the file name:
        if not base_name:
            base_name = 'default'

        file_path_string = QApplication.instance().activeWindow().ini_file_manager.get_full_file_path(f"{base_name.strip()}")

        dialog_file_path, _ = QFileDialog.getSaveFileName(
            None, "Save File", 
            file_path_string,
            "NMS Base Files (*.nms_base.json);;All Files (*)")
            
        # If a file path is selected, save the string to the file
        if dialog_file_path:
            try:
                with open(dialog_file_path, 'w', encoding='utf-8') as file:
                    file.write(text_data)
                QMessageBox.information(None, "Success", "File saved successfully!")
            except Exception as e:
                QMessageBox.critical(None, "Error", f"Failed to save file: {str(e)}")
        
        logger.debug("backup_a_base() EXIT")

    def restore_a_base(self, item):
        logger.debug("restore_a_base() ENTER")
        file_content = None
        
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly

        path_string = QApplication.instance().activeWindow().ini_file_manager.get_persistent_dir()

        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Restore A Base To First Position In Tree",
            path_string,
            "NMS Base Files (*.nms_base.json);;All Files (*)",
            options = options)
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    file_content = file.read()  # Reads the entire file as a string

            except Exception as e:
                # If there's an error reading the file, show an error message
                error_dialog = QMessageBox()
                error_dialog.setText(f"Error reading file: {str(e)}")
                error_dialog.exec_()
                
        if file_content:
            self.parent.update_tree_synced_indicator(False)
            self.parent.set_led_based_on_app_thread_load()

            nms_base_json = json.loads(file_content)
            self.parent.view.add_base(nms_base_json)

            dialog = QMessageBox()
            dialog.setText(f"New Base Added To Tree!")
            dialog.exec_()
        else:
            dialog = QMessageBox()
            dialog.setText(f"File Data May Not Exist. New Base Could NOT Be Added To Tree!")
            
        logger.debug("restore_a_base() EXIT")

    def backup_an_inventory(self, item):
        logger.debug("backup_an_inventory() ENTER")
        # QMessageBox.information(self, "Title", "Got request to save off a base!")

        json_data = self.parent.tree_widget_data_to_json(item)
        inventory_name = json_data['Name']
        text_data = json.dumps(json_data, indent=4)

        # Open the save file dialog
        options = QFileDialog.Options()

        # mainWindow is active window; path will include the name of the last 'bases' save file at this point:
        # assume we want to use the base name for the file name:

        if not inventory_name:
            inventory_name = 'default'

        file_path_string = QApplication.instance().activeWindow().ini_file_manager.get_full_file_path(f"{inventory_name.strip()}")

        print (file_path_string)

        dialog_file_path, _ = QFileDialog.getSaveFileName(
            None, "Save File",
            file_path_string,
            "NMS Inventory Files (*.nms_inventory.json);;All Files (*)")

        # If a file path is selected, save the string to the file
        if dialog_file_path:
            try:
                with open(dialog_file_path, 'w', encoding='utf-8') as file:
                    file.write(text_data)
                QMessageBox.information(None, "Success", "File saved successfully!")
            except Exception as e:
                QMessageBox.critical(None, "Error", f"Failed to save file: {str(e)}")

        logger.debug("backup_an_inventory() EXIT")

    def replace_an_inventory(self, item):
        logger.debug("replace_an_inventory() ENTER")
        file_content = None

        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly

        path_string = QApplication.instance().activeWindow().ini_file_manager.get_persistent_dir()

        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Replace Inventory Contents",
            path_string,
            "NMS Inventory Files (*.nms_inventory.json);;All Files (*)",
            options = options)

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    file_content = file.read()  # Reads the entire file as a string

            except Exception as e:
                # If there's an error reading the file, show an error message
                error_dialog = QMessageBox()
                error_dialog.setText(f"Error reading file: {str(e)}")
                error_dialog.exec_()

        if file_content:
            self.parent.update_tree_synced_indicator(False)
            self.parent.set_led_based_on_app_thread_load()

            nms_inventory_json = json.loads(file_content)
            self.parent.view.replace_inventory(nms_inventory_json, item)

            dialog = QMessageBox()
            dialog.setText(f"Inventory Contents Replaced!")
            dialog.exec_()
        else:
            dialog = QMessageBox()
            dialog.setText(f"File Data May Not Exist. New Base Could NOT Be Added To Tree!")

        logger.debug("replace_an_inventory() EXIT")

    def set_node_first_in_tree(self, node, new_parent):
        if node and new_parent:
            # Step 1: Remove freighter_node from its current parent, if it has one
            current_parent = node.parent()
            if current_parent:
                index = current_parent.indexOfChild(node)
                if index != -1:
                    current_parent.takeChild(index)
            else:
                # If the freighter_node is a top-level item, remove it from the tree widget
                tree_widget = node.treeWidget()
                if tree_widget:
                    index = tree_widget.indexOfTopLevelItem(node)
                    if index != -1:
                        tree_widget.takeTopLevelItem(index)

            # Step 2: Insert freighter_node at the top of new_parent's children
            new_parent.insertChild(0, node)

    def dropEvent(self, event):
        logger.debug("==================== DROP EVENT START ====================")
        #super().dropEvent(event)  # Call the base class dropEvent to handle basic drop logic
        #QApplication.processEvents()  # Process pending UI events to refresh the interface

        tab = self.parent

        tab.update_tree_synced_indicator(False)
        tab.set_led_based_on_app_thread_load()

        # Get the item being dragged
        dragged_item = self.currentItem()
        if not dragged_item:
            logger.debug("No dragged item found")
            event.ignore()
            logger.debug("==================== DROP EVENT END (IGNORED) ====================")
            return

        # Get the item where we're dropping
        drop_target = self.itemAt(event.pos())
        
        if not drop_target:
            logger.debug("No drop target found")
            event.ignore()
            logger.debug("==================== DROP EVENT END (IGNORED) ====================")
            return
            
        if not self.areParentsDataSameType(dragged_item, drop_target):
            logger.debug("=====dragged_item, drop_target parents were not of same type; leaving DROP EVENT=======")
            QMessageBox.information(self, "Error", "Dragged Item and Drop Target parents must exist and be of the same data type; Aborting Drag and Drop!")
            return
            
        if not self.areParentsArrayOrDict(dragged_item, drop_target):
            logger.debug("=====parents were not array or dict data types; leaving DROP EVENT=======")
            QMessageBox.information(self, "Error", "Parents must be Arrays or Dictionary data types; Aborting Drag and Drop!")
            return     
 
        if self.wouldBeLastChild(dragged_item):
            logger.debug("=====dragged item would have been last Child; leaving DROP EVENT=======")
            QMessageBox.information(self, "Error", "Dragged Item must not be the last Child under a Parent; Aborting Drag and Drop!")
            return

        logger.verbose(f"Dragged item: {dragged_item.text(0)}")
        logger.verbose(f"Drop target: {drop_target.text(0)}")

        # Log the entire tree structure before the move
        logger.verbose("Tree structure before move:")
        self.log_tree_structure()

        # Determine if we're dropping above or below the target
        drop_position = self.dropIndicatorPosition()
        logger.verbose(f"Drop indicator position: {drop_position}")

        # Get the parent of the drop target
        new_parent = drop_target.parent() or self.invisibleRootItem()
        logger.verbose(f"New parent: {new_parent.text(0) if isinstance(new_parent, QTreeWidgetItem) else 'Root'}")

        # Determine the new index
        new_index = self.getNewIndex(dragged_item, drop_target, new_parent)

        # Remove the dragged item from its original position
        old_parent = dragged_item.parent() or self.invisibleRootItem()
        old_index = old_parent.indexOfChild(dragged_item)
        logger.verbose(f"Old parent: {old_parent.text(0) if isinstance(old_parent, QTreeWidgetItem) else 'Root'}")
        logger.verbose(f"Old index: {old_index}")
        
        # Check if we're moving within the same parent
        if old_parent == new_parent and old_index < new_index:
            new_index -= 1
            logger.verbose(f"Adjusted new index for same parent move: {new_index}")

        logger.verbose(f"About to take child from old parent at index {old_index}")        
        
        item = old_parent.takeChild(old_index)
             
        if item:
            logger.verbose(f"Successfully took child: {item.text(0)}")
        else:
            logging.error("Failed to take child from old parent")
            event.ignore()
            logger.debug("==================== DROP EVENT END (IGNORED) ====================")
            return

        # Insert the dragged item at the new position
        logger.verbose(f"About to insert child to new parent at index {new_index}")
        new_parent.insertChild(new_index, item)

        logger.verbose(f"Item moved from index {old_index} to {new_index}")

        # Log the entire tree structure after the move
        logger.verbose("Tree structure after move:")
        self.log_tree_structure()
        QApplication.processEvents()  # Process pending UI events to refresh the interface

        tab.blockSignals()
        tab.update_model_from_tree()
        tab.unblockSignals()

        tab.model.modelChanged.emit(tab)

        logger.debug("==================== DROP EVENT END ====================")
        self.log_tree_structure()

    def wouldBeLastChild(self, dragged_item):  
        parent1 = dragged_item.parent()
        if(parent1.childCount() == 1):
            logger.verbose("Dragged_item would be last child of a parent");
            return True
        else:
            logger.verbose("Dragged_item would NOT be last child of a parent");
            return False
        
    def areParentsDataSameType(self, dragged_item, drop_target):
        parent1 = dragged_item.parent()
        parent2 = drop_target.parent()
        
        if parent1 == None or parent2 == None:
            logger.verbose(f"=========areParentsSameType() One of parents was Null, Returning False")
            return False
            
        parent1Data = parent1.data(0, QT_DATA_SAVE_NODES_DATA_STRUCT)
        parent2Data = parent2.data(0, QT_DATA_SAVE_NODES_DATA_STRUCT)         
              
        logger.verbose(f"==========areParentsSameType() Result: {type(parent1Data) == type(parent2Data)}")
        return type(parent1Data) == type(parent2Data)
        
    def areParentsArrayOrDict(self, dragged_item, drop_target):
        #function assumes we already know the parents ARE the SAME data type from previous check! 
        parent1 = dragged_item.parent()
        
        if parent1 == None:
            logger.debug(f"=========parentsNotArrayOrDict() One of parents was Null, Returning False")
            return False
            
        parent1Data = parent1.data(0, QT_DATA_SAVE_NODES_DATA_STRUCT)
              
        logger.debug(f"==========areParentsArrayOrDict Result: {isinstance(parent1Data, (list, dict))}")
        return isinstance(parent1Data, (list, dict)) 

    def getNewIndex(self, dragged_item, drop_target, new_parent):
        parent1 = dragged_item.parent()
        parent2 = drop_target.parent()
        new_index = 0
        
        if parent1 is parent2:
            if new_parent.indexOfChild(dragged_item) > new_parent.indexOfChild(drop_target):
                new_index = new_parent.indexOfChild(drop_target)
            else:
                new_index = new_parent.indexOfChild(drop_target) + 1
        else:
            #just stick it in below. End user can move drag it again within same parent to reposition:
            new_index = new_parent.indexOfChild(drop_target) + 1
            
        return new_index
 
    def refresh_view(self, item): 
        logger.debug("Refreshing view")
        self.dataChanged(self.indexFromItem(item), self.indexFromItem(item))
        self.update()
        self.scrollToItem(item)
        self.model().layoutChanged.emit()
        self.viewport().update()
        self.repaint()  # Force an immediate repaint
        QApplication.processEvents()  # Process any pending events

    def log_tree_structure(self, item=None, level=0):
        if item is None:
            item = self.invisibleRootItem()
        
        for i in range(item.childCount()):
            child = item.child(i)
            logger.verbose(f"Next Child in Tree Structure: {'  ' * level}{child.text(0)}")
            self.log_tree_structure(child, level + 1)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('application/x-qabstractitemmodeldatalist'):
            event.accept()
        else:
            event.ignore()

    """
    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat('application/x-qabstractitemmodeldatalist'):
            event.accept()
        else:
            event.ignore()
    """
    
    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat('application/x-qabstractitemmodeldatalist'):
            event.accept()
        else:
            event.ignore()

        rect = self.viewport().rect()
        mouse_pos = event.pos()
        scroll_threshold = 20

        if mouse_pos.y() < rect.top() + scroll_threshold:
            self.scroll_direction = -1  # Scroll up
            self.scroll_timer.start(25)  # Start scrolling every 20 ms
        elif mouse_pos.y() > rect.bottom() - scroll_threshold:
            self.scroll_direction = 1  # Scroll down
            self.scroll_timer.start(25)
        else:
            self.scroll_timer.stop()  # Stop scrolling if not near the edges

    def perform_smooth_scroll(self):
        if self.scroll_direction is not None:
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() + self.scroll_direction)
            
    """
    def paintEvent(self, event):
        logger.debug("paintEvent started")
        super().paintEvent(event)
        logger.debug("paintEvent completed")
    """

    def onDataChanged(self, topLeft, bottomRight, roles):
        logger.debug("dataChanged signal emitted")

    def onLayoutAboutToBeChanged(self):
        logger.debug("layoutAboutToBeChanged signal emitted")

    def onLayoutChanged(self):
        logger.debug("layoutChanged signal emitted")

    def onRowsInserted(self, parent, first, last):
        logger.debug(f"rowsInserted signal emitted: {first} to {last}")

    def onRowsMoved(self, parent, start, end, destination, row):
        logger.debug(f"rowsMoved signal emitted: {start} to {end}, new position {row}")

    def onRowsRemoved(self, parent, first, last):
        logger.debug(f"rowsRemoved signal emitted: {first} to {last}") 
        
        
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


    
        