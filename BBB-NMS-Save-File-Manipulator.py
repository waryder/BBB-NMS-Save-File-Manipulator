import sys, os, pdb, logging, json, traceback, configparser, pyautogui
from PyQt5.QtCore import pyqtSignal, QObject, Qt, QMimeData, QTimer
from PyQt5.QtWidgets import (QApplication, QMainWindow, QSplitter, QTabWidget,
                             QTextEdit, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QAction,
                             QTreeWidget, QTreeWidgetItem, QPushButton, QFileDialog, QMessageBox,
                             QAbstractItemView, QDialog, QLineEdit, QInputDialog, QMenu)
from PyQt5.QtGui import (QClipboard, QDragEnterEvent, QDropEvent, QDragMoveEvent, QDrag, QTextCursor,
                        QColor, QPalette)
from PyQt5.QtCore import Qt # Import the Qt namespace
from PyQt5 import QtCore, QtGui, QtWidgets


# Define a new logging level called VERBOSE with a numeric value lower than DEBUG (5)
VERBOSE = 5
logging.addLevelName(VERBOSE, "VERBOSE")
# Add VERBOSE as a reference to the logging module
logging.VERBOSE = VERBOSE

def verbose(self, message, *args, **kwargs):
    if self.isEnabledFor(VERBOSE):
        self._log(VERBOSE, message, args, **kwargs)

logging.Logger.verbose = verbose

# Set up logging to include VERBOSE level messages
logging.basicConfig(level=logging.ERROR, format='line %(lineno)d - %(asctime)s - %(levelname)s - %(message)s')

# Get a logger instance
logger = logging.getLogger(__name__)



