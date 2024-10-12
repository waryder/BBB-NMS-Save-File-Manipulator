from imports import *
from NMSHelpMenu import NMSHelpMenu  
from CustomTreeWidget import CustomTreeWidget

    
def get_new_QTreeWidgetItem():
    widget = QTreeWidgetItem()
    widget.setFlags(widget.flags() | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled)  # Make item drag and droppable Qt.ItemIsEditable
    return widget
    
    
def copy_to_clipboard(model, parentWindow = None):
    clipboard = QApplication.clipboard()
    clipboard.setText(model.get_text())
    QMessageBox.information(parentWindow, "Copied", "Text copied to clipboard!") 
    
    
def pretty_print_text_widget(model, parentWindow = None):
    logger.debug("pretty_print_text_widget() ENTER")
    
    parentWindow.text_changed_signal()
    parentWindow.update_text_widget_from_model()
        
    logger.debug("pretty_print_text_widget() EXIT")

        
def get_num_app_child_threads():
    logger.debug("get_num_app_child_threads() ENTER")
    # Get the current process (your application)
    current_process = psutil.Process(os.getpid())
    num_threads = len(current_process.threads())
    logger.debug("get_num_app_child_threads() EXIT, num threads: {num_threads}")
    return num_threads


#some values are preceeded by '0x' and some are not:    
def get_galaxy_system_planet_from_full_addr(galactic_addr_in):
    if isinstance(galactic_addr_in, int):
        galactic_address = f"0x{galactic_addr_in:X}" 
    elif "0x" not in galactic_addr_in:    
        galactic_address = f"0x{int(galactic_addr_in):X}"
    else:
        galactic_address = galactic_addr_in    
        
    gal_idx_slice = slice(6, 8)
    system_idx_slice = slice(3, 6)
    planet_idx = 2
    
    return [galactic_address[gal_idx_slice], galactic_address[system_idx_slice], galactic_address[2]]  

   
        
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
    
        
class CustomTextEdit(QPlainTextEdit):
    def __init__(self, parent=None):
        self.first_tab_obj = parent  # Reference to the parent tab object
        super(CustomTextEdit, self).__init__(parent)

    def keyPressEvent(self, event):
        # Check if Ctrl+V or Cmd+V (on macOS) is pressed
        if event.matches(QKeySequence.Paste):
            print("Text pasted via keyboard shortcut")
            self.first_tab_obj.update_status_indicator_to_green(False)  # Update indicator
            super(CustomTextEdit, self).keyPressEvent(event)  # Let the normal paste occur
        else:
            super(CustomTextEdit, self).keyPressEvent(event)

    def event(self, event):
        # Capture all paste events (context menu and programmatically)
        if event.type() == QEvent.Clipboard:
            print("Text pasted via paste event")
            self.first_tab_obj.update_status_indicator_to_green(False)  # Update indicator
        return super(CustomTextEdit, self).event(event)
        

# Set the global exception handler
sys.excepthook = global_exception_handler
            
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
            

