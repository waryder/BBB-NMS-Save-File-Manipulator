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
        label.setStyleSheet("QLabel { color : red; }")
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
        self.first_tab_obj = parent        
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
            
            highlight_in_text_box_action = menu.addAction("Highlight In Text Box")
            highlight_in_text_box_action.triggered.connect(lambda: self.highlight_in_text_box(item))
            
            toggle_expand_action = menu.addAction("Toggle Expansion 2 Levels")
            toggle_expand_action.triggered.connect(lambda: self.toggle_node_expansion(item))
            
            #if top level array we want to add a menu item:
            if(self.count_parents(item) == 0): #is top level    
                toggle_expand_action = menu.addAction("Restore a Base")
                toggle_expand_action.triggered.connect(lambda: self.restore_a_base(item))            
            
            is_a_base = item.data(0, QT_DATA_IS_BASE)
            if is_a_base: 
                toggle_expand_action = menu.addAction("Backup a Base")
                toggle_expand_action.triggered.connect(lambda: self.backup_a_base(item))
            
            delete_action = menu.addAction("Delete Node")
            delete_action.triggered.connect(lambda: self.delete_node(item))

            # Show the context menu at the position of the right-click
            menu.exec_(global_position) 
        
    def delete_tree_nodes_selected(self):
        logger.debug("delete_tree_nodes_selected() ENTER")
        
        dialog = DeleteTreeNodesSelectedDialog(len(self.right_button_selected_nodes))

        # Show the dialog and capture the response (OK or Cancel)
        if dialog.exec_() == QDialog.Accepted:
            logger.debug("OK button clicked")
            self.first_tab_obj.blockSignals()
            
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
            self.first_tab_obj.update_status_indicator_to_green(False)
            
            self.first_tab_obj.sync_text_from_tree_window()
            
            #leaving this up to the end user with the next live line of code
            #self.first_tab_obj.update_tree_from_model()
            self.first_tab_obj.update_tree_synced_indicator(False)            
            self.first_tab_obj.unblockSignals()
            
        else:
            logger.debug("Cancel button clicked")

        logger.debug("delete_tree_nodes_selected() EXIT")
        
   
    def count_parents(self, node):
        count = 0
        parent = node.parent()
        
        while parent is not None:
            count += 1
            parent = parent.parent()  # Move up to the next parent
            
        return count
    
    def highlight_in_text_box(self, item):
        logger.verbose("highlight_in_text_box() ENTER") 
        text_edit = self.first_tab_obj.text_edit
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
        
        json_data = self.first_tab_obj.tree_widget_data_to_json(item)
        base_name = json_data['Name']
        text_data = json.dumps(json_data, indent=4)
        
        
        # Open the save file dialog
        options = QFileDialog.Options()
        
        #file_path, _ = QFileDialog.getSaveFileName(None, "Save File", base_name, "NMS Base Files (*.nms_base.json);;All Files (*)", options=options)
        
        #mainWindow is active window; path will include the name of the last 'bases' save file at this point:
        path_string = QApplication.instance().activeWindow().ini_file_manager.get_last_working_file_path()
        #chop off the file_name so we have just the path:
        path_string = os.path.dirname(path_string)
        #assume we want to use the base name for the file name:
        path_string += f"\\{base_name}"
        
        file_path, _ = QFileDialog.getSaveFileName(
            None, "Save File", 
            path_string, 
            "NMS Base Files (*.nms_base.json);;All Files (*)")
            
        # If a file path is selected, save the string to the file
        if file_path:
            try:
                with open(file_path, 'w') as file:
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
        file_path, _ = QFileDialog.getOpenFileName(None, "Restore A Base To First Position In Tree", "", "NMS Base Files (*.nms_base.json);;All Files (*)", options=options)
        
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    file_content = file.read()  # Reads the entire file as a string

            except Exception as e:
                # If there's an error reading the file, show an error message
                error_dialog = QMessageBox()
                error_dialog.setText(f"Error reading file: {str(e)}")
                error_dialog.exec_()
                
        if file_content:              
            nms_base_json = json.loads(file_content)
            self.first_tab_obj.model.add_base(nms_base_json)
            dialog = QMessageBox()
            dialog.setText(f"New Base Added To Tree!")
            dialog.exec_()
        else:
            dialog = QMessageBox()
            dialog.setText(f"File Data May Not Exist. New Base Could NOT Be Added To Tree!")
            
        logger.debug("restore_a_base() EXIT")   
        
    def dropEvent(self, event):
        logger.debug("==================== DROP EVENT START ====================")
        
        self.first_tab_obj.set_led_based_on_app_thread_load()
        
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

        #Let us handle the updates so we know what's going on
        self.first_tab_obj.blockSignals() 
        
        logger.verbose(f"Model Text before update_model_from_tree(): {self.first_tab_obj.model.get_text()}")
        #update the model from the new Tree structure
        self.first_tab_obj.update_model_from_tree()
        logger.verbose(f"Model Text after update_model_from_tree(): {self.first_tab_obj.model.get_text()}")
        
        #update the text widget
        self.first_tab_obj.update_text_widget_from_model()    
        self.first_tab_obj.unblockSignals()
        self.setCurrentItem(item)

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