def global_exception_handler(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        # Let KeyboardInterrupt exceptions pass through without logging
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    # Print the error and traceback
    print(f"Unhandled exception: {exc_value}")
    traceback.print_exception(exc_type, exc_value, exc_traceback)
    
def get_new_QTreeWidgetItem():
    widget = QTreeWidgetItem()
    widget.setFlags(widget.flags() | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled)  # Make item drag and droppable Qt.ItemIsEditable
    return widget
    
def copy_to_clipboard(model, parentWindow = None):
    clipboard = QApplication.clipboard()
    clipboard.setText(model.get_text())
    QMessageBox.information(parentWindow, "Copied", "Text copied to clipboard!") 
    
        
class TextSearchDialog(QDialog):  # Change QWidget to QDialog
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("Search Dialog")

        # Create a line edit for search input
        self.line_edit = QLineEdit(self)
        self.line_edit.setPlaceholderText("Enter search term")

        # Create buttons for search and cancel
        self.search_button = QPushButton("Search", self)
        self.cancel_button = QPushButton("Cancel", self)

        # Layout to hold widgets
        layout = QVBoxLayout()
        layout.addWidget(self.line_edit)
        layout.addWidget(self.search_button)
        layout.addWidget(self.cancel_button)
        self.setLayout(layout)

        # Connect buttons to respective methods
        self.search_button.clicked.connect(self.perform_search)
        self.cancel_button.clicked.connect(self.reject)  # Use reject() for canceling

    def perform_search(self):
        search_string = self.line_edit.text()
        self.parent().handle_search_input(search_string)  # Handle search in parent
        #self.accept()  # Close the dialog upon successful search
        

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
        self.customContextMenuRequested.connect(self.show_context_menu)
        
    def show_context_menu(self, position):
        # Get the item at the position of the right-click
        item = self.itemAt(position)

        if item is not None:
            # Create a context menu
            menu = QMenu(self)

            # Add an action to toggle expansion of the selected node
            toggle_expand_action = menu.addAction("Toggle Expansion 2 Levels")
            toggle_expand_action.triggered.connect(lambda: self.toggle_node_expansion(item))
            
            # Add an action to delete the selected node and its children
            delete_action = menu.addAction("Delete Node")
            delete_action.triggered.connect(lambda: self.delete_node(item))

            # Show the context menu at the position of the right-click
            menu.exec_(self.viewport().mapToGlobal(position))
            
    def delete_node(self, item):
        # Get the parent of the item
        parent = item.parent()

        # If the item has a parent, remove it from the parent
        if parent is not None:
            parent.removeChild(item)
        else:
            # If no parent, the item is a top-level node
            index = self.tree_widget.indexOfTopLevelItem(item)
            if index != -1:
                self.tree_widget.takeTopLevelItem(index)

        self.first_tab_obj.sync_text_from_tree_window()      
        

    def toggle_node_expansion(self, item):
        # Toggle expansion of the current node
        if item.isExpanded():
            item.setExpanded(False)
        else:
            #item.setExpanded(True)    
            self.expand_node_to_level(item, 2)
        
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

    def dropEvent(self, event):
        logger.debug("==================== DROP EVENT START ====================")
        
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
        self.first_tab_obj.reset_tab_text_content_from_model()    
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
            
        parent1Data = parent1.data(0, Qt.UserRole)
        parent2Data = parent2.data(0, Qt.UserRole)         
              
        logger.verbose(f"==========areParentsSameType() Result: {type(parent1Data) == type(parent2Data)}")
        return type(parent1Data) == type(parent2Data)
        
    def areParentsArrayOrDict(self, dragged_item, drop_target):
        #function assumes we already know the parents ARE the SAME data type from previous check! 
        parent1 = dragged_item.parent()
        
        if parent1 == None:
            logger.debug(f"=========parentsNotArrayOrDict() One of parents was Null, Returning False")
            return False
            
        parent1Data = parent1.data(0, Qt.UserRole)
              
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

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat('application/x-qabstractitemmodeldatalist'):
            event.accept()
        else:
            event.ignore()
            
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
 
      

# Set the global exception handler
sys.excepthook = global_exception_handler

INIT_TEXT = """[
    {
        "BaseVersion":8,
        "OriginalBaseVersion":8,
        "GalacticAddress":5068787278259680,
        "Position":[
            4566.828125,
            -28771.09375,
            -94145.3125
        ],
        "Forward":[
            0.07187037914991379,
            -0.9528860449790955,
            0.29469117522239687
        ]
    }
]
"""

            
# Parent Class: DataModel
class DataModel(QObject):
    # Define the signal to be emitted when text changes (can be inherited)
    # (Dude I don't know. Python wants this out here even though it is treated like an instance variable
    # when declared this way. ChatGPT couldn't explain it to me. Just know: this thing is treated like
    # an instance variable for the life of the app:
    modelChanged = pyqtSignal()
    
    
    def __init__(self, ini_file_manager):
        logger.debug("DataModel(QObject).__init__ ENTER")
        super().__init__()
        self.model_data = None
        
        # Check if a file exists in the ini manager's last saved path
        self.last_file_path = ini_file_manager.get_last_working_file_path()
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
            

# Subclass: JsonArrayModel
class JsonArrayModel(DataModel):
    def __init__(self, ini_file_manager):
        logger.debug("JsonArrayModel(DataModel).__init__ ENTER")
        super().__init__(ini_file_manager)
        self.init_model_data()
        
        logger.debug("JsonArrayModel(DataModel).__init__ EXIT")        
        
    def init_model_data(self):
        if self.last_file_path and os.path.exists(self.last_file_path):
            # If the file exists, load its contents
            try:
                with open(self.last_file_path, 'r') as file:
                    self.model_data = json.loads(file.read())
            except Exception as e:
                print(f"Failed to load text from {self.last_file_path}: {e}")
                self.model_data = json.loads(INIT_TEXT)
        else:
            # Fall back to INIT_TEXT if no file path is found or the file doesn't exist
            self.model_data = json.loads(INIT_TEXT)
            
        #we need all values to be treated as strings:
        self.convert_values_to_strings_in_place(self.model_data)    
        
            
    def convert_values_to_strings_in_place(self, obj):
        if isinstance(obj, dict):
            # Recursively convert values in dictionaries (in place)
            for k, v in obj.items():
                obj[k] = self.convert_values_to_strings_in_place(v)
        elif isinstance(obj, list):
            # Recursively convert items in lists (in place)
            for i in range(len(obj)):
                obj[i] = self.convert_values_to_strings_in_place(obj[i])
        else:
            # Convert everything else (numbers, booleans, etc.) to strings
            if not isinstance(obj, str):
                obj = str(obj)

            return obj

        return obj  # Return the modified object for recursion consistency       
                

    # Override the stubbed accessor functions
    def get_text(self):
        return json.dumps(self.model_data, indent=4)

    def set_text(self, text):
        json_dumps = json.dumps(self.model_data)
        
        if text != json_dumps:  # Emit signal only if text is actually changed
            self.model_data = json_dumps
            self.modelChanged.emit()

    def get_json(self):
        return self.model_data
        
    def set_json(self, json_array):
        if json_array != self.model_data:  # Emit signal only if JSON data is actually changed
            self.model_data = json_array
            self.modelChanged.emit()
            

class BaseTabContent(QWidget):
    def __init__(self, model, tab_name):
        super().__init__()
        self.model = model
        self.tab_name = tab_name

    def reset_tab_text_content_from_model(self):
        pass

    def set_model_from_text_widget(self):
        pass
        
    def blockSignals(self):
        pass
        
    def unblockSignals(self):
        pass        


class FirstTabContent(BaseTabContent):
    def __init__(self, model, tab_name, parent=None):
        self.main_window = parent
        super().__init__(model, tab_name)
        self.init_ui()

    def init_ui(self):
        self.search_dialog = None

        # Set static width for buttons
        button_width = 140
                          
#left pane:
        self.left_button = QPushButton("Synch from Text Window")
        self.left_button.setFixedWidth(button_width) 
        
        self.sort_bases_by_gal_sys_name_button = QPushButton("Sort By Gal, Sys, Name")
        self.sort_bases_by_gal_sys_name_button.setFixedWidth(button_width)
        
        # Create tree widget and text edit
        #self.tree_widget = QTreeWidget()
        self.tree_widget = CustomTreeWidget(self)
        self.tree_widget.setHeaderHidden(True)
        
        # Create layout for the buttons to be horizontal
        left_buttons_lo = QHBoxLayout()
        left_buttons_lo.addWidget(self.left_button)
        left_buttons_lo.addWidget(self.sort_bases_by_gal_sys_name_button)

        # Set alignment
        left_buttons_lo.setAlignment(Qt.AlignLeft)

        # Create a vertical layout for the left side and add buttons layout
        left_button_layout = QVBoxLayout()
        
        # Create layouts for buttons
        left_button_layout = QVBoxLayout()
        left_button_layout.addLayout(left_buttons_lo)
        left_button_layout.addWidget(self.tree_widget)
        
        left_container = QWidget()
        left_container.setLayout(left_button_layout)
        
#right pane: 
        self.right_button = QPushButton("Synch from Tree Window")
        self.right_button.setFixedWidth(button_width)
        
        self.copy_button = QPushButton("Copy to Clipboard")  # New button for copying text
        self.copy_button.setFixedWidth(button_width)
        
        self.text_edit = QTextEdit()
        
        #Customize the palette to keep the selection highlighted when the window loses focus.
        #This also solved that on search, the found text was not highlighting. I didn't track down
        #the root cause of that since changing the default behavior of not highlighting on loss of focus
        #is what I want anyhow and solves that original issue.
        palette = self.text_edit.palette()
        palette.setColor(QPalette.Inactive, QPalette.Highlight, palette.color(QPalette.Active, QPalette.Highlight))
        palette.setColor(QPalette.Inactive, QPalette.HighlightedText, palette.color(QPalette.Active, QPalette.HighlightedText))
        self.text_edit.setPalette(palette)
        
        # Enable custom context menu
        self.text_edit.setContextMenuPolicy(Qt.CustomContextMenu)
        self.text_edit.customContextMenuRequested.connect(self.show_context_menu)
                
        self.text_edit.setText(self.model.get_text())

        right_pane_layout = QVBoxLayout()
        right_button_layout = QHBoxLayout()
        right_button_layout.setAlignment(Qt.AlignLeft)
        right_button_layout.setSpacing(2)
        #right_button_layout.addWidget(self.right_button)
        right_button_layout.addWidget(self.copy_button)
        right_pane_layout.addLayout(right_button_layout)
        right_pane_layout.addWidget(self.text_edit)

        right_container = QWidget()
        right_container.setLayout(right_pane_layout)
        
#Set up the main window:        
        self.splitter = QSplitter(Qt.Horizontal)  # Set the orientation to horizontal

        # Add both containers to the splitter
        self.splitter.addWidget(left_container)
        self.splitter.addWidget(right_container)

        # Set initial splitter size ratios (optional)
        self.splitter.setStretchFactor(0, 5)  # Left pane takes more space
        self.splitter.setStretchFactor(1, 5)  # Right pane takes less space

        # Set the splitter as the main layout for the widget
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.splitter)

        # Set the layout to the widget
        self.setLayout(main_layout)

        # Connect buttons to methods
        self.left_button.clicked.connect(self.sync_from_text_window)
        self.sort_bases_by_gal_sys_name_button.clicked.connect(self.sort_bases_by_gal_sys_name)
        self.right_button.clicked.connect(self.sync_text_from_tree_window)
        self.copy_button.clicked.connect(lambda: copy_to_clipboard(self.model, self))        
        
        # Update tree from model
        self.update_tree_from_model()
        #self.tree_widget.expandAll()
        self.tree_widget.expand_tree_to_level(1)
        
        # Connect text edit changes to model
        self.text_edit.textChanged.connect(self.set_model_from_text_widget)
        self.model.modelChanged.connect(self.model_changed)
        
            
       
    def show_context_menu(self, position):
        # Create the default context menu
        context_menu = self.text_edit.createStandardContextMenu()

        # Add a search option
        search_action = context_menu.addAction("Search Text")

        # Connect the search option to a function that performs the search
        search_action.triggered.connect(self.search_text)

        # Show the context menu
        context_menu.exec_(self.text_edit.mapToGlobal(position))

    def search_text(self):       
        logger.debug("search_text() ENTER")
        # Prompt the user to enter a search string
        self.open_initial_text_search_dialog()
        logger.debug("search_text() EXIT")

    def handle_search_input(self, search_string):
        if search_string:
            self.current_search_string = search_string
            self.last_cursor_position = self.text_edit.textCursor()
            self.find_next_occurrence()            

    def open_initial_text_search_dialog(self):
        logger.debug("open_initial_text_search_dialog() ENTER")

        self.search_dialog = TextSearchDialog(self)
        self.search_dialog.show()
        logger.debug("open_initial_text_search_dialog() EXIT")
        
    def find_next_occurrence(self):
        logger.debug("find_next_occurrence() ENTER")
        """
        Searches for the next occurrence of the current search string starting 
        from the last found position.
        """
        if not self.current_search_string:
            return  # If no search string is set, return

        # Get the QTextDocument object and continue searching from the current cursor position
        document = self.text_edit.document()
        cursor = document.find(self.current_search_string, self.text_edit.textCursor())
        logger.verbose(f"Selection start and end: {cursor.selectionStart()}, {cursor.selectionEnd()}")
        

        # If no more occurrences are found, show a dialog box
        if cursor.isNull():
            self.text_edit.setTextCursor(self.last_cursor_position)  # Reset the text cursor
            self.show_no_more_matches_dialog()
        else:
            
            # Highlight the found occurrence and update the last cursor position
            self.text_edit.setTextCursor(cursor)
            
            self.text_edit.ensureCursorVisible()  # Scroll to make the found text visible
            self.last_cursor_position = self.text_edit.textCursor()  # Update the last position
            
        logger.debug("find_next_occurrence() EXIT")


    # New method to show a dialog when no more matches are found
    def show_no_more_matches_dialog(self):
        """
        Shows a message box when no more occurrences of the search string are found.
        """
        QMessageBox.information(self, "End of Search", "No more occurrences found.")        
        
    def blockSignals(self):
        logger.debug("blockSignals() ENTER")
        
        self.text_edit.blockSignals(True)
        self.tree_widget.blockSignals(True)
        self.model.blockSignals(True)
        logger.debug("blockSignals() ENTER")
        
    def unblockSignals(self):
        logger.debug("unblockSignals() ENTER")
        self.text_edit.blockSignals(False)
        self.tree_widget.blockSignals(False)
        self.model.blockSignals(False)
        logger.debug("unblockSignals() ENTER")        
        
    def repaint_tree(self):
        logger.debug(f"repainting tree...")
        self.tree_widget.repaint()
        
    def model_changed(self):
        logger.debug(f"Model Changed.")
        logger.verbose(f"Now: {self.model.get_text()}")        

    def sync_from_text_window(self):
        logger.debug("Sync from Text Window")
        # Set tree from text
        try:
            json_data = json.loads(self.text_edit.toPlainText())
            self.clear_tree_view()
            self.populate_tree_from_json(json_data)
            self.tree_widget.expand_tree_to_level(1)
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Error", f"Failed to parse JSON from text window: {e}")
            
    def sort_bases_by_gal_sys_name(self):
        logger.debug("Sort Bases clicked")
        model_json = self.model.get_json()
        
        if(logging.getLogger().getEffectiveLevel() == logger.verbose):
            for el in model_json:
                logger.verbose(f"Gal: {el['GalacticAddress'][7:8]}, {Sys: el['GalacticAddress'][3:6]}, {el['Name']}")
        
        # Sort model_json in place based on the desired key
        model_json.sort(key=lambda el: (
            int(el['GalacticAddress'][7:8], 16),  # galaxy (characters 5 and 6)
            int(el['GalacticAddress'][3:6], 16),  # system (characters 2 to 4)
            el['Name']                   # base_name
        ))
        
        if(logging.getLogger().getEffectiveLevel() == logger.verbose):
            for el in model_json:
                logger.verbose(f"Gal: {el['GalacticAddress'][7:8]}, {Sys: el['GalacticAddress'][3:6]}, {el['Name']}")
        
        self.update_tree_from_model()
        self.tree_widget.expand_tree_to_level(1)
        self.reset_tab_text_content_from_model()        

    def sync_text_from_tree_window(self):
        logger.debug("Sync from Tree Window clicked")
        self.update_model_from_tree()
        self.reset_tab_text_content_from_model()        

    def set_model_from_text_widget(self):
        logger.debug("1st Tab set_model_from_text_widget() enter")
        new_text = self.text_edit.toPlainText()
        self.model.set_text(new_text)
        logger.debug("1st Tab set_model_from_text_widget() exit")

    def populate_tree(self, data, parent=None):
        if parent is None:
            parent = self.tree_widget.invisibleRootItem()

        if isinstance(data, dict):
            for key, value in data.items():
                item = QTreeWidgetItem([key])
                parent.addChild(item)
                self.populate_tree(value, item)
        elif isinstance(data, list):
            for index, value in enumerate(data):
                item = QTreeWidgetItem([f"Item {index}"])
                parent.addChild(item)
                self.populate_tree(value, item)

    def reset_tab_text_content_from_model(self):
        logger.debug("1st Tab reset_tab_text_content_from_model() enter")
        self.blockSignals()
        self.text_edit.setText(self.model.get_text())
        self.unblockSignals()
        logger.debug("1st Tab reset_tab_text_content_from_model() exit")
  
    def update_tree_from_model(self):
        logger.debug("update_tree_from_model() called")
        
        json_data = self.load_json_from_model()
        if json_data is not None:
            
            self.blockSignals()
            self.clear_tree_view()
            self.populate_tree_from_json(json_data)
            self.unblockSignals()
            
            logger.debug("Tree view updated with model data.")            
            
    def update_model_from_tree(self):
        logger.debug(f"update_model_from_tree() ENTER")
        # To start from the root and traverse the whole tree:
        tree_data = self.tree_widget_data_to_json()
       
        logger.verbose(f"tree string: {tree_data}")
        self.model.set_json(tree_data)
        
    def tree_widget_data_to_json(self): 
        def parse_item(tree_node, depth):
            node_data = tree_node.data(0, Qt.UserRole)
            
            logger.verbose(f"\n\nDepth: {depth}")            
            logger.verbose(f"current node data: {node_data}, data type={type(node_data)}")
            logger.verbose(f"current node.childCount()={tree_node.childCount()}")
                          
            if(isinstance(node_data, list)):
                output = []
                                                                        
                for i in range(tree_node.childCount()):
                    child_node = tree_node.child(i)
                    output.append(parse_item(child_node, depth + 1))

                return output   
                
            if(isinstance(node_data, dict)):
                output = {}
                
                for i in range(tree_node.childCount()):
                    child_node = tree_node.child(i) #these will be tuples
                    result = parse_item(child_node, depth + 1)
                    output[result[0]] = result[1]
                    
                logger.verbose(f"\n\nResult: {output}")

                return output   
             
            if(isinstance(node_data, tuple)):
                output = ()
                
                key = tree_node.child(0).data(0, Qt.UserRole)
                value = parse_item(tree_node.child(1), depth + 1) #go send the value nodes back around...
                
                output = (key, value)
                return output                

            else:                
                logger.verbose(f"got something else: {node_data}")                
                return node_data            
        
        #we want the first data node which is the child of the root node in the tree object:    
        first_real_tree_node = self.tree_widget.invisibleRootItem().child(0)
        tree_data = parse_item(first_real_tree_node, 0) 
        logger.verbose(f"\n\nResult: {tree_data}")

        return tree_data

        # Convert the list of data to a JSON string
        return json.dumps(tree_data, indent=4)
            
    def load_json_from_model(self):
        try:
            json_text = self.model.get_text()
            json_data = json.loads(json_text)
            return json_data
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON: {e}")
            return None        
            
    def clear_tree_view(self):
        logger.debug("clear_tree_view() Called.")
        self.tree_widget.clear()        

    def populate_tree_from_json(self, json_data, parent_tree_node=None):
        logger.debug("populate_tree_from_json() called.")
        
        def parse_item(json_data, parent_tree_node, level):
            logger.verbose(f"**start level:{level}")
            
            if isinstance(json_data, list):
                logger.verbose(f"list='{json_data}'")
                
                size = len(json_data)
                #new tree widget item for this level in the json text:
                item = get_new_QTreeWidgetItem()
                item.setText(0, f"Array ({size})")
                item.setData(0, Qt.UserRole, []) #add list as parent json_data at this level
                parent_tree_node.addChild(item)
                
                for idx, val in enumerate(json_data):
                    logger.verbose(f"list child[{idx}], val={val}")
                    
                    if(isinstance(val, dict) or isinstance(val, list)):
                        #for each of these child items go parse the next level of children:

                        parse_item(val, item, level + 1)
                    else:
                        #child is a scaler value. Just add it.
                        
                        child_item = get_new_QTreeWidgetItem()
                        child_item.setData(0, Qt.UserRole, val) #add val as data bottom of this level                 

                        child_item.setText(0, f"{val}")
                        #child_item.setFlags(item.flags() | Qt.ItemIsEditable)  # Make item editable
                        #current child_item to item for this level:
                        item.addChild(child_item)
                        #add item for this level in json data to the parent tree node that was passed in:
                        parent_tree_node.addChild(item)
            
            elif isinstance(json_data, dict):
                logger.verbose(f"dict='{json_data}'")
                
                size = len(json_data)
                #new tree widget item for this level in the json text:
                item = get_new_QTreeWidgetItem()
                
                #if we are the top level node, assuming this is NMS base data, add the base name data
                #to the top levelnode label text:
                if(level == 1 ):
                    base_name =  json_data['Name']
                    if not base_name:
                        base_name = "Unnamed Freighter Base"
                    
                    item.setText(0, f"Dict ({size}) Gal: {GALAXIES[int(json_data['GalacticAddress'][7:8], 16)]}, Sys: {json_data['GalacticAddress'][3:6]}, Base: {base_name}")
                else:
                    item.setText(0, f"Dict ({size})")                
                                
                item.setData(0, Qt.UserRole, {}) #add dict as parent json_data at this level
                               
                parent_tree_node.addChild(item)
                                
                for key, val in json_data.items():
                    data_tuple = (key,val)
                    
                    logger.verbose(f"dict child tuple['{key}']: {val}")
                    parse_item(data_tuple, item, level + 1)
            
            elif isinstance(json_data, tuple):
                logger.verbose(f"tuple='{json_data}'")
                
                key = json_data[0]
                val = json_data[1]
                
                size = len(json_data)
                #new tree widget item for this level in the json text:
                item = get_new_QTreeWidgetItem()
                item.setText(0, f"Tuple")
                item.setData(0, Qt.UserRole, ()) #add a tuple as parent at this level
            
                #add the key value to the dict child item:
                key_item = get_new_QTreeWidgetItem()
                key_item.setText(0, f"{key}")
                key_item.setData(0, Qt.UserRole, key)
                item.addChild(key_item)
                
                if(isinstance(val, dict) or isinstance(val, list)):
                    #for each of these child items go parse the next level of children:
                    parse_item(val, item, level + 1)
                else:
                    data_item = get_new_QTreeWidgetItem()
                    data_item.setText(0, f"{val}")
                    data_item.setData(0, Qt.UserRole, val) 
                    
                    #current data_item to tuple item for this level:
                    item.addChild(data_item)
                
                parent_tree_node.addChild(item)
            
            else:
                logger.verbose(f"data item, data='{json_data}', type of {type(json_data)}")
                
                item = QTreeWidgetItem([str(json_data)])
                item.setData(0, Qt.UserRole, json_data) 
                #item.setFlags(item.flags() | Qt.ItemIsEditable)  # Make item editable
                parent_tree_node.addChild(item)

                
            logger.verbose(f"**end level {level}")   

        
        parent_tree_node = self.tree_widget.invisibleRootItem()
        parse_item(json_data, parent_tree_node, 0)

        