class JsonArrayModel(DataModel):
    def __init__(self, ini_file_manager):
        logger.debug("JsonArrayModel(DataModel).__init__ ENTER")
        super().__init__(ini_file_manager)
        self.init_model_data()
        
        logger.debug("JsonArrayModel(DataModel).__init__ EXIT") 
        
    def init_model_data(self):
        logger.debug("init_model_data() ENTER")
        new_model_data = None
        
        if self.last_file_path and os.path.exists(self.last_file_path):
            # If the file exists, load its contents
            try:
                with open(self.last_file_path, 'r') as file:
                    new_model_data = json.loads(file.read())
            except Exception as e:
                print(f"Failed to load text from {self.last_file_path}: {e}")
                new_model_data = json.loads(INIT_TEXT)
        else:
            # Fall back to INIT_TEXT if no file path is found or the file doesn't exist
            new_model_data = json.loads(INIT_TEXT)            
            
        self.__set_self_with_json_data(new_model_data)    
        
        logger.debug("init_model_data() EXIT")

    # Override the stubbed accessor functions
    def get_text(self):
        logger.debug("get_text() ENTER")
        logger.debug("get_text() EXIT")
        return json.dumps(self.model_data, indent=4)

    def set_text(self, text):
        logger.debug("set_text() ENTER")
        json_loads = json.loads(text)
        self.__set_self_with_json_data(json_loads)
            
        logger.debug("set_text EXIT")    

    def get_json(self):
        logger.debug("get_json() ENTER")
        logger.debug("get_json() EXIT")
        return self.model_data
        
    def set_json(self, json_array):
        logger.debug("set_json() ENTER")
        self.__set_self_with_json_data(json_array)
        logger.debug("set_json() EXIT") 

    def add_base(self, nms_base_json_array):
        logger.debug("add_base() ENTER")
        
        self.model_data.insert(0, nms_base_json_array)
        self.modelChanged.emit()
        logger.debug("add_base() EXIT") 
        
    def __set_self_with_json_data(self, json_array):
        logger.debug("__set_model_with_json_data() ENTER")
        
        if json_array != self.model_data:
            self.model_data = json_array
            
            #this was causing issues:
            #we need all values to be treated as strings:
            #self.convert_values_to_strings_in_place(self.model_data)
            
            
            self.modelChanged.emit()
            
        logger.debug("__set_model_with_json_data() EXIT")    
            

class BaseTabContent(QWidget):
    def __init__(self, model, tab_name):
        super().__init__()
        self.model = model
        self.tab_name = tab_name

    def update_text_widget_from_model(self):
        pass

    def text_changed_signal(self):
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
        self.sync_from_text_window_button = QPushButton("Sync from Text Window")
        self.sync_from_text_window_button.setFixedWidth(button_width)
###
        # Create the text label and indicator widget for Tree sync status
        self.tree_synced_label = QLabel("Tree Synced:", self)  # Create a text label for "Status"
        self.tree_synced_label.setFixedWidth(button_width - 75)
        
        self.tree_synced_indicator = QWidget(self)  # Create a widget to represent the LED
        self.tree_synced_indicator.setFixedSize(10, 10)  # Set size to small (like an LED)

        # Initially set the indicator to red (off) and make it circular
        self.tree_synced_indicator.setStyleSheet(f"background-color: {GREEN_LED_COLOR}; border-radius: 4px;")
###
        self.sort_bases_by_gal_sys_name_button = QPushButton("Sort By Gal, Sys, Name")
        self.sort_bases_by_gal_sys_name_button.setFixedWidth(button_width)
###    
        # Create the text label and indicator widget for Background Processing status
        self.status_label = QLabel("Background Processing:", self)  # Create a text label for "Status"
        self.status_label.setFixedWidth(button_width - 25)
        
        self.status_indicator = QWidget(self)  # Create a widget to represent the LED
        self.status_indicator.setFixedSize(10, 10)  # Set size to small (like an LED)

        # Initially set the indicator to red (off) and make it circular
        self.status_indicator.setStyleSheet(f"background-color: {GREEN_LED_COLOR}; border-radius: 4px;")
###        
        # Create tree widget and text edit
        #self.tree_widget = QTreeWidget()
        self.tree_widget = CustomTreeWidget(self)
        self.tree_widget.setHeaderHidden(True)
        
        self.bottom_left_label = QLabel("", self)
###        
        status_layout = QHBoxLayout()
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.status_indicator)
###        
        tree_synced_indicator_layout = QHBoxLayout()
        tree_synced_indicator_layout.addWidget(self.tree_synced_label)
        tree_synced_indicator_layout.addWidget(self.tree_synced_indicator)
###        
        # Create layout for the buttons to be horizontal
        left_buttons_lo = QHBoxLayout()
        left_buttons_lo.addWidget(self.sync_from_text_window_button)
        left_buttons_lo.addLayout(tree_synced_indicator_layout)
        left_buttons_lo.addWidget(self.sort_bases_by_gal_sys_name_button)
        left_buttons_lo.addLayout(status_layout)  # Add the status layout to the left
        # Set alignment
        left_buttons_lo.setAlignment(Qt.AlignLeft)
###
        # Create a vertical layout for the left side and add buttons layout
        left_pane_layout = QVBoxLayout()
        # Create layouts for buttons
        left_pane_layout = QVBoxLayout()
        left_pane_layout.addLayout(left_buttons_lo)
        left_pane_layout.addWidget(self.tree_widget)
        left_pane_layout.addWidget(self.bottom_left_label)
###        
        left_container = QWidget()
        left_container.setLayout(left_pane_layout)
        
#right pane: 
        self.right_button = QPushButton("Synch from Tree Window")
        self.right_button.setFixedWidth(button_width)
###        
        self.copy_button = QPushButton("Copy to Clipboard")  # New button for copying text
        self.copy_button.setFixedWidth(button_width)
###        
        self.pretty_print_button = QPushButton("Pretty Print")  # New button for copying text
        self.pretty_print_button.setFixedWidth(button_width)
###        
        self.text_edit = CustomTextEdit(self)
        
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
                
        self.text_edit.setPlainText(self.model.get_text())

        #added just to keep spacing consistent with left panel:
        self.bottom_right_label = QLabel("", self)
        
        right_pane_layout = QVBoxLayout()
        right_button_layout = QHBoxLayout()
        right_button_layout.setAlignment(Qt.AlignLeft)
        #right_button_layout.setSpacing(2)
        
        #right_button_layout.addWidget(self.right_button)
        right_button_layout.addWidget(self.copy_button)
        right_button_layout.addWidget(self.pretty_print_button)
        
        right_pane_layout.addLayout(right_button_layout)
        right_pane_layout.addWidget(self.text_edit)
        right_pane_layout.addWidget(self.bottom_right_label)
        

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
        self.sync_from_text_window_button.clicked.connect(self.sync_from_text_window)
        self.sort_bases_by_gal_sys_name_button.clicked.connect(self.sort_bases_by_gal_sys_name)
        #self.right_button.clicked.connect(self.sync_text_from_tree_window)
        self.copy_button.clicked.connect(lambda: copy_to_clipboard(self.model, self))
        self.pretty_print_button.clicked.connect(lambda: pretty_print_text_widget(self.model, self))
        
        # Update tree from model
        self.update_tree_from_model()
        #self.tree_widget.expandAll()
        self.tree_widget.expand_tree_to_level(1)
        
        # Connect text edit changes to model
        
        
        #this is to update the model on each charater input. I think we're doing away with this:
        #self.text_edit.textChanged.connect(self.text_changed_signal)
        
        
        
        
        self.model.modelChanged.connect(self.model_changed)
        
            
    # Function to update the indicator color (red or green)
    def update_status_indicator_to_green(self, green_if_true):
        logger.debug("update_status_indicator_to_green() ENTER")
        palette = self.status_indicator.palette()
        
        if green_if_true:
            logger.debug("green")
            self.status_indicator.setStyleSheet(f"background-color: {GREEN_LED_COLOR}; border-radius: 4px;")
        else:
            logger.debug("yellow")
            self.status_indicator.setStyleSheet(f"background-color: {YELLOW_LED_COLOR}; border-radius: 4px;")
            
        self.status_indicator.setPalette(palette)
        self.status_indicator.update()
        logger.debug("update_status_indicator_to_green() EXIT")
        
    
    # Function to update the indicator color (red or green)
    def update_tree_synced_indicator(self, green_if_true):
        logger.debug("update_tree_synced_indicator() ENTER")
        palette = self.tree_synced_indicator.palette()
        
        if green_if_true:
            logger.debug("green")
            self.tree_synced_indicator.setStyleSheet(f"background-color: {GREEN_LED_COLOR}; border-radius: 4px;")
        else:
            logger.debug("red")
            self.tree_synced_indicator.setStyleSheet(f"background-color: red; border-radius: 4px;")
            
        self.tree_synced_indicator.setPalette(palette)
        self.tree_synced_indicator.update()
        logger.debug("update_tree_synced_indicator() EXIT")    
        

    def set_led_based_on_app_thread_load(self, max_threads = 4):
        logger.debug("set_led_based_on_app_thread_load() EXIT")
        
        def run():
            nonlocal max_threads
            logger.debug("set_led_based_on_app_thread_load() ENTER")
            
            #4 comes from testing the idle state of the app informally:
            num_threads = get_num_app_child_threads()
            logger.debug(f"max_threads: {max_threads}, num_threads: {num_threads}")
                
            if num_threads > max_threads:
                #set the led yellow:
                self.update_status_indicator_to_green(False)
                
                QTimer.singleShot(2000, run)
                logger.debug("set_led_based_on_app_thread_load() EXIT, yellow\n")
            else:    
                #set the led green:        
                self.update_status_indicator_to_green(True)
                logger.debug("set_led_based_on_app_thread_load() EXIT, green\n")            
        
        #wait 2 seconds on the first run:
        QTimer.singleShot(2000, run)
        logger.debug("set_led_based_on_app_thread_load() EXIT")
       
    def show_context_menu(self, position):
        logger.debug("show_context_menu() ENTER")
        # Create the default context menu
        context_menu = self.text_edit.createStandardContextMenu()

        # Add a search option
        search_action = context_menu.addAction("Search Text")

        # Connect the search option to a function that performs the search
        search_action.triggered.connect(self.search_text)

        # Show the context menu
        context_menu.exec_(self.text_edit.mapToGlobal(position))
        logger.debug("show_context_menu() ENTER")
        
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
        self.blockSignals()

        self.update_text_widget_from_model()
        self.update_tree_from_model()
        
        self.unblockSignals()
        logger.verbose(f"Now: {self.model.get_text()}")        

    def sync_from_text_window(self):
        print("Sync from Text Window ENTER")
        self.set_led_based_on_app_thread_load()
        
        # Set tree from text
        try:
            #update model from txt_widget:
            self.text_changed_signal()
            self.update_tree_from_model()
            
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Error", f"Failed to parse JSON from text window: {e}")
            
        self.tree_widget.expand_tree_to_level(1)
        self.update_tree_synced_indicator(True)            
        print("Sync from Text Window EXIT")    
            
    def sort_bases_by_gal_sys_name(self):
        logger.debug("Sort Bases clicked")
        
        self.set_led_based_on_app_thread_load()
        
        model_json = self.model.get_json()
        
        if(logging.getLogger().getEffectiveLevel() == logger.verbose):
            for el in model_json:
                galval = get_galaxy_system_planet_from_full_addr(el['GalacticAddress'])[GALAXY_FROM_GALACTIC_ADDR_IDX]
                sysval = get_galaxy_system_planet_from_full_addr(el['GalacticAddress'])[SYSTEM_FROM_GALACTIC_ADDR_IDX]
                logger.verbose(f"Gal: {galval}, Sys: {sysval}, {el['Name']}")
        
        # Sort model_json in place based on the desired key
        model_json.sort(key=lambda el: (
            int(get_galaxy_system_planet_from_full_addr(el['GalacticAddress'])[GALAXY_FROM_GALACTIC_ADDR_IDX], 16),  # galaxy (characters 5 and 6)
            int(get_galaxy_system_planet_from_full_addr(el['GalacticAddress'])[SYSTEM_FROM_GALACTIC_ADDR_IDX], 16),  # system (characters 2 to 4)
            el['Name'] # base_name
        ))
        
        if(logging.getLogger().getEffectiveLevel() == logger.verbose):
            for el in model_json:
                logger.verbose(f"Gal: {get_galaxy_system_planet_from_full_addr(el['GalacticAddress'])[GALAXY_FROM_GALACTIC_ADDR_IDX]}, Sys: {get_galaxy_system_planet_from_full_addr(el['GalacticAddress'])[SYSTEM_FROM_GALACTIC_ADDR_IDX]}, {el['Name']}")
        
        self.update_tree_from_model()
        self.update_text_widget_from_model()        

    def sync_text_from_tree_window(self):
        logger.debug("sync from Tree Window ENTER")
        self.update_model_from_tree()
        self.update_text_widget_from_model()        
        logger.debug("sync from Tree Window EXIT")

    def text_changed_signal(self):
        logger.debug("1st Tab text_changed_signal() enter")        
        self.update_tree_synced_indicator(False)
        new_text = self.text_edit.toPlainText()
        self.model.set_text(new_text)
        logger.debug("1st Tab text_changed_signal() exit")

    def populate_tree(self, data, parent=None):
        logger.debug("populate_tree() ENTER")
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
                
        logger.debug("populate_tree() EXIT")                    

    def update_text_widget_from_model(self):
        logger.debug("1st Tab update_text_widget_from_model() enter")
        #self.blockSignals()
        self.text_edit.setPlainText(self.model.get_text())
        #self.unblockSignals()
        logger.debug("1st Tab update_text_widget_from_model() exit")
  
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
        
    def tree_widget_data_to_json(self, node_in = None): 
        def parse_item(tree_node, depth):
            #we do not expect this here but were seeing it for some reason. We have deleted nodes
            #at times when we get to this point and it seems like maybe Qt hangs onto a ghost reference
            #to deleted nodes or something:            
            if tree_node is None:
                return
            
            node_data = tree_node.data(0, QT_DATA_SAVE_NODES_DATA_STRUCT)
            
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
                
                key = tree_node.child(0).data(0, QT_DATA_SAVE_NODES_DATA_STRUCT)
                value = parse_item(tree_node.child(1), depth + 1) #go send the value nodes back around...
                
                output = (key, value)
                return output                

            else:                
                logger.verbose(f"got something else: {node_data}")                
                return node_data            
        
        if not node_in:
            #assume we want the whole tree
            #we want the first data node which is the child of the root node in the tree object:    
            tree_node = self.tree_widget.invisibleRootItem().child(0)
        else:
            tree_node = node_in
           
        tree_data = parse_item(tree_node, 0) 
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
        #return
        logger.debug("populate_tree_from_json() ENTER")

        base_count = 0
        line_count = 0
        
        def parse_item(json_data, parent_tree_node, level):
            nonlocal base_count
            nonlocal line_count
            logger.verbose(f"**start level:{level}")
            
            if isinstance(json_data, list):
                logger.verbose(f"list='{json_data}'")
                
                size = len(json_data)
                #new tree widget item for this level in the json text:
                item = get_new_QTreeWidgetItem()
                item.setText(0, f"Array ({size})")
                item.setData(0, QT_DATA_SAVE_NODES_DATA_STRUCT, []) #add list as parent json_data at this level
                line_count += 1
                item.setData(0, QT_DATA_LINE_COUNT, line_count) #store off the expected line number upon generation of the text from this this tree 
                
                parent_tree_node.addChild(item)
                
                for idx, val in enumerate(json_data):
                    logger.verbose(f"list child[{idx}], val={val}")
                    
                    if(isinstance(val, dict) or isinstance(val, list)):
                        #for each of these child items go parse the next level of children:

                        parse_item(val, item, level + 1)
                    else:
                        #child is a scaler value. Just add it.
                        
                        child_item = get_new_QTreeWidgetItem()
                        child_item.setData(0, QT_DATA_SAVE_NODES_DATA_STRUCT, val) #add val as data bottom of this level                 

                        child_item.setText(0, f"{val}")
                        
                        line_count += 1
                        child_item.setData(0, QT_DATA_LINE_COUNT, line_count) #store off the expected line number upon generation of the text from this this tree 
                        
                        
                        #child_item.setFlags(item.flags() | Qt.ItemIsEditable)  # Make item editable
                        #current child_item to item for this level:
                        item.addChild(child_item)
                        #add item for this level in json data to the parent tree node that was passed in:
                        parent_tree_node.addChild(item)
                
                #at the end of processing a list, the text output will have a trailing '],' and
                #so we need to adjust the line count for that on the way out: 
                line_count += 1        
                        
            
            elif isinstance(json_data, dict):
                logger.verbose(f"dict='{json_data}'")
                
                size = len(json_data)
                #new tree widget item for this level in the json text:
                item = get_new_QTreeWidgetItem()
                
                #if we are the top level node, assuming this is NMS base data, add the base name data
                #to the top level node label text:
                if(level == 1 ):
                    #store off indiecation that tree node is for a base: 
                    item.setData(0, QT_DATA_IS_BASE, True)
                    base_count += 1
                    
                    #empty base names usually indicate it's a freighter:
                    base_name =  json_data['Name']
                    if not base_name:
                        base_name = "Unnamed Freighter Base"
                    
                    galactic_addr = json_data['GalacticAddress']
                    galaxy = get_galaxy_system_planet_from_full_addr(galactic_addr)[GALAXY_FROM_GALACTIC_ADDR_IDX]
                    system = get_galaxy_system_planet_from_full_addr(galactic_addr)[SYSTEM_FROM_GALACTIC_ADDR_IDX]
                    item.setText(0, f"[{base_count - 1}] Dict ({size}) Gal name: {GALAXIES[int(galaxy, 16)]}, Sys: {system}, Base: {base_name}")
                else:
                    item.setText(0, f"Dict ({size})")                
                                
                item.setData(0, QT_DATA_SAVE_NODES_DATA_STRUCT, {}) #add dict as parent json_data at this level
                
                line_count += 1
                item.setData(0, QT_DATA_LINE_COUNT, line_count) #store off the expected line number upon generation of the text from this this tree 
                               
                parent_tree_node.addChild(item)
                                
                for key, val in json_data.items():
                    data_tuple = (key,val)
                    
                    logger.verbose(f"dict child tuple['{key}']: {val}")
                    parse_item(data_tuple, item, level + 1)
                    
                #at the end of processing a dict, the text output will have a trailing '},' and
                #so we need to adjust the line count for that on the way out: 
                line_count += 1
            
            elif isinstance(json_data, tuple):
                logger.verbose(f"tuple='{json_data}'")
                
                key = json_data[0]
                val = json_data[1]
                
                size = len(json_data)
                #new tree widget item for this level in the json text:
                item = get_new_QTreeWidgetItem()
                item.setText(0, f"Tuple")
                item.setData(0, QT_DATA_SAVE_NODES_DATA_STRUCT, ()) #add a tuple as parent at this level
                line_count += 1
                
                #if the tuple key is "Message", testing revealed it could be over multiple lines based on '/w's. Account for this:
                if( key == "Message" ):
                    line_count += val.count('/w')
                    
               
                item.setData(0, QT_DATA_LINE_COUNT, line_count) #store off the expected line number upon generation of the text from this this tree
                            
                #add the key value to the dict child item:
                key_item = get_new_QTreeWidgetItem()
                key_item.setText(0, f"{key}")
                key_item.setData(0, QT_DATA_SAVE_NODES_DATA_STRUCT, key)

                #this data came from the same line in the source text so do not increment line_count here:    
                key_item.setData(0, QT_DATA_LINE_COUNT, line_count) #store off the expected line number upon generation of the text from this this tree 
                
                item.addChild(key_item)
                
                if(isinstance(val, dict) or isinstance(val, list)):
                    #line_count will be incremented at the next stage for the array, when actually because we are processing a tuple right now, the array 
                    #or list symbol is on the same line as the "tuple", so decrement it here so when bumped back at the next stage, saved off line numbers will be correct:
                    line_count -= 1    
                    
                    #for each of these child items go parse the next level of children:
                    parse_item(val, item, level + 1)

                else:
                    data_item = get_new_QTreeWidgetItem()
                    data_item.setText(0, f"{val}")
                    data_item.setData(0, QT_DATA_SAVE_NODES_DATA_STRUCT, val) 
                    
                    #this data came from the same line in the source text so do not increment line_count here:    
                    data_item.setData(0, QT_DATA_LINE_COUNT, line_count) #store off the expected line number upon generation of the text from this this tree 
                    
                    #current data_item to tuple item for this level:
                    item.addChild(data_item)
                
                parent_tree_node.addChild(item)
            
            else:
                print(f"data item, data='{json_data}', type of {type(json_data)}")
                
                #This was converting items to strings but it caused issues on export...
                #item = QTreeWidgetItem([str(json_data)])
                item.setData(0, QT_DATA_SAVE_NODES_DATA_STRUCT, json_data) 
                
                line_count += 1
                item.setData(0, QT_DATA_LINE_COUNT, line_count) #store off the expected line number upon generation of the text from this this tree 
                
                #item.setFlags(item.flags() | Qt.ItemIsEditable)  # Make item editable
                parent_tree_node.addChild(item)

                
            logger.verbose(f"**end level {level}")   

        
        parent_tree_node = self.tree_widget.invisibleRootItem()
        parse_item(json_data, parent_tree_node, 0)
        
        self.tree_widget.expand_tree_to_level(1)
        self.bottom_left_label.setText(f"Number of Bases: {base_count}")
        
        logger.debug("populate_tree_from_json() EXIT") 