class SecondTabContent(BaseTabContent):
    def __init__(self, model, tab_name):
        super().__init__(model, tab_name)
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        self.layout.addWidget(self.text_edit)
        self.setLayout(self.layout)

        self.text_edit.setText(self.model.get_text())
        self.text_edit.textChanged.connect(self.set_model_from_text_widget)

    def set_model_from_text_widget(self):
        logger.debug("2nd Tab set_model_from_text_widget() enter")
        new_text = self.text_edit.toPlainText()
        self.model.set_text(new_text)
        logger.debug("2nd Tab set_model_from_text_widget() exit")

    def reset_tab_text_content_from_model(self):
        logger.debug("2nd Tab reset_tab_text_content_from_model() enter")
        self.blockSignals()
        self.text_edit.setText(self.model.get_text())
        self.unblockSignals()

        logger.debug("2nd Tab reset_tab_text_content_from_model() exit")
        
    def blockSignals(self):
        self.text_edit.blockSignals(True)
        self.model.blockSignals(True)
        
    def unblockSignals(self):
        self.text_edit.blockSignals(False)
        self.model.blockSignals(False)           
        

class IniFileManager:
    def __init__(self, ini_file='app_preferences.ini'):
        """
        Initializes the IniFileManager class.
        :param ini_file: The path to the .ini file (default is 'app_preferences.ini').
        """
        # Set the ini file path to be in the same directory as the script
        self.ini_file = os.path.join(os.path.dirname(__file__), ini_file)
        self.config = configparser.ConfigParser()

        # Check if ini file exists, if not create a new one
        if os.path.exists(self.ini_file):
            self.config.read(self.ini_file)
        else:
            self.create_empty_ini_file()

        # Initialize the working file path from the ini file if it exists
        self.working_file_path = self.config.get('Preferences', 'working_file_path', fallback='')

    def create_empty_ini_file(self):
        """Creates an empty ini file if it doesn't exist."""
        self.config['Preferences'] = {'working_file_path': ''}
        with open(self.ini_file, 'w') as configfile:
            self.config.write(configfile)

    def store_current_working_file_path(self, file_path):
        """
        Stores the given file path in the ini file.
        :param file_path: The full path of the working file to store.
        """
        self.config['Preferences'] = {'working_file_path': file_path}
        with open(self.ini_file, 'w') as configfile:
            self.config.write(configfile)
        self.working_file_path = file_path

    def get_last_working_file_path(self):
        """
        Retrieves the last stored working file path from the ini file.
        :return: The last working file path or an empty string if not found.
        """
        return self.working_file_path

    def get_last_working_file_directory(self):
        """
        Retrieves the directory of the last stored working file path.
        :return: The directory of the working file, or an empty string if the path is not set.
        """
        if self.working_file_path:
            return os.path.dirname(self.working_file_path)
        return ''

    def get_last_working_file_name(self):
        """
        Retrieves the file name of the last stored working file path.
        :return: The file name of the working file, or an empty string if the path is not set.
        """
        if self.working_file_path:
            return os.path.basename(self.working_file_path)
        return ''