class SecondTabContent(BaseTabContent):
    def __init__(self, model, tab_name):
        super().__init__(model, tab_name)
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.text_edit = QPlainTextEdit()
        self.layout.addWidget(self.text_edit)
        self.setLayout(self.layout)

        self.text_edit.setPlainText(self.model.get_text())
        self.text_edit.textChanged.connect(self.text_changed_signal)

    def text_changed_signal(self):
        logger.debug("2nd Tab text_changed_signal() enter")
        new_text = self.text_edit.toPlainText()
        self.model.set_text(new_text)
        logger.debug("2nd Tab text_changed_signal() exit")

    def update_text_widget_from_model(self):
        logger.debug("2nd Tab update_text_widget_from_model() enter")
        self.blockSignals()
        self.text_edit.setPlainText(self.model.get_text())
        self.unblockSignals()

        logger.debug("2nd Tab update_text_widget_from_model() exit")
        
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

        self.tab1 = FirstTabContent(self.model, 'Bases', self)
        self.tab2 = SecondTabContent(self.model, 'Tab 2')

        self.tabs.addTab(self.tab1, 'Base Processing')
        self.tabs.addTab(self.tab2, 'Tab 2')

        self.tabs.currentChanged.connect(self.tab_changed)

        self.setCentralWidget(self.tabs)
        self.setWindowTitle('BBB NMS Save File Manipulator')
        self.setGeometry(400, 250, 1500, 800)

        self.create_menu_bar(self.model)
        
        self.tab1.set_led_based_on_app_thread_load(max_threads = 5)
        
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
        
        self.help_menu = NMSHelpMenu(self)  # Create an instance of the HelpMenu
        self.help_menu.create_help_menu(menu_bar)  # Add the Help menu to the menu bar

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
            self.tabs.widget(index).update_text_widget_from_model()
        except Exception as e:
            logging.error(f"An error occurred: {e}")

        logger.debug("tab_changed() exit")
        
    def update_tabs_from_model(self):
        self.tab1.update_text_widget_from_model()
        self.tab2.update_text_widget_from_model()
        
    #def closeEvent(self, event):
    #    """Handle app close event and stop Yappi profiling."""
    #    yappi.stop()
    #    print("Application closed. Printing Yappi profiling stats...")
    #    yappi.get_func_stats().print_all()
    #    yappi.get_thread_stats().print_all()
    #    event.accept()  # Proceed with closing the window    
        
 
def main():
    init_galaxies()
    logger.debug("main enter")
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    logger.debug("main exit")
    
    return app.exec_()
    
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
    #yappi.start() 
    
    exit_code = main()
    sys.exit(exit_code)  # Ensure the program terminates correctly
    
   
    
    
    