class MainWindow(QMainWindow):
    def __init__(self):
        logger.debug("MainWindow(QMainWindow).__init__ ENTER")
        
        
        super().__init__()
        
        self.ini_file_manager = IniFileManager()
        
        self.model = JsonArrayModel(self.ini_file_manager)
        self.tabs = QTabWidget()

        self.tab1 = FirstTabContent(self.model, 'Tab 1', self)
        self.tab2 = SecondTabContent(self.model, 'Tab 2')

        self.tabs.addTab(self.tab1, 'Tab 1')
        self.tabs.addTab(self.tab2, 'Tab 2')

        self.tabs.currentChanged.connect(self.tab_changed)

        self.setCentralWidget(self.tabs)
        self.setWindowTitle('Model-View Example')
        self.setGeometry(400, 250, 1500, 800)

        self.create_menu_bar(self.model)
        logger.debug("MainWindow(QMainWindow).__init__ EXIT")
        

    def create_menu_bar(self, model):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu('File')

        open_action = QAction('Open', self)
        save_action = QAction('Save', self)
        save_as_action = QAction('Save As', self)
        copy_action = QAction('Copy to Clipboard', self)

        open_action.triggered.connect(self.open_file)
        save_action.triggered.connect(self.save_file)
        save_as_action.triggered.connect(self.save_file_as)
        copy_action.triggered.connect(lambda: copy_to_clipboard(model, self))

        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(save_as_action)
        file_menu.addAction(copy_action)

    def open_file(self):
        options = QFileDialog.Options()
        
        # Get the last working directory from the ini manager
        initial_directory = self.ini_file_manager.get_last_working_file_directory() or os.getcwd()
        
        # Open file dialog starting from the last working directory
        file_name, _ = QFileDialog.getOpenFileName(self, 
                                                   "Open File", 
                                                   initial_directory,  # Set the initial directory
                                                   "JSON Files (*.json);;All Files (*)", 
                                                   options=options)
        
        if file_name:
            try:
                # Open the selected file and read its contents
                with open(file_name, 'r') as file:
                    self.model.set_text(file.read())
                    self.update_tabs_from_model()

                # Store the new file path in the ini manager
                self.ini_file_manager.store_current_working_file_path(file_name)
            
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open file: {e}")

    def save_file(self):
        """Saves the file using the last saved path, or prompts if no path is set."""
        # Get the last working file path from the ini manager
        last_file_path = self.ini_file_manager.get_last_working_file_path()
        
        if last_file_path and os.path.exists(last_file_path):
            # If there's a valid path, save directly
            try:
                with open(last_file_path, 'w') as f:
                    f.write(self.model.get_text())

                # Show a confirmation message
                QMessageBox.information(self, 'File Saved', f'File saved at: {last_file_path}')
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {e}")
        else:
            # If no path is set or the file doesn't exist, use "Save As" behavior
            self.save_file_as()  # Fallback to "Save As" behavior if no previous file path


    def save_file_as(self):
        """Implements the Save As functionality allowing the user to specify a file location."""
        # Get the preferences from the ini manager for the default save path
        save_file_name = QFileDialog.getSaveFileName(
            self, 'Save As', 
            self.ini_file_manager.get_last_working_file_path()
        )

        if save_file_name[0]:
            try:
                # Save the file content
                with open(save_file_name[0], 'w') as f:
                    f.write(self.model.get_text())

                # Show a confirmation message
                QMessageBox.information(self, 'File Saved As', f'File saved at: {save_file_name[0]}')

                # Store the file path in the ini manager after saving
                self.ini_file_manager.store_current_working_file_path(save_file_name[0])
            
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {e}")


    def tab_changed(self, index):
        logger.debug(f"tab_changed() enter, index: {index}")

        try:
            self.tabs.widget(index).reset_tab_text_content_from_model()
        except Exception as e:
            logging.error(f"An error occurred: {e}")

        logger.debug("tab_changed() exit")
        
    def update_tabs_from_model(self):
        self.tab1.reset_tab_text_content_from_model()
        self.tab2.reset_tab_text_content_from_model()
 
def main():
    init_galaxies()
    logger.debug("main enter")
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    logger.debug("main exit")
    sys.exit(app.exec_())
    
def init_galaxies():
    global GALAXIES
    GALAXIES = {}
    GALAXIES[0] = 'Euclid'
    GALAXIES[1] = 'Hilbert Dimension'
    GALAXIES[2] = 'Calypso'
    GALAXIES[3] = 'Hesperius Dimension'
    GALAXIES[4] = 'Hyades'
    GALAXIES[5] = 'Ickjamatew'
    GALAXIES[6] = 'Budullangr'
    GALAXIES[7] = 'Kikolgallr'
    GALAXIES[8] = 'Eltiensleen'
    GALAXIES[9] = 'Eissentam'
    GALAXIES[10] = 'Elkupalos'
    GALAXIES[11] = 'Aptarkaba'
    GALAXIES[12] = 'Ontiniangp'
    GALAXIES[13] = 'Odiwagiri'
    GALAXIES[14] = 'Ogtialabi'
    GALAXIES[15] = 'Muhacksonto'
    GALAXIES[16] = 'Hitonskyer'
    GALAXIES[17] = 'Rerasmutul'
    GALAXIES[18] = 'Isdoraijung'
    GALAXIES[19] = 'Doctinawyra'
    GALAXIES[20] = 'Loychazinq'
    GALAXIES[21] = 'Zukasizawa'
    GALAXIES[22] = 'Ekwathore'
    GALAXIES[23] = 'Yeberhahne'
    GALAXIES[24] = 'Twerbetek'
    GALAXIES[25] = 'Sivarates'
    GALAXIES[26] = 'Eajerandal'
    GALAXIES[27] = 'Aldukesci'
    GALAXIES[28] = 'Wotyarogii'
    GALAXIES[29] = 'Sudzerbal'
    GALAXIES[30] = 'Maupenzhay'
    GALAXIES[31] = 'Sugueziume'
    GALAXIES[32] = 'Brogoweldian'
    GALAXIES[33] = 'Ehbogdenbu'
    GALAXIES[34] = 'Ijsenufryos'
    GALAXIES[35] = 'Nipikulha'
    GALAXIES[36] = 'Autsurabin'
    GALAXIES[37] = 'Lusontrygiamh'
    GALAXIES[38] = 'Rewmanawa'
    GALAXIES[39] = 'Ethiophodhe'
    GALAXIES[40] = 'Urastrykle'
    GALAXIES[41] = 'Xobeurindj'
    GALAXIES[42] = 'Oniijialdu'
    GALAXIES[43] = 'Wucetosucc'
    GALAXIES[44] = 'Ebyeloof'
    GALAXIES[45] = 'Odyavanta'
    GALAXIES[46] = 'Milekistri'
    GALAXIES[47] = 'Waferganh'
    GALAXIES[48] = 'Agnusopwit'
    GALAXIES[49] = 'Teyaypilny'
    GALAXIES[50] = 'Zalienkosm'
    GALAXIES[51] = 'Ladgudiraf'
    GALAXIES[52] = 'Mushonponte'
    GALAXIES[53] = 'Amsentisz'
    GALAXIES[54] = 'Fladiselm'
    GALAXIES[55] = 'Laanawemb'
    GALAXIES[56] = 'Ilkerloor'
    GALAXIES[57] = 'Davanossi'
    GALAXIES[58] = 'Ploehrliou'
    GALAXIES[59] = 'Corpinyaya'
    GALAXIES[60] = 'Leckandmeram'
    GALAXIES[61] = 'Quulngais'
    GALAXIES[62] = 'Nokokipsechl'
    GALAXIES[63] = 'Rinblodesa'
    GALAXIES[64] = 'Loydporpen'
    GALAXIES[65] = 'Ibtrevskip'
    GALAXIES[66] = 'Elkowaldb'
    GALAXIES[67] = 'Heholhofsko'
    GALAXIES[68] = 'Yebrilowisod'
    GALAXIES[69] = 'Husalvangewi'
    GALAXIES[70] = 'Ovnauesed'
    GALAXIES[71] = 'Bahibusey'
    GALAXIES[72] = 'Nuybeliaure'
    GALAXIES[73] = 'Doshawchuc'
    GALAXIES[74] = 'Ruckinarkh'
    GALAXIES[75] = 'Thorettac'
    GALAXIES[76] = 'Nuponoparau'
    GALAXIES[77] = 'Moglaschil'
    GALAXIES[78] = 'Uiweupose'
    GALAXIES[79] = 'Nasmilete'
    GALAXIES[80] = 'Ekdaluskin'
    GALAXIES[81] = 'Hakapanasy'
    GALAXIES[82] = 'Dimonimba'
    GALAXIES[83] = 'Cajaccari'
    GALAXIES[84] = 'Olonerovo'
    GALAXIES[85] = 'Umlanswick'
    GALAXIES[86] = 'Henayliszm'
    GALAXIES[87] = 'Utzenmate'
    GALAXIES[88] = 'Umirpaiya'
    GALAXIES[89] = 'Paholiang'
    GALAXIES[90] = 'Iaereznika'
    GALAXIES[91] = 'Yudukagath'
    GALAXIES[92] = 'Boealalosnj'
    GALAXIES[93] = 'Yaevarcko'
    GALAXIES[94] = 'Coellosipp'
    GALAXIES[95] = 'Wayndohalou'
    GALAXIES[96] = 'Smoduraykl'
    GALAXIES[97] = 'Apmaneessu'
    GALAXIES[98] = 'Hicanpaav'
    GALAXIES[99] = 'Akvasanta'
    GALAXIES[100] = 'Tuychelisaor'
    GALAXIES[101] = 'Rivskimbe'
    GALAXIES[102] = 'Daksanquix'
    GALAXIES[103] = 'Kissonlin'
    GALAXIES[104] = 'Aediabiel'
    GALAXIES[105] = 'Ulosaginyik'
    GALAXIES[106] = 'Roclaytonycar'
    GALAXIES[107] = 'Kichiaroa'
    GALAXIES[108] = 'Irceauffey'
    GALAXIES[109] = 'Nudquathsenfe'
    GALAXIES[110] = 'Getaizakaal'
    GALAXIES[111] = 'Hansolmien'
    GALAXIES[112] = 'Bloytisagra'
    GALAXIES[113] = 'Ladsenlay'
    GALAXIES[114] = 'Luyugoslasr'
    GALAXIES[115] = 'Ubredhatk'
    GALAXIES[116] = 'Cidoniana'
    GALAXIES[117] = 'Jasinessa'
    GALAXIES[118] = 'Torweierf'
    GALAXIES[119] = 'Saffneckm'
    GALAXIES[120] = 'Thnistner'
    GALAXIES[121] = 'Dotusingg'
    GALAXIES[122] = 'Luleukous'
    GALAXIES[123] = 'Jelmandan'
    GALAXIES[124] = 'Otimanaso'
    GALAXIES[125] = 'Enjaxusanto'
    GALAXIES[126] = 'Sezviktorew'
    GALAXIES[127] = 'Zikehpm'
    GALAXIES[128] = 'Bephembah'
    GALAXIES[129] = 'Broomerrai'
    GALAXIES[130] = 'Meximicka'
    GALAXIES[131] = 'Venessika'
    GALAXIES[132] = 'Gaiteseling'
    GALAXIES[133] = 'Zosakasiro'
    GALAXIES[134] = 'Drajayanes'
    GALAXIES[135] = 'Ooibekuar'
    GALAXIES[136] = 'Urckiansi'
    GALAXIES[137] = 'Dozivadido'
    GALAXIES[138] = 'Emiekereks'
    GALAXIES[139] = 'Meykinunukur'
    GALAXIES[140] = 'Kimycuristh'
    GALAXIES[141] = 'Roansfien'
    GALAXIES[142] = 'Isgarmeso'
    GALAXIES[143] = 'Daitibeli'
    GALAXIES[144] = 'Gucuttarik'
    GALAXIES[145] = 'Enlaythie'
    GALAXIES[146] = 'Drewweste'
    GALAXIES[147] = 'Akbulkabi'
    GALAXIES[148] = 'Homskiw'
    GALAXIES[149] = 'Zavainlani'
    GALAXIES[150] = 'Jewijkmas'
    GALAXIES[151] = 'Itlhotagra'
    GALAXIES[152] = 'Podalicess'
    GALAXIES[153] = 'Hiviusauer'
    GALAXIES[154] = 'Halsebenk'
    GALAXIES[155] = 'Puikitoac'
    GALAXIES[156] = 'Gaybakuaria'
    GALAXIES[157] = 'Grbodubhe'
    GALAXIES[158] = 'Rycempler'
    GALAXIES[159] = 'Indjalala'
    GALAXIES[160] = 'Fontenikk'
    GALAXIES[161] = 'Pasycihelwhee'
    GALAXIES[162] = 'Ikbaksmit'
    GALAXIES[163] = 'Telicianses'
    GALAXIES[164] = 'Oyleyzhan'
    GALAXIES[165] = 'Uagerosat'
    GALAXIES[166] = 'Impoxectin'
    GALAXIES[167] = 'Twoodmand'
    GALAXIES[168] = 'Hilfsesorbs'
    GALAXIES[169] = 'Ezdaranit'
    GALAXIES[170] = 'Wiensanshe'
    GALAXIES[171] = 'Ewheelonc'
    GALAXIES[172] = 'Litzmantufa'
    GALAXIES[173] = 'Emarmatosi'
    GALAXIES[174] = 'Mufimbomacvi'
    GALAXIES[175] = 'Wongquarum'
    GALAXIES[176] = 'Hapirajua'
    GALAXIES[177] = 'Igbinduina'
    GALAXIES[178] = 'Wepaitvas'
    GALAXIES[179] = 'Sthatigudi'
    GALAXIES[180] = 'Yekathsebehn'
    GALAXIES[181] = 'Ebedeagurst'
    GALAXIES[182] = 'Nolisonia'
    GALAXIES[183] = 'Ulexovitab'
    GALAXIES[184] = 'Iodhinxois'
    GALAXIES[185] = 'Irroswitzs'
    GALAXIES[186] = 'Bifredait'
    GALAXIES[187] = 'Beiraghedwe'
    GALAXIES[188] = 'Yeonatlak'
    GALAXIES[189] = 'Cugnatachh'
    GALAXIES[190] = 'Nozoryenki'
    GALAXIES[191] = 'Ebralduri'
    GALAXIES[192] = 'Evcickcandj'
    GALAXIES[193] = 'Ziybosswin'
    GALAXIES[194] = 'Heperclait'
    GALAXIES[195] = 'Sugiuniam'
    GALAXIES[196] = 'Aaseertush'
    GALAXIES[197] = 'Uglyestemaa'
    GALAXIES[198] = 'Horeroedsh'
    GALAXIES[199] = 'Drundemiso'
    GALAXIES[200] = 'Ityanianat'
    GALAXIES[201] = 'Purneyrine'
    GALAXIES[202] = 'Dokiessmat'
    GALAXIES[203] = 'Nupiacheh'
    GALAXIES[204] = 'Dihewsonj'
    GALAXIES[205] = 'Rudrailhik'
    GALAXIES[206] = 'Tweretnort'
    GALAXIES[207] = 'Snatreetze'
    GALAXIES[208] = 'Iwundaracos'
    GALAXIES[209] = 'Digarlewena'
    GALAXIES[210] = 'Erquagsta'
    GALAXIES[211] = 'Logovoloin'
    GALAXIES[212] = 'Boyaghosganh'
    GALAXIES[213] = 'Kuolungau'
    GALAXIES[214] = 'Pehneldept'
    GALAXIES[215] = 'Yevettiiqidcon'
    GALAXIES[216] = 'Sahliacabru'
    GALAXIES[217] = 'Noggalterpor'
    GALAXIES[218] = 'Chmageaki'
    GALAXIES[219] = 'Veticueca'
    GALAXIES[220] = 'Vittesbursul'
    GALAXIES[221] = 'Nootanore'
    GALAXIES[222] = 'Innebdjerah'
    GALAXIES[223] = 'Kisvarcini'
    GALAXIES[224] = 'Cuzcogipper'
    GALAXIES[225] = 'Pamanhermonsu'
    GALAXIES[226] = 'Brotoghek'
    GALAXIES[227] = 'Mibittara'
    GALAXIES[228] = 'Huruahili'
    GALAXIES[229] = 'Raldwicarn'
    GALAXIES[230] = 'Ezdartlic'
    GALAXIES[231] = 'Badesclema'
    GALAXIES[232] = 'Isenkeyan'
    GALAXIES[233] = 'Iadoitesu'
    GALAXIES[234] = 'Yagrovoisi'
    GALAXIES[235] = 'Ewcomechio'
    GALAXIES[236] = 'Inunnunnoda'
    GALAXIES[237] = 'Dischiutun'
    GALAXIES[238] = 'Yuwarugha'
    GALAXIES[239] = 'Ialmendra'
    GALAXIES[240] = 'Reponudrle'
    GALAXIES[241] = 'Rinjanagrbo'
    GALAXIES[242] = 'Zeziceloh'
    GALAXIES[243] = 'Oeileutasc'
    GALAXIES[244] = 'Zicniijinis'
    GALAXIES[245] = 'Dugnowarilda'
    GALAXIES[246] = 'Neuxoisan'
    GALAXIES[247] = 'Ilmenhorn'
    GALAXIES[248] = 'Rukwatsuku'
    GALAXIES[249] = 'Nepitzaspru'
    GALAXIES[250] = 'Chcehoemig'
    GALAXIES[251] = 'Haffneyrin'
    GALAXIES[252] = 'Uliciawai'
    GALAXIES[253] = 'Tuhgrespod'
    GALAXIES[254] = 'Iousongola'
    GALAXIES[255] = 'Odyalutai'
    

if __name__ == '__main__':
    main()

