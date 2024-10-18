#from imports import *
from BaseTabContent import *
from CustomTreeWidget import *
from CustomTextEdit import *
from DataModels import *
from TextSearchDialog import *
from IniFileManager import *

class FirstTabContent(BaseTabContent):
    def __init__(self, parent=None):
        self.main_window = parent        
        self.ini_file_manager = ini_file_manager 
        self.model = JsonArrayModel(self.ini_file_manager.get_last_tab1_working_file_path(), self.init_text())
        self.text_edit = None       
        super().__init__(self.model, self.text_edit)        
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
        
        self.tree_synced = True
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
        self.copy_button.clicked.connect(lambda: self.copy_to_clipboard(self))
        self.pretty_print_button.clicked.connect(lambda: pretty_print_text_widget(self.model, self))
        
        # Update tree from model
        self.update_tree_from_model()
        self.tree_widget.expand_tree_to_level(1)
        
        # Connect text edit changes to model  
        self.model.modelChanged.connect(self.model_changed)
        
        #this is to update the model on each charater input.
        self.text_edit.textChanged.connect(self.text_changed_signal) 
                       
    # Function to update the indicator color (red or green)
    def update_tree_synced_indicator(self, green_if_true):
        logger.debug("1st tab update_tree_synced_indicator() ENTER")
        self.tree_synced = green_if_true
        palette = self.tree_synced_indicator.palette()
        
        if green_if_true:
            logger.debug("1st tab green")
            self.tree_synced_indicator.setStyleSheet(f"background-color: {GREEN_LED_COLOR}; border-radius: 4px;")
        else:
            logger.debug("1st tab red")
            self.tree_synced_indicator.setStyleSheet(f"background-color: red; border-radius: 4px;")
            
        self.tree_synced_indicator.setPalette(palette)
        self.tree_synced_indicator.update()
        logger.debug("1st tab update_tree_synced_indicator() EXIT")    
       
    def show_context_menu(self, position):
        logger.debug("1st tab show_context_menu() ENTER")
        # Create the default context menu
        context_menu = self.text_edit.createStandardContextMenu()

        # Add a search option
        search_action = context_menu.addAction("Search Text")

        # Connect the search option to a function that performs the search
        search_action.triggered.connect(self.search_text)

        # Show the context menu
        context_menu.exec_(self.text_edit.mapToGlobal(position))
        logger.debug("1st tab show_context_menu() ENTER")
        
    def search_text(self):       
        logger.debug("1st tab search_text() ENTER")
        self.search_dialog = TextSearchDialog(self)
        self.search_dialog.show()
        logger.debug("1st tab search_text() EXIT")
        
    def blockSignals(self):
        logger.debug("1st tab blockSignals() ENTER")
        
        self.text_edit.blockSignals(True)
        self.tree_widget.blockSignals(True)
        self.model.blockSignals(True)
        logger.debug("1st tab blockSignals() ENTER")
        
    def unblockSignals(self):
        logger.debug("1st tab unblockSignals() ENTER")
        self.text_edit.blockSignals(False)
        self.tree_widget.blockSignals(False)
        self.model.blockSignals(False)
        logger.debug("1st tab unblockSignals() ENTER")        
        
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
        print("1st Tab Sync from Text Window ENTER")
        self.main_window.background_processing_signal.emit(4, "1st Tab")
        
        # Set tree from text
        try:
            self.blockSignals()
            self.update_model_from_text_edit()
            self.update_tree_from_model()
            self.unblockSignals()
            
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Error", f"Failed to parse JSON from text window: {e}")
            
        self.tree_widget.expand_tree_to_level(1)
        self.update_tree_synced_indicator(True)            
        print("1st Tab Sync from Text Window EXIT")
        
            
    def sort_bases_by_gal_sys_name(self):
        logger.debug("1st tab Sort Bases clicked")
        self.main_window.background_processing_signal.emit(4, "1st Tab")
        
        model_json = self.model.get_json()
       
        """
        #Sort model_json in place based on the desired key
        model_json.sort(key=lambda el: (
            int(get_galaxy_system_planet_from_full_addr(el['GalacticAddress'])[GALAXY_FROM_GALACTIC_ADDR_IDX], 16),  # galaxy (characters 5 and 6)
            int(get_galaxy_system_planet_from_full_addr(el['GalacticAddress'])[SYSTEM_FROM_GALACTIC_ADDR_IDX], 16),  # system (characters 2 to 4)
            el['Name'] # base_name
        ))
        """
        
        model_json.sort(key=lambda el: (
            int(get_galaxy_system_planet_from_full_addr(el['GalacticAddress'])[GALAXY_FROM_GALACTIC_ADDR_IDX], 16) if el.get('GalacticAddress') else 0,  # default galaxy value
            int(get_galaxy_system_planet_from_full_addr(el['GalacticAddress'])[SYSTEM_FROM_GALACTIC_ADDR_IDX], 16) if el.get('GalacticAddress') else 0,  # default system value
            el['Name'] if el.get('Name') else ""  # default to empty string if 'Name' is missing
        ))    

        # Now loop through model_json and simulate the key generation for debug output
        for el in model_json:
            galaxy_value = int(get_galaxy_system_planet_from_full_addr(el['GalacticAddress'])[GALAXY_FROM_GALACTIC_ADDR_IDX], 16) if el.get('GalacticAddress') else 0
            system_value = int(get_galaxy_system_planet_from_full_addr(el['GalacticAddress'])[SYSTEM_FROM_GALACTIC_ADDR_IDX], 16) if el.get('GalacticAddress') else 0
            name_value = el['Name'] if el.get('Name') else ""

            # Print the sorting values used
            print(f"Debug key values: Galaxy: {galaxy_value}, System: {system_value}, Name: {name_value}")
        

        self.blockSignals()
        self.update_tree_from_model()
        self.update_text_widget_from_model()        
        self.unblockSignals()

    def sync_text_from_tree_window(self):
        logger.debug("1st tab sync from Tree Window ENTER")
        self.update_model_from_tree()
        self.update_text_widget_from_model()        
        logger.debug("1st tab sync from Tree Window EXIT")

    def update_model_from_text_edit(self):
        logger.debug("1st Tab update_model_from_text_edit() enter")        
        self.update_tree_synced_indicator(False)
        new_text = self.text_edit.toPlainText()
        self.model.set_text(new_text)
        logger.debug("1st Tab update_model_from_text_edit() exit")        

    def populate_tree(self, data, parent=None):
        logger.debug("1st tab populate_tree() ENTER")
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
                
        logger.debug("1st tab populate_tree() EXIT")                    

    def update_text_widget_from_model(self):
        logger.debug("1st Tab update_text_widget_from_model() enter")
        #self.blockSignals()
        self.text_edit.setPlainText(self.model.get_text())
        #self.unblockSignals()
        logger.debug("1st Tab update_text_widget_from_model() exit")
  
    def update_tree_from_model(self):
        logger.debug("1st tab update_tree_from_model() called")
        
        json_data = self.load_json_from_model()
        if json_data is not None:            
            self.blockSignals()
            self.clear_tree_view()
            self.populate_tree_from_json(json_data)
            self.unblockSignals()
            
            logger.debug("1st tab Tree view updated with model data.")            
            
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
        logger.debug("1st tab clear_tree_view() Called.")
        self.tree_widget.clear()        

    def populate_tree_from_json(self, json_data, parent_tree_node=None):
        #return
        logger.debug("1st tab populate_tree_from_json() ENTER")

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
                    #store off indication that tree node is for a base: 
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
        
        logger.debug("1st tab populate_tree_from_json() EXIT") 
        
    def init_text(self):
        return """[
        {
        "BaseVersio": 8,
        "OriginalBaseVersion": 5,
        "GalacticAddress": 39595225214000,
        "Position": [
            375.5400390625,
            -456.28515625,
            178.638671875
        ],
        "Forward": [
            0.7562813758850098,
            0.36866065859794617,
            0.5404864549636841
        ],
        "UserData": 0,
        "LastUpdateTimestamp": 1728532328,
        "Objects": [
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_IND",
                "UserData": 51,
                "Position": [
                    3.0517578125e-05,
                    4.000070571899414,
                    19.500091552734375
                ],
                "Up": [
                    8.742271262462964e-08,
                    1.0,
                    -4.76837158203125e-07
                ],
                "At": [
                    -1.5099583094979607e-07,
                    -4.76837158203125e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_IND",
                "UserData": 51,
                "Position": [
                    4.57763671875e-05,
                    4.00007438659668,
                    27.500152587890625
                ],
                "Up": [
                    8.742271262462964e-08,
                    1.0,
                    -4.76837158203125e-07
                ],
                "At": [
                    -1.509958451606508e-07,
                    -4.76837158203125e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_IND",
                "UserData": 51,
                "Position": [
                    9.1552734375e-05,
                    4.000078201293945,
                    35.500152587890625
                ],
                "Up": [
                    -1.509958451606508e-07,
                    1.0,
                    -3.576278402306343e-07
                ],
                "At": [
                    -1.5099578831723193e-07,
                    -3.5762786865234375e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^AIRLCKCONNECTOR",
                "UserData": 4294967296000,
                "Position": [
                    3.099999958067201e-05,
                    4.000005722045898,
                    15.500080108642578
                ],
                "Up": [
                    -8.742284762774943e-08,
                    1.0,
                    -4.76837158203125e-07
                ],
                "At": [
                    -1.509957598955225e-07,
                    -4.76837158203125e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^BRIDGECONNECTOR",
                "UserData": 0,
                "Position": [
                    3.099999958067201e-05,
                    4.000019073486328,
                    39.50008010864258
                ],
                "Up": [
                    0.0,
                    1.0,
                    -4.76837158203125e-07
                ],
                "At": [
                    0.0,
                    4.76837158203125e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^CEILINGLIGHT",
                "UserData": 0,
                "Position": [
                    14.365234375,
                    11.016468048095703,
                    -21.370014190673828
                ],
                "Up": [
                    0.0006624667439609766,
                    -1.0000008344650269,
                    0.0001490748836658895
                ],
                "At": [
                    0.9990383386611938,
                    0.0006683646352030337,
                    0.043840374797582626
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_IND",
                "UserData": 51,
                "Position": [
                    -7.9999542236328125,
                    4.000009536743164,
                    19.50006103515625
                ],
                "Up": [
                    4.371151263171669e-08,
                    1.0000011920928955,
                    -4.0419462266072514e-07
                ],
                "At": [
                    1.0,
                    -4.371138118131057e-08,
                    1.9470719792025193e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_NPCWEA",
                "UserData": 51,
                "Position": [
                    -15.999984741210938,
                    4.000009536743164,
                    19.499969482421875
                ],
                "Up": [
                    4.371141315573368e-08,
                    1.0000009536743164,
                    -5.010519998904783e-07
                ],
                "At": [
                    1.0,
                    -4.371139183945161e-08,
                    -4.3711366970455856e-08
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_FLEET",
                "UserData": 51,
                "Position": [
                    -7.999977111816406,
                    3.9999728202819824,
                    27.50006103515625
                ],
                "Up": [
                    4.371151263171669e-08,
                    1.0000009536743164,
                    -4.470349495022674e-07
                ],
                "At": [
                    1.0,
                    -4.371138118131057e-08,
                    1.9470721213110664e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_IND",
                "UserData": 51,
                "Position": [
                    16.0001220703125,
                    3.999887466430664,
                    19.5
                ],
                "Up": [
                    -4.371142381387472e-08,
                    1.0000011920928955,
                    -5.289918476591993e-07
                ],
                "At": [
                    -1.0,
                    -4.371139183945161e-08,
                    -4.3711366970455856e-08
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_FLEET",
                "UserData": 51,
                "Position": [
                    -15.99993896484375,
                    3.9997692108154297,
                    27.499969482421875
                ],
                "Up": [
                    -7.549781599891503e-08,
                    1.0000011920928955,
                    -4.544860701116704e-07
                ],
                "At": [
                    1.0,
                    7.54979225803254e-08,
                    4.331257343892503e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_TECH",
                "UserData": 51,
                "Position": [
                    8.0001220703125,
                    3.999943256378174,
                    35.500144958496094
                ],
                "Up": [
                    -4.371132078517803e-08,
                    1.000001072883606,
                    -3.3155095024994807e-07
                ],
                "At": [
                    -1.0,
                    -4.371140605030632e-08,
                    -4.013392356227996e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_ROCLOC",
                "UserData": 51,
                "Position": [
                    8.000015258789062,
                    4.000094890594482,
                    27.50018310546875
                ],
                "Up": [
                    8.742279078433057e-08,
                    1.0000009536743164,
                    -4.768376697938947e-07
                ],
                "At": [
                    -1.6391264523463178e-07,
                    -4.76837158203125e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_VEHICL",
                "UserData": 51,
                "Position": [
                    -15.999969482421875,
                    4.000005722045898,
                    11.500030517578125
                ],
                "Up": [
                    -7.54978870531886e-08,
                    1.0000011920928955,
                    -5.83008556986897e-07
                ],
                "At": [
                    1.0,
                    7.549790836947068e-08,
                    1.9470715528768778e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_IND",
                "UserData": 51,
                "Position": [
                    0.000152587890625,
                    4.000181198120117,
                    -4.499940872192383
                ],
                "Up": [
                    7.54979723183169e-08,
                    1.0,
                    -4.76837158203125e-07
                ],
                "At": [
                    -1.0,
                    7.549789415861596e-08,
                    -1.6292071336465597e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1718937519,
                "ObjectID": "^CRATELCYLINDER",
                "UserData": 0,
                "Position": [
                    -17.33160400390625,
                    3.4581289291381836,
                    -2.028291702270508
                ],
                "Up": [
                    -1.8847470073524164e-07,
                    1.0000011920928955,
                    -4.34122910064616e-07
                ],
                "At": [
                    0.47295814752578735,
                    4.716391970305267e-07,
                    0.8810849189758301
                ],
                "Message": ""
            },
            {
                "Timestamp": 1718937523,
                "ObjectID": "^CRATELCYLINDER",
                "UserData": 0,
                "Position": [
                    -17.478225708007812,
                    3.458127975463867,
                    -3.623353958129883
                ],
                "Up": [
                    1.350753620066314e-09,
                    1.0000011920928955,
                    -5.568938945543778e-07
                ],
                "At": [
                    0.9242266416549683,
                    2.1139813100035099e-07,
                    0.3818443715572357
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_REFINE",
                "UserData": 51,
                "Position": [
                    -15.999908447265625,
                    4.000123977661133,
                    3.500028610229492
                ],
                "Up": [
                    4.3711374075883214e-08,
                    1.000001072883606,
                    -4.172329965967947e-07
                ],
                "At": [
                    1.0,
                    -4.3711395392165286e-08,
                    -1.629206565212371e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_IND",
                "UserData": 51,
                "Position": [
                    -7.999908447265625,
                    4.000120162963867,
                    -4.499971389770508
                ],
                "Up": [
                    1.4901162970204496e-08,
                    1.0,
                    -4.76837158203125e-07
                ],
                "At": [
                    2.9802322387695312e-08,
                    4.76837158203125e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_FLEET",
                "UserData": 51,
                "Position": [
                    -23.999908447265625,
                    4.00001335144043,
                    27.50006103515625
                ],
                "Up": [
                    4.371168671468695e-08,
                    1.0000011920928955,
                    -6.034976536284375e-07
                ],
                "At": [
                    1.0,
                    -4.3711370523169535e-08,
                    4.3312579123266914e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    64.00041198730469,
                    4.000478744506836,
                    -20.5
                ],
                "Up": [
                    1.947075531916198e-07,
                    1.0000009536743164,
                    -4.798643544745573e-07
                ],
                "At": [
                    -1.0,
                    1.947071694985425e-07,
                    -4.0133934930963733e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -7.9996795654296875,
                    4.0002899169921875,
                    -28.4998779296875
                ],
                "Up": [
                    1.6292105442516913e-07,
                    1.0000009536743164,
                    -3.261960443978751e-07
                ],
                "At": [
                    1.0,
                    -1.629206565212371e-07,
                    7.907536883067223e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1718944724,
                "ObjectID": "^ROBOTICARM",
                "UserData": 0,
                "Position": [
                    -19.32025146484375,
                    7.531370162963867,
                    -4.510311126708984
                ],
                "Up": [
                    1.743441104888916,
                    -0.07315096259117126,
                    7.901776370999869e-07
                ],
                "At": [
                    -0.041920922696590424,
                    -0.9991209506988525,
                    4.6054569224907027e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_TELEPO",
                "UserData": 51,
                "Position": [
                    -15.999908447265625,
                    3.999760150909424,
                    35.499961853027344
                ],
                "Up": [
                    -7.549779468263296e-08,
                    1.0000009536743164,
                    -4.5448553009919124e-07
                ],
                "At": [
                    1.0,
                    7.54979225803254e-08,
                    4.331257343892503e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1718944775,
                "ObjectID": "^S_CANISTER0",
                "UserData": 0,
                "Position": [
                    -17.902542114257812,
                    3.458249092102051,
                    -6.39085578918457
                ],
                "Up": [
                    -2.0512611342837772e-07,
                    3.0000033378601074,
                    -1.6284670891764108e-06
                ],
                "At": [
                    0.6226565837860107,
                    4.6732972691643226e-07,
                    0.7824952602386475
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_IND",
                "UserData": 51,
                "Position": [
                    8.000152587890625,
                    3.999887466430664,
                    19.50000762939453
                ],
                "Up": [
                    7.549806468887255e-08,
                    1.0000011920928955,
                    -4.97326880122273e-07
                ],
                "At": [
                    -1.0,
                    7.549789415861596e-08,
                    -1.6292071336465597e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1718944786,
                "ObjectID": "^S_CANISTER0",
                "UserData": 0,
                "Position": [
                    -17.810943603515625,
                    3.45947265625,
                    -0.46050238609313965
                ],
                "Up": [
                    4.991707669432799e-08,
                    3.0000033378601074,
                    -1.4094435982769937e-06
                ],
                "At": [
                    0.9979745149612427,
                    -4.64920439924299e-08,
                    -0.06361398845911026
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_STORE0",
                "UserData": 51,
                "Position": [
                    3.0517578125e-05,
                    4.000005722045898,
                    11.50006103515625
                ],
                "Up": [
                    -1.606443541803524e-22,
                    1.0,
                    -4.76837158203125e-07
                ],
                "At": [
                    2.9802322387695312e-08,
                    4.76837158203125e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1718944807,
                "ObjectID": "^S_CANISTER1",
                "UserData": 0,
                "Position": [
                    -17.799148559570312,
                    3.458249092102051,
                    -5.114778518676758
                ],
                "Up": [
                    -5.670060421181233e-09,
                    2.3254761695861816,
                    -1.1112051652162336e-06
                ],
                "At": [
                    -0.06255250424146652,
                    4.7675158043603005e-07,
                    0.9980416893959045
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_FLEET",
                "UserData": 51,
                "Position": [
                    -24.000030517578125,
                    3.9999403953552246,
                    11.499977111816406
                ],
                "Up": [
                    1.5099598726919794e-07,
                    1.000001072883606,
                    -4.768376697938947e-07
                ],
                "At": [
                    5.9604531088552903e-08,
                    -4.76837158203125e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_PLANT1",
                "UserData": 51,
                "Position": [
                    8.00006103515625,
                    4.000005722045898,
                    11.500030517578125
                ],
                "Up": [
                    7.549780889348767e-08,
                    1.0,
                    -5.010515451431274e-07
                ],
                "At": [
                    -1.0,
                    7.549790836947068e-08,
                    1.9470715528768778e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_FLEET",
                "UserData": 51,
                "Position": [
                    -23.999908447265625,
                    4.000062942504883,
                    35.50006103515625
                ],
                "Up": [
                    1.5099590200406965e-07,
                    1.0,
                    -7.152557373046875e-07
                ],
                "At": [
                    1.5099571726295835e-07,
                    -7.152557373046875e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_STORE1",
                "UserData": 51,
                "Position": [
                    6.103515625e-05,
                    4.000001907348633,
                    3.500028610229492
                ],
                "Up": [
                    4.371132789060539e-08,
                    1.0,
                    -4.172325134277344e-07
                ],
                "At": [
                    1.0,
                    -4.3711395392165286e-08,
                    -1.629206565212371e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_STORE2",
                "UserData": 51,
                "Position": [
                    -7.999969482421875,
                    4.000127792358398,
                    11.500091552734375
                ],
                "Up": [
                    -8.742271262462964e-08,
                    1.0,
                    -4.76837158203125e-07
                ],
                "At": [
                    1.5099583094979607e-07,
                    -4.76837158203125e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_STORE3",
                "UserData": 51,
                "Position": [
                    -7.99993896484375,
                    4.000062942504883,
                    3.499998092651367
                ],
                "Up": [
                    4.371132789060539e-08,
                    1.0,
                    -4.172325134277344e-07
                ],
                "At": [
                    1.0,
                    -4.3711395392165286e-08,
                    -1.629206565212371e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_PLANT1",
                "UserData": 51,
                "Position": [
                    16.0001220703125,
                    3.9999446868896484,
                    11.50006103515625
                ],
                "Up": [
                    7.549781599891503e-08,
                    1.0,
                    -4.76837158203125e-07
                ],
                "At": [
                    -1.0,
                    7.549790836947068e-08,
                    1.9470715528768778e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_PLANT1",
                "UserData": 51,
                "Position": [
                    8.00006103515625,
                    4.000062942504883,
                    3.500059127807617
                ],
                "Up": [
                    7.549781599891503e-08,
                    1.0,
                    -4.76837158203125e-07
                ],
                "At": [
                    -1.0,
                    7.549790836947068e-08,
                    1.9470715528768778e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_PLANT1",
                "UserData": 51,
                "Position": [
                    16.000137329101562,
                    4.000062942504883,
                    3.500089645385742
                ],
                "Up": [
                    5.960464477539063e-08,
                    1.0000001192092896,
                    -4.768372150465439e-07
                ],
                "At": [
                    2.086162567138672e-07,
                    4.76837158203125e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_PLANT1",
                "UserData": 51,
                "Position": [
                    24.000137329101562,
                    4.000066757202148,
                    11.5001220703125
                ],
                "Up": [
                    2.9802322387695312e-08,
                    1.0,
                    -4.76837158203125e-07
                ],
                "At": [
                    1.788139485370266e-07,
                    4.76837158203125e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_PLANT1",
                "UserData": 51,
                "Position": [
                    24.00018310546875,
                    4.000123977661133,
                    3.500120162963867
                ],
                "Up": [
                    5.960465898624534e-08,
                    1.0,
                    -4.76837158203125e-07
                ],
                "At": [
                    5.960465188081798e-08,
                    4.76837158203125e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_PLANT1",
                "UserData": 51,
                "Position": [
                    8.000091552734375,
                    4.000181198120117,
                    -4.499910354614258
                ],
                "Up": [
                    1.4901162970204496e-08,
                    1.0,
                    -4.76837158203125e-07
                ],
                "At": [
                    2.3841860752327193e-07,
                    4.76837158203125e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_PLANT1",
                "UserData": 51,
                "Position": [
                    16.000106811523438,
                    4.000242233276367,
                    -4.499910354614258
                ],
                "Up": [
                    2.9802322387695312e-08,
                    1.0,
                    -4.76837158203125e-07
                ],
                "At": [
                    2.9802320611338473e-08,
                    4.76837158203125e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_PLANT1",
                "UserData": 51,
                "Position": [
                    24.000213623046875,
                    4.000181198120117,
                    -4.499849319458008
                ],
                "Up": [
                    1.4901171851988693e-08,
                    1.0,
                    -3.5762786865234375e-07
                ],
                "At": [
                    8.940696716308594e-08,
                    3.5762786865234375e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    16.0001220703125,
                    12.000160217285156,
                    -44.4998779296875
                ],
                "Up": [
                    7.549799363459897e-08,
                    1.0000009536743164,
                    -5.345796125766356e-07
                ],
                "At": [
                    -1.0,
                    7.549790126404332e-08,
                    -4.3711430919302074e-08
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    8.000091552734375,
                    4.000116348266602,
                    -12.4998779296875
                ],
                "Up": [
                    4.3711366970455856e-08,
                    1.0000009536743164,
                    -4.458711373445112e-07
                ],
                "At": [
                    1.0,
                    -4.3711395392165286e-08,
                    -1.629206565212371e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    0.0001220703125,
                    4.000173568725586,
                    -20.4998779296875
                ],
                "Up": [
                    4.371141315573368e-08,
                    1.0000009536743164,
                    -5.047772901889402e-07
                ],
                "At": [
                    1.0,
                    -4.371139183945161e-08,
                    -4.3711366970455856e-08
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -7.999755859375,
                    4.000173568725586,
                    -20.499755859375
                ],
                "Up": [
                    1.62921111268588e-07,
                    1.0000009536743164,
                    -4.447069841262419e-07
                ],
                "At": [
                    1.0,
                    -1.629206565212371e-07,
                    6.715443987559411e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    8.000381469726562,
                    4.000288009643555,
                    -36.4998779296875
                ],
                "Up": [
                    1.7881393432617188e-07,
                    1.0000009536743164,
                    -3.576280960260192e-07
                ],
                "At": [
                    -7.366754175563983e-07,
                    3.5762786865234375e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    8.000396728515625,
                    4.000284194946289,
                    -44.4998779296875
                ],
                "Up": [
                    1.7881393432617188e-07,
                    1.0000009536743164,
                    -3.576280960260192e-07
                ],
                "At": [
                    -7.385380627056293e-07,
                    3.5762786865234375e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -23.999664306640625,
                    4.000165939331055,
                    -36.5
                ],
                "Up": [
                    2.3841843699301535e-07,
                    1.0000009536743164,
                    -3.576279254957626e-07
                ],
                "At": [
                    -1.1846410643556737e-06,
                    3.5762786865234375e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -23.999603271484375,
                    3.9999866485595703,
                    -28.49993896484375
                ],
                "Up": [
                    1.7881380642847944e-07,
                    1.0000011920928955,
                    -3.576280960260192e-07
                ],
                "At": [
                    -1.1399375807741308e-06,
                    3.5762786865234375e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -31.999557495117188,
                    4.0000457763671875,
                    -28.499908447265625
                ],
                "Up": [
                    2.0861610039446532e-07,
                    1.0000009536743164,
                    -3.5762798233918147e-07
                ],
                "At": [
                    -1.1026846777895116e-06,
                    3.5762786865234375e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -31.999755859375,
                    4.000234603881836,
                    -20.4998779296875
                ],
                "Up": [
                    -7.549787994776125e-08,
                    1.0,
                    -2.6822092991096724e-07
                ],
                "At": [
                    1.0,
                    7.549790126404332e-08,
                    7.549787994776125e-08
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -39.99974060058594,
                    4.000295639038086,
                    -20.499847412109375
                ],
                "Up": [
                    -7.54978870531886e-08,
                    1.0000001192092896,
                    -2.6822092991096724e-07
                ],
                "At": [
                    1.0,
                    7.549790126404332e-08,
                    7.549787994776125e-08
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -47.99974060058594,
                    4.000356674194336,
                    -20.49981689453125
                ],
                "Up": [
                    -7.54978870531886e-08,
                    1.0,
                    -2.086162567138672e-07
                ],
                "At": [
                    1.0,
                    7.549790126404332e-08,
                    7.54978870531886e-08
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -55.99974060058594,
                    4.000417709350586,
                    -20.499786376953125
                ],
                "Up": [
                    -7.54978870531886e-08,
                    1.0,
                    -2.384185791015625e-07
                ],
                "At": [
                    1.0,
                    7.549790126404332e-08,
                    7.54978870531886e-08
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -63.99971008300781,
                    4.000417709350586,
                    -20.499755859375
                ],
                "Up": [
                    -7.54978870531886e-08,
                    1.0,
                    -1.788139627478813e-07
                ],
                "At": [
                    1.0,
                    7.549790126404332e-08,
                    7.54978870531886e-08
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    16.000404357910156,
                    4.000284194946289,
                    -44.4998779296875
                ],
                "Up": [
                    1.9470768108931225e-07,
                    1.0000009536743164,
                    -3.858006607515563e-07
                ],
                "At": [
                    -1.0,
                    1.9470714107683307e-07,
                    -8.781764790910529e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    24.000396728515625,
                    4.000345230102539,
                    -44.4998779296875
                ],
                "Up": [
                    1.9470768108931225e-07,
                    1.0000009536743164,
                    -3.909229349119414e-07
                ],
                "At": [
                    -1.0,
                    1.9470714107683307e-07,
                    -8.781764790910529e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    0.000396728515625,
                    4.000223159790039,
                    -44.4998779296875
                ],
                "Up": [
                    2.821304576627881e-07,
                    1.0000009536743164,
                    -3.4784920899255667e-07
                ],
                "At": [
                    1.0,
                    -2.8212994607201836e-07,
                    7.907537451501412e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -39.999725341796875,
                    4.0002899169921875,
                    -28.4998779296875
                ],
                "Up": [
                    4.3711519737144044e-08,
                    1.0000011920928955,
                    -2.896418891396024e-07
                ],
                "At": [
                    1.0,
                    -4.3711374075883214e-08,
                    3.139165016818879e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_W_STA",
                "UserData": 51,
                "Position": [
                    0.0001220703125,
                    4.0001068115234375,
                    -28.4998779296875
                ],
                "Up": [
                    8.940693874137651e-08,
                    1.0000009536743164,
                    -4.768376129504759e-07
                ],
                "At": [
                    -1.6577520511873445e-07,
                    4.76837158203125e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    24.000259399414062,
                    4.000417709350586,
                    -20.49981689453125
                ],
                "Up": [
                    -4.371141315573368e-08,
                    1.0,
                    -3.5762786865234375e-07
                ],
                "At": [
                    -1.0,
                    -4.371138473402425e-08,
                    7.549791547489804e-08
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -7.999580383300781,
                    4.000162124633789,
                    -44.49993896484375
                ],
                "Up": [
                    1.6292108284687856e-07,
                    1.0000009536743164,
                    -3.483149555449927e-07
                ],
                "At": [
                    1.0,
                    -1.629206565212371e-07,
                    7.907536883067223e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    40.00038146972656,
                    4.000532150268555,
                    -36.49993896484375
                ],
                "Up": [
                    1.4901159772762185e-07,
                    1.0000009536743164,
                    -4.768376129504759e-07
                ],
                "At": [
                    2.9802293965985882e-08,
                    4.76837158203125e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    48.000335693359375,
                    4.000478744506836,
                    -20.4998779296875
                ],
                "Up": [
                    1.947075531916198e-07,
                    1.0000011920928955,
                    -3.96511182998438e-07
                ],
                "At": [
                    -1.0,
                    1.947071694985425e-07,
                    -4.013393208879279e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    56.00038146972656,
                    4.000539779663086,
                    -20.4998779296875
                ],
                "Up": [
                    1.9470752476991038e-07,
                    1.0000009536743164,
                    -4.286415844489966e-07
                ],
                "At": [
                    -1.0,
                    1.947071694985425e-07,
                    -4.013393208879279e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -7.999656677246094,
                    4.000226974487305,
                    -36.4998779296875
                ],
                "Up": [
                    1.7881372116335115e-07,
                    1.0000009536743164,
                    -3.2584145515102136e-07
                ],
                "At": [
                    1.104670104723482e-06,
                    -3.2584134146418364e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    72.00039672851562,
                    4.000417709350586,
                    -20.499664306640625
                ],
                "Up": [
                    -4.371141315573368e-08,
                    1.0,
                    -3.5762786865234375e-07
                ],
                "At": [
                    -1.0,
                    -4.371138473402425e-08,
                    7.549791547489804e-08
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^TOXICPLANT",
                "UserData": 61847529062400,
                "Position": [
                    24.000274658203125,
                    3.802548408508301,
                    -5.499818801879883
                ],
                "Up": [
                    -1.4901146982992941e-08,
                    1.0,
                    -3.5762786865234375e-07
                ],
                "At": [
                    1.1920928244535389e-07,
                    3.5762786865234375e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^TOXICPLANT",
                "UserData": 61847529062400,
                "Position": [
                    24.000244140625,
                    3.802549362182617,
                    -3.499849319458008
                ],
                "Up": [
                    -1.4901146982992941e-08,
                    1.0,
                    -3.5762786865234375e-07
                ],
                "At": [
                    1.1920928244535389e-07,
                    3.5762786865234375e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^NIPPLANT",
                "UserData": 61847529062400,
                "Position": [
                    24.000213623046875,
                    3.8023691177368164,
                    2.5001163482666016
                ],
                "Up": [
                    5.215406062575312e-08,
                    1.0000011920928955,
                    -3.576282949779852e-07
                ],
                "At": [
                    -2.9802285084201685e-08,
                    3.5762786865234375e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^NIPPLANT",
                "UserData": 61847529062400,
                "Position": [
                    24.00018310546875,
                    3.802370071411133,
                    4.500085830688477
                ],
                "Up": [
                    5.215406062575312e-08,
                    1.0000011920928955,
                    -3.576282949779852e-07
                ],
                "At": [
                    -2.9802285084201685e-08,
                    3.5762786865234375e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^NIPPLANT",
                "UserData": 61847529062400,
                "Position": [
                    24.000152587890625,
                    3.802250862121582,
                    10.500091552734375
                ],
                "Up": [
                    1.862644971595273e-08,
                    1.0000009536743164,
                    -4.768376129504759e-07
                ],
                "At": [
                    1.7881374958506058e-07,
                    4.76837158203125e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^NIPPLANT",
                "UserData": 61847529062400,
                "Position": [
                    24.000152587890625,
                    3.8022518157958984,
                    12.50008773803711
                ],
                "Up": [
                    1.862644971595273e-08,
                    1.0000009536743164,
                    -4.768376129504759e-07
                ],
                "At": [
                    1.7881374958506058e-07,
                    4.76837158203125e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^NIPPLANT",
                "UserData": 61847529062400,
                "Position": [
                    17.000152587890625,
                    3.8022518157958984,
                    11.500110626220703
                ],
                "Up": [
                    -4.371152328985772e-08,
                    1.000001072883606,
                    -4.824255483981688e-07
                ],
                "At": [
                    -1.0,
                    -4.371138118131057e-08,
                    1.9470721213110664e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^NIPPLANT",
                "UserData": 61847529062400,
                "Position": [
                    15.000152587890625,
                    3.8022518157958984,
                    11.500076293945312
                ],
                "Up": [
                    -4.371152328985772e-08,
                    1.000001072883606,
                    -4.824255483981688e-07
                ],
                "At": [
                    -1.0,
                    -4.371138118131057e-08,
                    1.9470721213110664e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^NIPPLANT",
                "UserData": 61847529062400,
                "Position": [
                    9.000106811523438,
                    3.8023738861083984,
                    11.500049591064453
                ],
                "Up": [
                    7.549794389660747e-08,
                    1.000001072883606,
                    -4.824256052415876e-07
                ],
                "At": [
                    -1.0,
                    7.549790126404332e-08,
                    7.549786573690653e-08
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^NIPPLANT",
                "UserData": 61847529062400,
                "Position": [
                    7.000091552734375,
                    3.8022518157958984,
                    11.500080108642578
                ],
                "Up": [
                    7.549794389660747e-08,
                    1.000001072883606,
                    -4.824256052415876e-07
                ],
                "At": [
                    -1.0,
                    7.549790126404332e-08,
                    7.549786573690653e-08
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^TOXICPLANT",
                "UserData": 61847529062400,
                "Position": [
                    7.0000762939453125,
                    3.802370071411133,
                    3.500059127807617
                ],
                "Up": [
                    7.549775205006881e-08,
                    1.0,
                    -5.066394805908203e-07
                ],
                "At": [
                    -1.0,
                    7.549791547489804e-08,
                    3.1391644483846903e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^TOXICPLANT",
                "UserData": 61847529062400,
                "Position": [
                    9.000076293945312,
                    3.802431106567383,
                    3.500059127807617
                ],
                "Up": [
                    7.549775205006881e-08,
                    1.0,
                    -5.066394805908203e-07
                ],
                "At": [
                    -1.0,
                    7.549791547489804e-08,
                    3.1391644483846903e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^NIPPLANT",
                "UserData": 61847529062400,
                "Position": [
                    16.000152587890625,
                    3.802370071411133,
                    4.50007438659668
                ],
                "Up": [
                    5.587936513506975e-08,
                    1.0000011920928955,
                    -4.768377266373136e-07
                ],
                "At": [
                    1.788137637959153e-07,
                    4.76837158203125e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^NIPPLANT",
                "UserData": 61847529062400,
                "Position": [
                    16.000152587890625,
                    3.8023691177368164,
                    2.5000782012939453
                ],
                "Up": [
                    5.587936513506975e-08,
                    1.0000011920928955,
                    -4.768377266373136e-07
                ],
                "At": [
                    1.788137637959153e-07,
                    4.76837158203125e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^TOXICPLANT",
                "UserData": 61847529062400,
                "Position": [
                    16.000137329101562,
                    3.802549362182617,
                    -3.499910354614258
                ],
                "Up": [
                    5.960462701182223e-08,
                    1.0,
                    -5.960464477539062e-07
                ],
                "At": [
                    2.980232594040899e-08,
                    5.960464477539062e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^TOXICPLANT",
                "UserData": 61847529062400,
                "Position": [
                    16.000167846679688,
                    3.802609443664551,
                    -5.499910354614258
                ],
                "Up": [
                    5.960462701182223e-08,
                    1.0,
                    -5.960464477539062e-07
                ],
                "At": [
                    2.980232594040899e-08,
                    5.960464477539062e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_DOOR_A",
                "UserData": 51,
                "Position": [
                    0.00017547607421875,
                    4.000051498413086,
                    -16.49993896484375
                ],
                "Up": [
                    2.9802322387695312e-08,
                    1.0000009536743164,
                    -4.768376129504759e-07
                ],
                "At": [
                    -1.4808013304445922e-07,
                    4.76837158203125e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^TOXICPLANT",
                "UserData": 61847529062400,
                "Position": [
                    8.0001220703125,
                    3.802488327026367,
                    -3.499910354614258
                ],
                "Up": [
                    1.4901161193847656e-08,
                    1.0,
                    -4.76837158203125e-07
                ],
                "At": [
                    2.384185791015625e-07,
                    4.76837158203125e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    24.000228881835938,
                    4.000410079956055,
                    -36.4998779296875
                ],
                "Up": [
                    5.960463056453591e-08,
                    1.0000009536743164,
                    -4.450510289188969e-07
                ],
                "At": [
                    3.8941436741879443e-07,
                    -4.450506310149649e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    16.00011444091797,
                    4.000234603881836,
                    -20.49981689453125
                ],
                "Up": [
                    7.549799363459897e-08,
                    1.0000009536743164,
                    -5.047772901889402e-07
                ],
                "At": [
                    -1.0,
                    7.549790126404332e-08,
                    -4.3711427366588396e-08
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    8.00042724609375,
                    4.000219345092773,
                    -52.4998779296875
                ],
                "Up": [
                    1.7881393432617188e-07,
                    1.0000009536743164,
                    -3.576280960260192e-07
                ],
                "At": [
                    -7.394693852802448e-07,
                    3.5762786865234375e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    16.000404357910156,
                    4.000280380249023,
                    -52.49981689453125
                ],
                "Up": [
                    1.9470770951102168e-07,
                    1.0000009536743164,
                    -4.3213395883867634e-07
                ],
                "At": [
                    -1.0,
                    1.9470714107683307e-07,
                    -8.781764790910529e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    24.000381469726562,
                    4.000280380249023,
                    -52.4998779296875
                ],
                "Up": [
                    1.9470778056529525e-07,
                    1.0000009536743164,
                    -4.996548454982985e-07
                ],
                "At": [
                    -1.0,
                    1.9470714107683307e-07,
                    -8.781764790910529e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -7.9995574951171875,
                    4.000097274780273,
                    -52.49993896484375
                ],
                "Up": [
                    1.6292119653371628e-07,
                    1.0000009536743164,
                    -3.9907200743982685e-07
                ],
                "At": [
                    1.0,
                    -1.629206423103824e-07,
                    1.0291722674082848e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    0.0004425048828125,
                    4.000158309936523,
                    -52.49993896484375
                ],
                "Up": [
                    8.940688189795765e-08,
                    1.0000009536743164,
                    -3.5762815286943805e-07
                ],
                "At": [
                    -7.208428769445163e-07,
                    3.5762786865234375e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_W_STA",
                "UserData": 51,
                "Position": [
                    16.000106811523438,
                    12.000164031982422,
                    -36.49993896484375
                ],
                "Up": [
                    1.5099602990176209e-07,
                    1.0000009536743164,
                    -5.960470161880949e-07
                ],
                "At": [
                    1.509957598955225e-07,
                    -5.960464477539062e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    8.0001220703125,
                    12.000160217285156,
                    -44.49993896484375
                ],
                "Up": [
                    2.9802315282267955e-08,
                    1.0000009536743164,
                    -4.768376129504759e-07
                ],
                "At": [
                    -1.1920916165308881e-07,
                    4.76837158203125e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    0.00012969970703125,
                    12.000160217285156,
                    -44.49993896484375
                ],
                "Up": [
                    2.980233304583635e-08,
                    1.0000009536743164,
                    -5.960470161880949e-07
                ],
                "At": [
                    -1.0337669920090775e-07,
                    5.960464477539062e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    0.000152587890625,
                    12.000099182128906,
                    -52.49993896484375
                ],
                "Up": [
                    1.2346891799166083e-14,
                    1.0000009536743164,
                    -5.960470161880949e-07
                ],
                "At": [
                    -1.0430802888095059e-07,
                    5.960464477539062e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    16.0001220703125,
                    12.000160217285156,
                    -52.49993896484375
                ],
                "Up": [
                    7.549799363459897e-08,
                    1.0000009536743164,
                    -5.646147656079847e-07
                ],
                "At": [
                    -1.0,
                    7.549790126404332e-08,
                    -4.371143447201575e-08
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    8.000152587890625,
                    12.000099182128906,
                    -52.49993896484375
                ],
                "Up": [
                    -4.3711278152613886e-08,
                    1.0000009536743164,
                    -5.948827492829878e-07
                ],
                "At": [
                    -1.0,
                    -4.3711398944878965e-08,
                    -2.8212994607201836e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    24.000167846679688,
                    11.999847412109375,
                    -60.4998779296875
                ],
                "Up": [
                    1.4901172562531428e-07,
                    1.0000009536743164,
                    -5.960468456578383e-07
                ],
                "At": [
                    -1.0943027746179723e-06,
                    5.960464477539062e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    24.0001220703125,
                    12.000160217285156,
                    -44.4998779296875
                ],
                "Up": [
                    1.5099602990176209e-07,
                    1.0000009536743164,
                    -5.960470161880949e-07
                ],
                "At": [
                    1.509957598955225e-07,
                    -5.960464477539062e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -47.99971008300781,
                    4.0004119873046875,
                    -28.49981689453125
                ],
                "Up": [
                    -7.549795810746218e-08,
                    1.0000011920928955,
                    -2.216553411926725e-07
                ],
                "At": [
                    1.0,
                    7.549790836947068e-08,
                    1.947071694985425e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    24.0001220703125,
                    12.000164031982422,
                    -36.49993896484375
                ],
                "Up": [
                    1.5099602990176209e-07,
                    1.0000009536743164,
                    -5.960470161880949e-07
                ],
                "At": [
                    1.509957598955225e-07,
                    -5.960464477539062e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -55.99971008300781,
                    4.0004119873046875,
                    -28.499786376953125
                ],
                "Up": [
                    -7.549791547489804e-08,
                    1.0000011920928955,
                    -2.845196434009267e-07
                ],
                "At": [
                    1.0,
                    7.549791547489804e-08,
                    3.1391647326017846e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -63.99967956542969,
                    4.0005340576171875,
                    -28.499786376953125
                ],
                "Up": [
                    4.371150552628933e-08,
                    1.0000011920928955,
                    -1.8626505493557488e-07
                ],
                "At": [
                    1.0,
                    -4.3711370523169535e-08,
                    4.331257628109597e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    24.0001220703125,
                    12.000171661376953,
                    -28.49993896484375
                ],
                "Up": [
                    1.509959588474885e-07,
                    1.0000009536743164,
                    -5.960470161880949e-07
                ],
                "At": [
                    4.284074961447004e-08,
                    -5.960464477539062e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    24.0001220703125,
                    12.000171661376953,
                    -20.49993896484375
                ],
                "Up": [
                    1.5099597305834322e-07,
                    1.0000009536743164,
                    -5.960470161880949e-07
                ],
                "At": [
                    5.122267054957774e-08,
                    -5.960464477539062e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    16.00012969970703,
                    12.000110626220703,
                    -20.5
                ],
                "Up": [
                    1.6292095494918613e-07,
                    1.0000009536743164,
                    -6.272461519074568e-07
                ],
                "At": [
                    1.0,
                    -1.6292067073209182e-07,
                    1.9470729739623494e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    8.000129699707031,
                    12.000049591064453,
                    -20.5
                ],
                "Up": [
                    1.6292096916004084e-07,
                    1.000001072883606,
                    -6.598424420189986e-07
                ],
                "At": [
                    1.0,
                    -1.6292067073209182e-07,
                    1.9470729739623494e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    40.000244140625,
                    3.9996814727783203,
                    -28.5001220703125
                ],
                "Up": [
                    -7.549667202511046e-08,
                    1.000001072883606,
                    -9.089714012588956e-07
                ],
                "At": [
                    1.0,
                    7.549796521288954e-08,
                    1.506009311924572e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    0.0001373291015625,
                    11.999988555908203,
                    -20.5
                ],
                "Up": [
                    1.6292095494918613e-07,
                    1.0000009536743164,
                    -6.526247489091475e-07
                ],
                "At": [
                    1.0,
                    -1.6292067073209182e-07,
                    1.9470729739623494e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -7.999847412109375,
                    11.999927520751953,
                    -20.5
                ],
                "Up": [
                    1.6292095494918613e-07,
                    1.0000009536743164,
                    -6.523919182654936e-07
                ],
                "At": [
                    1.0,
                    -1.6292067073209182e-07,
                    1.9470729739623494e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    72.0004653930664,
                    4.000364303588867,
                    -4.499696731567383
                ],
                "Up": [
                    1.5099583094979607e-07,
                    0.9999999403953552,
                    -3.576278118089249e-07
                ],
                "At": [
                    1.5099580252808664e-07,
                    -3.5762786865234375e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    72.00049591064453,
                    4.000337600708008,
                    3.500272750854492
                ],
                "Up": [
                    3.8941439584050386e-07,
                    0.9999999403953552,
                    -3.5762778338721546e-07
                ],
                "At": [
                    1.341104507446289e-07,
                    -3.5762786865234375e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    72.0005111694336,
                    4.000310897827148,
                    11.500274658203125
                ],
                "Up": [
                    3.8941448110563215e-07,
                    0.9999999403953552,
                    -3.5762769812208717e-07
                ],
                "At": [
                    3.894144242622133e-07,
                    -3.5762786865234375e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    72.00054168701172,
                    4.000284194946289,
                    19.500244140625
                ],
                "Up": [
                    3.874303331485862e-07,
                    0.9999999403953552,
                    -2.0663189559400053e-07
                ],
                "At": [
                    3.89414338997085e-07,
                    -2.0663208033511182e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    72.00057220458984,
                    4.00025749206543,
                    27.500244140625
                ],
                "Up": [
                    4.7683710135970614e-07,
                    0.9999998807907104,
                    -2.066318671722911e-07
                ],
                "At": [
                    3.8941431057537557e-07,
                    -2.0663208033511182e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    72.00060272216797,
                    4.00023078918457,
                    35.500244140625
                ],
                "Up": [
                    3.278254325778107e-07,
                    0.9999998807907104,
                    -8.742264867578342e-08
                ],
                "At": [
                    3.8941436741879443e-07,
                    -8.742277657347586e-08,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    72.0003890991211,
                    4.0004119873046875,
                    -28.499664306640625
                ],
                "Up": [
                    2.9802309953197437e-08,
                    0.9999998807907104,
                    -3.576278402306343e-07
                ],
                "At": [
                    2.980232949312267e-08,
                    3.5762786865234375e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -7.999839782714844,
                    11.999866485595703,
                    -28.5
                ],
                "Up": [
                    1.62921111268588e-07,
                    1.0000009536743164,
                    -6.665945306849608e-07
                ],
                "At": [
                    1.0,
                    -1.6292067073209182e-07,
                    4.3312587649779744e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    72.00040435791016,
                    4.000406265258789,
                    -44.49967956542969
                ],
                "Up": [
                    1.7881392011531716e-07,
                    0.9999999403953552,
                    -2.3841855067985307e-07
                ],
                "At": [
                    -1.0658136801236767e-14,
                    2.384185791015625e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    72.00042724609375,
                    4.000402450561523,
                    -52.49969482421875
                ],
                "Up": [
                    2.980232238769531e-07,
                    0.9999999403953552,
                    -3.576278118089249e-07
                ],
                "At": [
                    -1.3411046495548362e-07,
                    3.5762786865234375e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    72.00043487548828,
                    4.000396728515625,
                    -60.49969482421875
                ],
                "Up": [
                    4.172327976448287e-07,
                    0.9999999403953552,
                    -3.576277265437966e-07
                ],
                "At": [
                    -2.831220911048149e-07,
                    3.5762786865234375e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    72.00045776367188,
                    4.000394821166992,
                    -68.49971008300781
                ],
                "Up": [
                    3.874303331485862e-07,
                    0.9999999403953552,
                    -2.3841842278216063e-07
                ],
                "At": [
                    -3.427267358802055e-07,
                    2.384185791015625e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    72.0004653930664,
                    4.000391006469727,
                    -76.49971008300781
                ],
                "Up": [
                    4.76837158203125e-07,
                    0.9999998807907104,
                    -2.3841835172788706e-07
                ],
                "At": [
                    -4.023314090773056e-07,
                    2.3841856489070778e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    72.00047302246094,
                    4.000387191772461,
                    -84.49972534179688
                ],
                "Up": [
                    3.2782546099952015e-07,
                    0.9999998807907104,
                    -1.192091474422341e-07
                ],
                "At": [
                    -4.1723268395799096e-07,
                    1.1920928955078125e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    72.00048065185547,
                    4.000383377075195,
                    -92.49972534179688
                ],
                "Up": [
                    3.8743036157029564e-07,
                    0.9999999403953552,
                    1.8118839761882555e-13
                ],
                "At": [
                    -4.6193639491320937e-07,
                    0.0,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    72.0005111694336,
                    4.000410079956055,
                    -100.49972534179688
                ],
                "Up": [
                    4.76837158203125e-07,
                    0.9999999403953552,
                    2.2737367544323206e-13
                ],
                "At": [
                    -4.768372150465439e-07,
                    0.0,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    72.00051879882812,
                    4.000406265258789,
                    -108.499755859375
                ],
                "Up": [
                    5.662440685227921e-07,
                    0.9999999403953552,
                    2.8066438062523957e-13
                ],
                "At": [
                    -4.917383762403915e-07,
                    0.0,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    72.00053405761719,
                    4.000402450561523,
                    -116.499755859375
                ],
                "Up": [
                    6.55651035685878e-07,
                    0.9999999403953552,
                    3.446132268436486e-13
                ],
                "At": [
                    -5.215406986280868e-07,
                    0.0,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    72.00054931640625,
                    4.000429153442383,
                    -124.499755859375
                ],
                "Up": [
                    7.450583439094771e-07,
                    0.9999999403953552,
                    4.121147867408581e-13
                ],
                "At": [
                    -5.513430210157821e-07,
                    0.0,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    64.00056457519531,
                    4.000429153442383,
                    -124.49977111816406
                ],
                "Up": [
                    8.781761948739586e-07,
                    0.9999998807907104,
                    8.940756401898398e-08
                ],
                "At": [
                    1.0,
                    -8.781763654042152e-07,
                    6.715442850691034e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    56.000587463378906,
                    4.000429153442383,
                    -124.49980163574219
                ],
                "Up": [
                    8.781761948739586e-07,
                    0.9999998807907104,
                    1.490122087943746e-07
                ],
                "At": [
                    1.0,
                    -8.781763654042152e-07,
                    6.715442282256845e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    48.000633239746094,
                    4.000459671020508,
                    -124.49984741210938
                ],
                "Up": [
                    9.97385427581321e-07,
                    0.9999999403953552,
                    2.0861723726284254e-07
                ],
                "At": [
                    1.0,
                    -9.973856549549964e-07,
                    7.907535177764657e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    40.00066375732422,
                    4.000459671020508,
                    -124.4998779296875
                ],
                "Up": [
                    1.1165946034452645e-06,
                    0.9999999403953552,
                    2.384196307048114e-07
                ],
                "At": [
                    1.0,
                    -1.1165949445057777e-06,
                    7.907534609330469e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    32.00067901611328,
                    4.000490188598633,
                    -124.49990844726562
                ],
                "Up": [
                    9.973853138944833e-07,
                    0.9999999403953552,
                    2.980243039019115e-07
                ],
                "At": [
                    1.0,
                    -9.973856549549964e-07,
                    7.90753404089628e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    24.000694274902344,
                    4.000490188598633,
                    -124.49992370605469
                ],
                "Up": [
                    1.1165946034452645e-06,
                    0.9999999403953552,
                    3.576291192075587e-07
                ],
                "At": [
                    1.0,
                    -1.1165949445057777e-06,
                    7.907532904027903e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    16.00072479248047,
                    4.000490188598633,
                    -124.49993896484375
                ],
                "Up": [
                    1.235803779309208e-06,
                    0.9999999403953552,
                    3.8743141317354457e-07
                ],
                "At": [
                    1.0,
                    -1.235804234056559e-06,
                    7.907532335593714e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    8.000755310058594,
                    4.000490188598633,
                    -124.49996948242188
                ],
                "Up": [
                    1.1165944897584268e-06,
                    0.9999999403953552,
                    4.470360863706446e-07
                ],
                "At": [
                    1.0,
                    -1.1165949445057777e-06,
                    7.907531767159526e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    0.00078582763671875,
                    4.000490188598633,
                    -124.5
                ],
                "Up": [
                    1.116594376071589e-06,
                    0.9999999403953552,
                    5.066407311460353e-07
                ],
                "At": [
                    1.0,
                    -1.1165949445057777e-06,
                    9.09962409423315e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -7.999214172363281,
                    4.000490188598633,
                    -124.50003051757812
                ],
                "Up": [
                    1.116594376071589e-06,
                    0.9999998807907104,
                    5.364428261600551e-07
                ],
                "At": [
                    1.0,
                    -1.1165949445057777e-06,
                    9.099623525798961e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -15.999176025390625,
                    4.000490188598633,
                    -124.50006103515625
                ],
                "Up": [
                    1.2358036656223703e-06,
                    1.0,
                    5.960476983091212e-07
                ],
                "At": [
                    1.0,
                    -1.235804234056559e-06,
                    9.099621820496395e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -23.99915313720703,
                    4.000490188598633,
                    -124.50009155273438
                ],
                "Up": [
                    1.2358036656223703e-06,
                    1.0,
                    6.258499070099788e-07
                ],
                "At": [
                    1.0,
                    -1.235804234056559e-06,
                    9.099621820496395e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -31.9991455078125,
                    4.000490188598633,
                    -124.5001220703125
                ],
                "Up": [
                    1.3550127277994761e-06,
                    0.9999999403953552,
                    6.854550633761392e-07
                ],
                "At": [
                    1.0,
                    -1.3550135236073402e-06,
                    1.029171357913583e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -39.99913024902344,
                    4.000490188598633,
                    -124.50013732910156
                ],
                "Up": [
                    1.4742219036634197e-06,
                    0.9999999403953552,
                    7.450598786817864e-07
                ],
                "At": [
                    1.0,
                    -1.4742229268449591e-06,
                    1.0291711305399076e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -47.99913024902344,
                    4.000490188598633,
                    -124.50013732910156
                ],
                "Up": [
                    1.5934313069010386e-06,
                    1.0,
                    8.046643529269204e-07
                ],
                "At": [
                    1.0,
                    -1.5934321027089027e-06,
                    1.0291710168530699e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -55.99909210205078,
                    4.000490188598633,
                    -124.50015258789062
                ],
                "Up": [
                    1.7126403690781444e-06,
                    0.9999999403953552,
                    8.344674142790609e-07
                ],
                "At": [
                    1.0,
                    -1.7126415059465216e-06,
                    1.1483800790301757e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -63.999061584472656,
                    4.000459671020508,
                    -124.50015258789062
                ],
                "Up": [
                    1.831849544942088e-06,
                    0.9999999403953552,
                    8.642696229799185e-07
                ],
                "At": [
                    1.0,
                    -1.831850795497303e-06,
                    1.148379965343338e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -71.9990463256836,
                    4.000459671020508,
                    -124.50015258789062
                ],
                "Up": [
                    1.951058948179707e-06,
                    1.0,
                    9.23874324598728e-07
                ],
                "At": [
                    1.0,
                    -1.951060085048084e-06,
                    1.1483797379696625e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -71.99900817871094,
                    4.000432968139648,
                    -116.50018310546875
                ],
                "Up": [
                    1.9371511825738708e-06,
                    0.9999999403953552,
                    9.854633162831306e-07
                ],
                "At": [
                    1.3430907301881234e-06,
                    9.854609288595384e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -71.99897766113281,
                    4.000375747680664,
                    -108.50021362304688
                ],
                "Up": [
                    2.056360472124652e-06,
                    0.9999999403953552,
                    9.85463543656806e-07
                ],
                "At": [
                    1.3430908438749611e-06,
                    9.854609288595384e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -71.99893188476562,
                    4.000349044799805,
                    -100.50022888183594
                ],
                "Up": [
                    2.145767894035089e-06,
                    0.9999998807907104,
                    9.854636573436437e-07
                ],
                "At": [
                    1.3430909575617989e-06,
                    9.854609288595384e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -71.9988784790039,
                    4.000322341918945,
                    -92.50022888183594
                ],
                "Up": [
                    2.2351748611981748e-06,
                    0.9999998807907104,
                    9.854637710304814e-07
                ],
                "At": [
                    1.3430909575617989e-06,
                    9.854609288595384e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -71.99884796142578,
                    4.000326156616211,
                    -84.50025939941406
                ],
                "Up": [
                    2.3543839233752806e-06,
                    0.9999999403953552,
                    9.854638847173192e-07
                ],
                "At": [
                    1.3430910712486366e-06,
                    9.854609288595384e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -71.99879455566406,
                    4.000268936157227,
                    -76.50025939941406
                ],
                "Up": [
                    2.3841855636419496e-06,
                    1.0,
                    9.854646805251832e-07
                ],
                "At": [
                    1.5815097640370368e-06,
                    9.854609288595384e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -71.99877166748047,
                    4.000242233276367,
                    -68.500244140625
                ],
                "Up": [
                    2.47359230343136e-06,
                    0.9999998807907104,
                    9.854646805251832e-07
                ],
                "At": [
                    1.5815097640370368e-06,
                    9.854609288595384e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -71.99872589111328,
                    4.000213623046875,
                    -60.500274658203125
                ],
                "Up": [
                    2.622604142743512e-06,
                    1.0,
                    9.854650215856964e-07
                ],
                "At": [
                    1.5815099914107122e-06,
                    9.854609288595384e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -71.99859619140625,
                    4.000126838684082,
                    -44.50038146972656
                ],
                "Up": [
                    2.8173133159725694e-06,
                    1.0000011920928955,
                    9.536738616588991e-07
                ],
                "At": [
                    -1.0,
                    2.817311496983166e-06,
                    -1.7126387774624163e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -71.99874877929688,
                    4.000201225280762,
                    -52.50025939941406
                ],
                "Up": [
                    2.5788945094973315e-06,
                    1.0000011920928955,
                    9.238716529580415e-07
                ],
                "At": [
                    -1.0,
                    2.5788929178816034e-06,
                    -1.5934298289721482e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -71.99861145019531,
                    4.000104904174805,
                    -36.500335693359375
                ],
                "Up": [
                    2.8312203994573792e-06,
                    1.0,
                    1.1046753343180171e-06
                ],
                "At": [
                    1.8199291389464634e-06,
                    1.1046702184103196e-06,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -71.99968719482422,
                    4.0005035400390625,
                    -28.499786376953125
                ],
                "Up": [
                    2.9802343703977385e-08,
                    0.9999999403953552,
                    -2.0663203770254768e-07
                ],
                "At": [
                    3.8941439584050386e-07,
                    -2.0663208033511182e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -7.9998321533203125,
                    11.999797821044922,
                    -36.5
                ],
                "Up": [
                    1.4901178246873314e-07,
                    1.0000009536743164,
                    -7.152563057388761e-07
                ],
                "At": [
                    -6.379552814905765e-07,
                    7.152557373046875e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    40.00032043457031,
                    3.999979019165039,
                    -44.500030517578125
                ],
                "Up": [
                    4.3712379493854314e-08,
                    1.0000009536743164,
                    -7.897619411778578e-07
                ],
                "At": [
                    1.0,
                    -4.371133144331907e-08,
                    1.2675908465098473e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -7.999855041503906,
                    12.000099182128906,
                    -44.5
                ],
                "Up": [
                    5.960463766996327e-08,
                    1.0000009536743164,
                    -5.960470161880949e-07
                ],
                "At": [
                    -8.47502619194529e-08,
                    5.960464477539062e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -7.999855041503906,
                    12.000099182128906,
                    -52.5
                ],
                "Up": [
                    5.9604641222676946e-08,
                    1.0000009536743164,
                    -5.960470161880949e-07
                ],
                "At": [
                    -8.102497162099098e-08,
                    5.960464477539062e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    24.000213623046875,
                    4.0004119873046875,
                    -28.4998779296875
                ],
                "Up": [
                    7.549810021600933e-08,
                    1.0000011920928955,
                    -4.3609239241959585e-07
                ],
                "At": [
                    -1.0,
                    7.54978870531886e-08,
                    -2.821300029154372e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    40.00035095214844,
                    4.000280380249023,
                    -52.4998779296875
                ],
                "Up": [
                    1.6292138127482758e-07,
                    1.0000011920928955,
                    -5.364423714127042e-07
                ],
                "At": [
                    1.0,
                    -1.629206423103824e-07,
                    1.0291722674082848e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    48.000396728515625,
                    4.000532150268555,
                    -36.499908447265625
                ],
                "Up": [
                    1.9470734002879908e-07,
                    1.0000009536743164,
                    -4.323669884342962e-07
                ],
                "At": [
                    -1.0,
                    1.9470718370939721e-07,
                    7.549781599891503e-08
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    56.00041198730469,
                    4.000593185424805,
                    -36.49993896484375
                ],
                "Up": [
                    1.9470734002879908e-07,
                    1.0000009536743164,
                    -4.349281255144888e-07
                ],
                "At": [
                    -1.0,
                    1.9470718370939721e-07,
                    7.549781599891503e-08
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    64.00042724609375,
                    4.000593185424805,
                    -36.499969482421875
                ],
                "Up": [
                    1.9470734002879908e-07,
                    1.0000009536743164,
                    -4.349281255144888e-07
                ],
                "At": [
                    -1.0,
                    1.9470718370939721e-07,
                    7.549781599891503e-08
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    16.0001220703125,
                    20.00011444091797,
                    -20.49994659423828
                ],
                "Up": [
                    4.371153039528508e-08,
                    1.0000009536743164,
                    -5.406332093116362e-07
                ],
                "At": [
                    1.0,
                    -4.371138118131057e-08,
                    1.9470721213110664e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    8.000106811523438,
                    4.000234603881836,
                    -20.4998779296875
                ],
                "Up": [
                    4.371141315573368e-08,
                    1.0000009536743164,
                    -5.029146450397093e-07
                ],
                "At": [
                    1.0,
                    -4.371139183945161e-08,
                    -4.3711366970455856e-08
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    0.0001678466796875,
                    4.000116348266602,
                    -12.49993896484375
                ],
                "Up": [
                    7.549804337259047e-08,
                    1.0000009536743164,
                    -4.752077984448988e-07
                ],
                "At": [
                    -1.0,
                    7.549789415861596e-08,
                    -1.6292071336465597e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    8.000137329101562,
                    20.00005340576172,
                    -20.49994659423828
                ],
                "Up": [
                    4.37115268425714e-08,
                    1.0000009536743164,
                    -5.345796125766356e-07
                ],
                "At": [
                    1.0,
                    -4.371138118131057e-08,
                    1.9470721213110664e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    0.0001678466796875,
                    19.99999237060547,
                    -20.50000762939453
                ],
                "Up": [
                    4.37115268425714e-08,
                    1.0000009536743164,
                    -5.345796125766356e-07
                ],
                "At": [
                    1.0,
                    -4.371138118131057e-08,
                    1.9470721213110664e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -63.99859619140625,
                    4.000043869018555,
                    -36.50030517578125
                ],
                "Up": [
                    2.8173124064778676e-06,
                    1.0000009536743164,
                    1.0393606544312206e-06
                ],
                "At": [
                    -1.0,
                    2.817311496983166e-06,
                    -1.8318478396395221e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -55.99989318847656,
                    4.000165939331055,
                    -36.499847412109375
                ],
                "Up": [
                    1.947076384567481e-07,
                    1.0000011920928955,
                    -4.6752444404773996e-07
                ],
                "At": [
                    -1.0,
                    1.9470715528768778e-07,
                    -5.205486104387091e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -7.99981689453125,
                    19.99993133544922,
                    -20.50000762939453
                ],
                "Up": [
                    4.37115268425714e-08,
                    1.0000009536743164,
                    -5.345796125766356e-07
                ],
                "At": [
                    1.0,
                    -4.371138118131057e-08,
                    1.9470721213110664e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -7.999809265136719,
                    19.999862670898438,
                    -28.50000762939453
                ],
                "Up": [
                    5.960462345910855e-08,
                    1.0000009536743164,
                    -4.768376129504759e-07
                ],
                "At": [
                    -3.697346926401224e-07,
                    4.76837158203125e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_DOOR_A",
                "UserData": 51,
                "Position": [
                    -11.999786376953125,
                    4.000173568725586,
                    -20.499755859375
                ],
                "Up": [
                    7.5498491014514e-08,
                    1.0000009536743164,
                    -5.066399353381712e-07
                ],
                "At": [
                    -1.0,
                    7.549785152605182e-08,
                    -1.1165950581926154e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    40.000244140625,
                    4.000356674194336,
                    -20.499786376953125
                ],
                "Up": [
                    4.3711430919302074e-08,
                    1.0000011920928955,
                    -3.5762843708653236e-07
                ],
                "At": [
                    1.0,
                    -4.371139183945161e-08,
                    -4.3711374075883214e-08
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -7.9998016357421875,
                    19.999801635742188,
                    -36.49993896484375
                ],
                "Up": [
                    8.940695295223122e-08,
                    1.0000009536743164,
                    -4.768376129504759e-07
                ],
                "At": [
                    -3.697346926401224e-07,
                    4.76837158203125e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -7.999786376953125,
                    19.999671936035156,
                    -44.49993896484375
                ],
                "Up": [
                    1.1920928244535389e-07,
                    1.0000009536743164,
                    -4.768376129504759e-07
                ],
                "At": [
                    -3.604213816288393e-07,
                    4.76837158203125e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -7.999763488769531,
                    19.999610900878906,
                    -52.5
                ],
                "Up": [
                    1.4901159772762185e-07,
                    1.0000009536743164,
                    -4.76837556107057e-07
                ],
                "At": [
                    -3.6414670034901064e-07,
                    4.76837158203125e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    0.0002593994140625,
                    19.999610900878906,
                    -52.500030517578125
                ],
                "Up": [
                    1.9470759582418395e-07,
                    1.0000009536743164,
                    -4.7311220896517625e-07
                ],
                "At": [
                    -1.0,
                    1.9470715528768778e-07,
                    -5.205486104387091e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    8.000221252441406,
                    19.999549865722656,
                    -52.49993896484375
                ],
                "Up": [
                    7.549824232455649e-08,
                    1.0000009536743164,
                    -5.692713216376433e-07
                ],
                "At": [
                    -1.0,
                    7.549787994776125e-08,
                    -5.205486104387091e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    16.000228881835938,
                    19.999549865722656,
                    -52.4998779296875
                ],
                "Up": [
                    7.54982565354112e-08,
                    1.0000009536743164,
                    -5.937185960647184e-07
                ],
                "At": [
                    -1.0,
                    7.549787994776125e-08,
                    -5.205486104387091e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    24.000244140625,
                    19.999610900878906,
                    -52.4998779296875
                ],
                "Up": [
                    7.549827785169327e-08,
                    1.0000009536743164,
                    -6.312043296929915e-07
                ],
                "At": [
                    -1.0,
                    7.549787994776125e-08,
                    -5.205486104387091e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    24.000244140625,
                    19.999610900878906,
                    -44.4998779296875
                ],
                "Up": [
                    1.6292126758798986e-07,
                    1.0000009536743164,
                    -6.821941269663512e-07
                ],
                "At": [
                    1.0,
                    -1.629206565212371e-07,
                    6.715444555993599e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    24.000259399414062,
                    19.999618530273438,
                    -36.49993896484375
                ],
                "Up": [
                    1.6292125337713514e-07,
                    1.0000009536743164,
                    -6.607737077501952e-07
                ],
                "At": [
                    1.0,
                    -1.629206565212371e-07,
                    6.715444555993599e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    24.000259399414062,
                    19.999557495117188,
                    -28.49994659423828
                ],
                "Up": [
                    4.371185724494353e-08,
                    1.000001072883606,
                    -6.717168048453459e-07
                ],
                "At": [
                    1.0,
                    -4.37113598650285e-08,
                    6.715443987559411e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    24.0001220703125,
                    20.00011444091797,
                    -20.49988555908203
                ],
                "Up": [
                    4.371165829297752e-08,
                    1.0000009536743164,
                    -5.669430720445234e-07
                ],
                "At": [
                    1.0,
                    -4.3711370523169535e-08,
                    4.3312579123266914e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_NPCSCI",
                "UserData": 51,
                "Position": [
                    -15.999786376953125,
                    4.000173568725586,
                    -20.499755859375
                ],
                "Up": [
                    1.6292116811200685e-07,
                    1.0000011920928955,
                    -4.768376697938947e-07
                ],
                "At": [
                    1.0,
                    -1.629206565212371e-07,
                    6.715443987559411e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -15.999748229980469,
                    3.9996891021728516,
                    -12.49993896484375
                ],
                "Up": [
                    -7.549778047177824e-08,
                    1.0000009536743164,
                    -6.407503292393812e-07
                ],
                "At": [
                    1.0,
                    7.549791547489804e-08,
                    3.1391644483846903e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -7.9997711181640625,
                    4.000177383422852,
                    -12.49981689453125
                ],
                "Up": [
                    1.629211254794427e-07,
                    1.0000009536743164,
                    -4.780016524819075e-07
                ],
                "At": [
                    1.0,
                    -1.629206565212371e-07,
                    6.715443987559411e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_STORE4",
                "UserData": 51,
                "Position": [
                    -15.999588012695312,
                    3.9999866485595703,
                    -28.499908447265625
                ],
                "Up": [
                    1.6292128179884457e-07,
                    1.0000011920928955,
                    -3.967438431118353e-07
                ],
                "At": [
                    1.0,
                    -1.6292062809952768e-07,
                    1.148381556959066e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_STORE5",
                "UserData": 51,
                "Position": [
                    -15.999649047851562,
                    4.000104904174805,
                    -36.49993896484375
                ],
                "Up": [
                    2.82130713458173e-07,
                    1.0000011920928955,
                    -3.632160598954215e-07
                ],
                "At": [
                    1.0,
                    -2.821299176503089e-07,
                    1.2675908465098473e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1718944885,
                "ObjectID": "^S_MACHINE0",
                "UserData": 0,
                "Position": [
                    -11.651580810546875,
                    3.458493232727051,
                    -6.633146286010742
                ],
                "Up": [
                    4.989399116084314e-09,
                    0.6776381731033325,
                    -3.0154978958307765e-07
                ],
                "At": [
                    0.027833834290504456,
                    -4.4503374851956323e-07,
                    -0.99961256980896
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    40.000091552734375,
                    3.9999942779541016,
                    -12.49993896484375
                ],
                "Up": [
                    4.3711665398404875e-08,
                    1.0000009536743164,
                    -5.811456844639906e-07
                ],
                "At": [
                    1.0,
                    -4.3711370523169535e-08,
                    4.3312579123266914e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_STORE6",
                "UserData": 51,
                "Position": [
                    -15.999588012695312,
                    4.000101089477539,
                    -44.499969482421875
                ],
                "Up": [
                    1.6292115390115214e-07,
                    1.0000011920928955,
                    -3.837053270672186e-07
                ],
                "At": [
                    1.0,
                    -1.629206565212371e-07,
                    7.907536883067223e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -15.999534606933594,
                    4.000036239624023,
                    -52.49993896484375
                ],
                "Up": [
                    1.62921210744571e-07,
                    1.0000009536743164,
                    -4.142061982292944e-07
                ],
                "At": [
                    1.0,
                    -1.629206423103824e-07,
                    1.0291722674082848e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -15.99951171875,
                    4.000030517578125,
                    -60.49993896484375
                ],
                "Up": [
                    1.6292125337713514e-07,
                    1.0000009536743164,
                    -4.1094634184446477e-07
                ],
                "At": [
                    1.0,
                    -1.6292062809952768e-07,
                    1.148381556959066e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -7.999504089355469,
                    4.000091552734375,
                    -60.49993896484375
                ],
                "Up": [
                    5.9604559510262334e-08,
                    1.0000009536743164,
                    -3.576281812911475e-07
                ],
                "At": [
                    -7.031478048702411e-07,
                    3.5762786865234375e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    56.0003662109375,
                    4.0005340576171875,
                    -28.499908447265625
                ],
                "Up": [
                    1.947074395047821e-07,
                    1.0000009536743164,
                    -4.468024314974173e-07
                ],
                "At": [
                    -1.0,
                    1.947071694985425e-07,
                    -1.6292077020807483e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    64.00041198730469,
                    4.0005340576171875,
                    -28.499969482421875
                ],
                "Up": [
                    1.947074395047821e-07,
                    1.0000009536743164,
                    -4.468024314974173e-07
                ],
                "At": [
                    -1.0,
                    1.947071694985425e-07,
                    -1.6292077020807483e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_STORE7",
                "UserData": 51,
                "Position": [
                    0.0004730224609375,
                    4.000091552734375,
                    -60.499969482421875
                ],
                "Up": [
                    1.1548393530347312e-07,
                    1.0000011920928955,
                    -3.576282097128569e-07
                ],
                "At": [
                    -7.152548846534046e-07,
                    3.5762786865234375e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_STORE8",
                "UserData": 51,
                "Position": [
                    8.000442504882812,
                    4.000091552734375,
                    -60.49993896484375
                ],
                "Up": [
                    2.1979205655497935e-07,
                    1.0000011920928955,
                    -3.576281244477286e-07
                ],
                "At": [
                    -7.45057150197681e-07,
                    3.5762786865234375e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_STORE9",
                "UserData": 51,
                "Position": [
                    16.000396728515625,
                    4.000091552734375,
                    -60.500091552734375
                ],
                "Up": [
                    2.1234149016891024e-07,
                    1.0000011920928955,
                    -3.576280960260192e-07
                ],
                "At": [
                    -9.238708571501775e-07,
                    3.5762786865234375e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    8.000350952148438,
                    4.0003509521484375,
                    -28.499847412109375
                ],
                "Up": [
                    1.947076384567481e-07,
                    1.0000011920928955,
                    -3.364408200923208e-07
                ],
                "At": [
                    -1.0,
                    1.9470715528768778e-07,
                    -7.589671895402716e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    24.000167846679688,
                    3.999788284301758,
                    -60.4998779296875
                ],
                "Up": [
                    1.1920937481590954e-07,
                    1.0000009536743164,
                    -5.960469025012571e-07
                ],
                "At": [
                    -1.0868523077078862e-06,
                    5.960464477539062e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    32.00016784667969,
                    3.999788284301758,
                    -60.49981689453125
                ],
                "Up": [
                    1.4901176825787843e-07,
                    1.0000009536743164,
                    -5.960468456578383e-07
                ],
                "At": [
                    -1.3094380619804724e-06,
                    5.960464477539062e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^CUBEROOM_SPACE",
                "UserData": 0,
                "Position": [
                    32.0003662109375,
                    4.000280380249023,
                    -52.49986267089844
                ],
                "Up": [
                    1.4901169720360485e-07,
                    1.0000009536743164,
                    -5.642603468913876e-07
                ],
                "At": [
                    1.1046699910366442e-06,
                    -5.642600058308744e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_TECH",
                "UserData": 51,
                "Position": [
                    32.000335693359375,
                    3.999979019165039,
                    -44.50006103515625
                ],
                "Up": [
                    7.54989102347281e-08,
                    1.0000011920928955,
                    -7.841741762604215e-07
                ],
                "At": [
                    -1.0,
                    7.549784442062446e-08,
                    -1.2358043477433966e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_NPCBUI",
                "UserData": 51,
                "Position": [
                    32.00030517578125,
                    3.9998598098754883,
                    -36.5001220703125
                ],
                "Up": [
                    5.58798589622711e-08,
                    1.0000011920928955,
                    -8.344659931935894e-07
                ],
                "At": [
                    -1.4007076742927893e-06,
                    8.344650268554688e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_TECH",
                "UserData": 51,
                "Position": [
                    32.000274658203125,
                    3.9997425079345703,
                    -28.50018310546875
                ],
                "Up": [
                    -4.371004891368102e-08,
                    1.0000011920928955,
                    -9.18284797535307e-07
                ],
                "At": [
                    -1.0,
                    -4.3711459341011505e-08,
                    -1.5934321027089027e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^TOXICPLANT",
                "UserData": 61847529062400,
                "Position": [
                    8.000091552734375,
                    3.802365303039551,
                    -5.499940872192383
                ],
                "Up": [
                    1.862644971595273e-08,
                    1.0000009536743164,
                    -4.768376129504759e-07
                ],
                "At": [
                    2.682206172721635e-07,
                    4.76837158203125e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    16.00011444091797,
                    4.000177383422852,
                    -12.4998779296875
                ],
                "Up": [
                    -1.509958593715055e-07,
                    1.0000009536743164,
                    -5.960470161880949e-07
                ],
                "At": [
                    1.5099588779321493e-07,
                    -5.960464477539062e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    24.000106811523438,
                    4.000177383422852,
                    -12.49993896484375
                ],
                "Up": [
                    7.549799363459897e-08,
                    1.0000009536743164,
                    -5.348124432202894e-07
                ],
                "At": [
                    -1.0,
                    7.549790126404332e-08,
                    -4.3711430919302074e-08
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    72.00044250488281,
                    4.000654220581055,
                    -36.5
                ],
                "Up": [
                    1.9470734002879908e-07,
                    1.0000009536743164,
                    -4.349281255144888e-07
                ],
                "At": [
                    -1.0,
                    1.9470718370939721e-07,
                    7.549781599891503e-08
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    32.00010681152344,
                    3.9999942779541016,
                    -12.499969482421875
                ],
                "Up": [
                    4.3711548158853475e-08,
                    1.0000011920928955,
                    -5.83008556986897e-07
                ],
                "At": [
                    1.0,
                    -4.371138118131057e-08,
                    1.9470721213110664e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -7.9998016357421875,
                    11.999870300292969,
                    -12.500007629394531
                ],
                "Up": [
                    4.37115268425714e-08,
                    1.0000009536743164,
                    -5.352781045075972e-07
                ],
                "At": [
                    1.0,
                    -4.371138118131057e-08,
                    1.9470721213110664e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -15.999763488769531,
                    11.999748229980469,
                    -12.499946594238281
                ],
                "Up": [
                    -7.54977875772056e-08,
                    1.0000009536743164,
                    -6.346967893477995e-07
                ],
                "At": [
                    1.0,
                    7.549791547489804e-08,
                    3.1391644483846903e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -15.999824523925781,
                    11.999866485595703,
                    -20.5
                ],
                "Up": [
                    1.6292095494918613e-07,
                    1.0000009536743164,
                    -6.523919182654936e-07
                ],
                "At": [
                    1.0,
                    -1.6292067073209182e-07,
                    1.9470729739623494e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_COOK",
                "UserData": 51,
                "Position": [
                    0.0001220703125,
                    11.999870300292969,
                    -12.500068664550781
                ],
                "Up": [
                    1.9470759582418395e-07,
                    1.0000011920928955,
                    -6.70552879000752e-07
                ],
                "At": [
                    -1.0,
                    1.947071694985425e-07,
                    -2.821300881805655e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_COOK",
                "UserData": 51,
                "Position": [
                    8.0001220703125,
                    11.999992370605469,
                    -12.500068664550781
                ],
                "Up": [
                    1.9470759582418395e-07,
                    1.0000011920928955,
                    -6.70552879000752e-07
                ],
                "At": [
                    -1.0,
                    1.947071694985425e-07,
                    -2.821300881805655e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_COOK",
                "UserData": 51,
                "Position": [
                    16.0001220703125,
                    11.999992370605469,
                    -12.500068664550781
                ],
                "Up": [
                    1.9470758161332924e-07,
                    1.0000011920928955,
                    -6.370252094711759e-07
                ],
                "At": [
                    -1.0,
                    1.947071694985425e-07,
                    -2.821300881805655e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    32.0001220703125,
                    12.000171661376953,
                    -20.49993896484375
                ],
                "Up": [
                    1.509959588474885e-07,
                    1.0000009536743164,
                    -5.960470161880949e-07
                ],
                "At": [
                    2.1420362372737145e-08,
                    -5.960464477539062e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    32.000152587890625,
                    11.999931335449219,
                    -12.499946594238281
                ],
                "Up": [
                    1.5099602990176209e-07,
                    1.0000009536743164,
                    -5.960470161880949e-07
                ],
                "At": [
                    1.5099570305210364e-07,
                    -5.960464477539062e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    24.000137329101562,
                    12.000114440917969,
                    -12.500007629394531
                ],
                "Up": [
                    1.5099597305834322e-07,
                    1.0000009536743164,
                    -5.960470161880949e-07
                ],
                "At": [
                    5.4016616957142105e-08,
                    -5.960464477539062e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_PLANT0",
                "UserData": 51,
                "Position": [
                    32.0001220703125,
                    12.000110626220703,
                    -28.49993896484375
                ],
                "Up": [
                    1.5099607253432623e-07,
                    1.0000011920928955,
                    -5.960471867183514e-07
                ],
                "At": [
                    1.490113561430917e-07,
                    -5.960464477539062e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_PLANT0",
                "UserData": 51,
                "Position": [
                    32.00010681152344,
                    11.999858856201172,
                    -36.49993896484375
                ],
                "Up": [
                    7.549826364083856e-08,
                    1.0000011920928955,
                    -5.718326292480924e-07
                ],
                "At": [
                    -1.0,
                    7.549787994776125e-08,
                    -5.205486104387091e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_PLANT0",
                "UserData": 51,
                "Position": [
                    32.0001220703125,
                    11.999977111816406,
                    -44.49993896484375
                ],
                "Up": [
                    7.549814284857348e-08,
                    1.0000011920928955,
                    -5.811459118376661e-07
                ],
                "At": [
                    -1.0,
                    7.54978870531886e-08,
                    -2.821300029154372e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    32.00013732910156,
                    12.000038146972656,
                    -52.4998779296875
                ],
                "Up": [
                    1.5099615779945452e-07,
                    1.0000009536743164,
                    -5.96046959344676e-07
                ],
                "At": [
                    3.8941431057537557e-07,
                    -5.960464477539062e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    32.00016784667969,
                    11.999847412109375,
                    -60.4998779296875
                ],
                "Up": [
                    1.4901169720360485e-07,
                    1.0000011920928955,
                    -5.642604605782253e-07
                ],
                "At": [
                    1.1046699910366442e-06,
                    -5.642599489874556e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    24.000167846679688,
                    11.999855041503906,
                    -52.49993896484375
                ],
                "Up": [
                    1.49011739836169e-07,
                    1.0000009536743164,
                    -5.960468456578383e-07
                ],
                "At": [
                    -1.2582154340634588e-06,
                    5.960464477539062e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_PLANT1",
                "UserData": 51,
                "Position": [
                    16.0001220703125,
                    12.000091552734375,
                    -60.499969482421875
                ],
                "Up": [
                    7.549801495088104e-08,
                    1.0000011920928955,
                    -5.885964924345899e-07
                ],
                "At": [
                    -1.0,
                    7.549790126404332e-08,
                    -4.371143447201575e-08
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_PLANT1",
                "UserData": 51,
                "Position": [
                    8.00018310546875,
                    12.000091552734375,
                    -60.499969482421875
                ],
                "Up": [
                    -4.3711281705327565e-08,
                    1.0000011920928955,
                    -6.109482910687802e-07
                ],
                "At": [
                    -1.0,
                    -4.3711398944878965e-08,
                    -2.8212994607201836e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_PLANT1",
                "UserData": 51,
                "Position": [
                    0.00018310546875,
                    12.000091552734375,
                    -60.499969482421875
                ],
                "Up": [
                    4.371165829297752e-08,
                    1.0000011920928955,
                    -5.438930088530469e-07
                ],
                "At": [
                    1.0,
                    -4.3711370523169535e-08,
                    4.3312579123266914e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -15.999839782714844,
                    12.000038146972656,
                    -52.5
                ],
                "Up": [
                    4.371154105342612e-08,
                    1.0000009536743164,
                    -5.941842573520262e-07
                ],
                "At": [
                    1.0,
                    -4.371138118131057e-08,
                    1.9470721213110664e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -7.999839782714844,
                    12.000030517578125,
                    -60.5
                ],
                "Up": [
                    4.371154105342612e-08,
                    1.0000009536743164,
                    -5.941842573520262e-07
                ],
                "At": [
                    1.0,
                    -4.371138118131057e-08,
                    1.9470721213110664e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -15.999748229980469,
                    11.999420166015625,
                    -60.50006103515625
                ],
                "Up": [
                    1.6292105442516913e-07,
                    1.0000009536743164,
                    -5.632177817460615e-07
                ],
                "At": [
                    1.0,
                    -1.6292067073209182e-07,
                    4.33125848076088e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_BIO",
                "UserData": 51,
                "Position": [
                    -15.999847412109375,
                    12.000099182128906,
                    -44.5
                ],
                "Up": [
                    1.0430814256778831e-07,
                    1.0000011920928955,
                    -5.960471867183514e-07
                ],
                "At": [
                    -1.1920917586394353e-07,
                    5.960464477539062e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_BIO",
                "UserData": 51,
                "Position": [
                    -15.999801635742188,
                    11.999736785888672,
                    -36.5
                ],
                "Up": [
                    1.5099639938398468e-07,
                    1.0000011920928955,
                    -7.152564762691327e-07
                ],
                "At": [
                    6.278329465203569e-07,
                    -7.152557373046875e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^CUBEROOM_SPACE",
                "UserData": 0,
                "Position": [
                    8.0001220703125,
                    20.00006103515625,
                    -12.499935150146484
                ],
                "Up": [
                    4.37115268425714e-08,
                    1.0000009536743164,
                    -5.215410396886e-07
                ],
                "At": [
                    1.0,
                    -4.371138118131057e-08,
                    1.9470721213110664e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^CUBEROOM_SPACE",
                "UserData": 0,
                "Position": [
                    16.00018310546875,
                    19.999969482421875,
                    -12.499935150146484
                ],
                "Up": [
                    1.5099602990176209e-07,
                    1.0000009536743164,
                    -5.960470161880949e-07
                ],
                "At": [
                    1.5099571726295835e-07,
                    -5.960464477539062e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    24.000137329101562,
                    20.00006103515625,
                    -12.500011444091797
                ],
                "Up": [
                    1.5099602990176209e-07,
                    1.0000009536743164,
                    -5.960470161880949e-07
                ],
                "At": [
                    1.5099570305210364e-07,
                    -5.960464477539062e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    32.0001220703125,
                    20.0,
                    -12.499950408935547
                ],
                "Up": [
                    1.5099602990176209e-07,
                    1.0000009536743164,
                    -5.960470161880949e-07
                ],
                "At": [
                    1.5099570305210364e-07,
                    -5.960464477539062e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^CUBEROOM_SPACE",
                "UserData": 0,
                "Position": [
                    32.000213623046875,
                    20.00005340576172,
                    -20.49987030029297
                ],
                "Up": [
                    7.549819258656498e-08,
                    1.0000009536743164,
                    -5.960468456578383e-07
                ],
                "At": [
                    -1.0,
                    7.54978870531886e-08,
                    -4.0133929246621847e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^CUBEROOM_SPACE",
                "UserData": 0,
                "Position": [
                    32.000274658203125,
                    19.999526977539062,
                    -28.49993133544922
                ],
                "Up": [
                    1.5099635675142054e-07,
                    1.0000009536743164,
                    -7.152563057388761e-07
                ],
                "At": [
                    6.278329465203569e-07,
                    -7.152557373046875e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^CUBEROOM_SPACE",
                "UserData": 0,
                "Position": [
                    32.00030517578125,
                    19.999588012695312,
                    -36.49992370605469
                ],
                "Up": [
                    7.549840574938571e-08,
                    1.0000009536743164,
                    -6.183986442920286e-07
                ],
                "At": [
                    -1.0,
                    7.549786573690653e-08,
                    -7.589671895402716e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    32.000244140625,
                    19.999610900878906,
                    -52.4998779296875
                ],
                "Up": [
                    7.549836311682157e-08,
                    1.0000009536743164,
                    -6.584454581570753e-07
                ],
                "At": [
                    -1.0,
                    7.549787284233389e-08,
                    -6.397578999894904e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^CUBEROOM_SPACE",
                "UserData": 0,
                "Position": [
                    32.000244140625,
                    19.999549865722656,
                    -44.49986267089844
                ],
                "Up": [
                    7.549845548737721e-08,
                    1.0000009536743164,
                    -6.780032890674192e-07
                ],
                "At": [
                    -1.0,
                    7.549786573690653e-08,
                    -7.589671895402716e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    32.00025939941406,
                    19.999549865722656,
                    -60.49981689453125
                ],
                "Up": [
                    7.549829206254799e-08,
                    1.0000009536743164,
                    -6.635677323174605e-07
                ],
                "At": [
                    -1.0,
                    7.549787994776125e-08,
                    -5.205486104387091e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -7.9997711181640625,
                    19.999610900878906,
                    -60.5
                ],
                "Up": [
                    1.7881390590446244e-07,
                    1.0000009536743164,
                    -4.76837556107057e-07
                ],
                "At": [
                    -3.6507805134533555e-07,
                    4.76837158203125e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_DOOR_A",
                "UserData": 51,
                "Position": [
                    48.00018310546875,
                    4.000030517578125,
                    -64.4998779296875
                ],
                "Up": [
                    2.384186927884002e-07,
                    1.0000009536743164,
                    -5.960466182841628e-07
                ],
                "At": [
                    -1.6167743979167426e-06,
                    5.960464477539062e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -23.999725341796875,
                    19.999656677246094,
                    -68.50009155273438
                ],
                "Up": [
                    2.821304576627881e-07,
                    1.0000009536743164,
                    -4.805627895621001e-07
                ],
                "At": [
                    1.0,
                    -2.8212994607201836e-07,
                    5.523351660485787e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    0.0001983642578125,
                    19.999610900878906,
                    -60.5
                ],
                "Up": [
                    1.9470758161332924e-07,
                    1.0000009536743164,
                    -4.39584596279019e-07
                ],
                "At": [
                    -1.0,
                    1.9470715528768778e-07,
                    -5.205486104387091e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    8.000244140625,
                    19.999549865722656,
                    -60.499969482421875
                ],
                "Up": [
                    1.9470762424589338e-07,
                    1.0000009536743164,
                    -5.196783376959502e-07
                ],
                "At": [
                    -1.0,
                    1.9470715528768778e-07,
                    -5.20548667282128e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -15.999755859375,
                    19.999488830566406,
                    -60.50006103515625
                ],
                "Up": [
                    1.6292104021431442e-07,
                    1.0000009536743164,
                    -5.261976525616774e-07
                ],
                "At": [
                    1.0,
                    -1.6292067073209182e-07,
                    4.33125848076088e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^CUBEROOM_SPACE",
                "UserData": 0,
                "Position": [
                    -15.99981689453125,
                    19.999671936035156,
                    -44.49992370605469
                ],
                "Up": [
                    1.629210260034597e-07,
                    1.0000009536743164,
                    -4.6938703235355206e-07
                ],
                "At": [
                    1.0,
                    -1.6292067073209182e-07,
                    4.33125848076088e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^CUBEROOM_SPACE",
                "UserData": 0,
                "Position": [
                    -15.99981689453125,
                    19.999801635742188,
                    -36.49993896484375
                ],
                "Up": [
                    4.3711576580562905e-08,
                    1.0000009536743164,
                    -5.066399921815901e-07
                ],
                "At": [
                    1.0,
                    -4.3711374075883214e-08,
                    3.139165016818879e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -15.999748229980469,
                    19.999549865722656,
                    -52.5
                ],
                "Up": [
                    1.629210260034597e-07,
                    1.0000009536743164,
                    -4.933685318064818e-07
                ],
                "At": [
                    1.0,
                    -1.6292067073209182e-07,
                    4.33125848076088e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^CUBEROOM_SPACE",
                "UserData": 0,
                "Position": [
                    -15.99981689453125,
                    19.99993133544922,
                    -20.49999237060547
                ],
                "Up": [
                    4.37115268425714e-08,
                    1.0000009536743164,
                    -5.215410396886e-07
                ],
                "At": [
                    1.0,
                    -4.371138118131057e-08,
                    1.9470721213110664e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^CUBEROOM_SPACE",
                "UserData": 0,
                "Position": [
                    -15.99981689453125,
                    19.999862670898438,
                    -28.49999237060547
                ],
                "Up": [
                    1.5099615779945452e-07,
                    1.0000009536743164,
                    -5.96046959344676e-07
                ],
                "At": [
                    3.8941431057537557e-07,
                    -5.960464477539062e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -15.999763488769531,
                    19.999755859375,
                    -12.500011444091797
                ],
                "Up": [
                    4.371167250383223e-08,
                    1.0000009536743164,
                    -5.965125637885649e-07
                ],
                "At": [
                    1.0,
                    -4.3711370523169535e-08,
                    4.3312579123266914e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^CUBEROOM_SPACE",
                "UserData": 0,
                "Position": [
                    0.000152587890625,
                    20.0,
                    -12.500011444091797
                ],
                "Up": [
                    -4.371129946889596e-08,
                    1.0000009536743164,
                    -5.14090515935095e-07
                ],
                "At": [
                    -1.0,
                    -4.3711398944878965e-08,
                    -2.8212994607201836e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^CUBEROOM_SPACE",
                "UserData": 0,
                "Position": [
                    -7.999755859375,
                    19.999725341796875,
                    -12.499996185302734
                ],
                "Up": [
                    -4.3711196440199274e-08,
                    1.0000009536743164,
                    -6.332998054858763e-07
                ],
                "At": [
                    -1.0,
                    -4.371140605030632e-08,
                    -4.013392356227996e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    8.000350952148438,
                    27.999252319335938,
                    -36.50007629394531
                ],
                "Up": [
                    1.6292240445636708e-07,
                    1.0000009536743164,
                    -7.129278287720808e-07
                ],
                "At": [
                    1.0,
                    -1.6292058546696353e-07,
                    2.3404745661537163e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    0.0001983642578125,
                    27.999855041503906,
                    -44.50001525878906
                ],
                "Up": [
                    7.549811442686405e-08,
                    1.0000009536743164,
                    -5.643819349643309e-07
                ],
                "At": [
                    -1.0,
                    7.54978870531886e-08,
                    -2.821300029154372e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    0.00020599365234375,
                    27.999794006347656,
                    -52.49995422363281
                ],
                "Up": [
                    7.549812863771876e-08,
                    1.0000009536743164,
                    -5.9441708799568e-07
                ],
                "At": [
                    -1.0,
                    7.54978870531886e-08,
                    -2.821300029154372e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    0.000213623046875,
                    27.999732971191406,
                    -60.49995422363281
                ],
                "Up": [
                    7.549813574314612e-08,
                    1.0000009536743164,
                    -6.239866365831404e-07
                ],
                "At": [
                    -1.0,
                    7.54978870531886e-08,
                    -2.821300029154372e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -7.999763488769531,
                    27.999732971191406,
                    -52.50001525878906
                ],
                "Up": [
                    1.5099620043201867e-07,
                    1.0000009536743164,
                    -7.15256362582295e-07
                ],
                "At": [
                    3.8941428215366614e-07,
                    -7.152557373046875e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -7.999748229980469,
                    27.999732971191406,
                    -60.50001525878906
                ],
                "Up": [
                    1.192094174484737e-07,
                    1.0000009536743164,
                    -7.15256362582295e-07
                ],
                "At": [
                    -5.606556214843295e-07,
                    7.152557373046875e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -15.999717712402344,
                    27.999549865722656,
                    -44.50019836425781
                ],
                "Up": [
                    1.6292152338337473e-07,
                    1.0000009536743164,
                    -6.395860623342742e-07
                ],
                "At": [
                    1.0,
                    -1.6292062809952768e-07,
                    1.148381556959066e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -15.999763488769531,
                    27.999671936035156,
                    -52.50001525878906
                ],
                "Up": [
                    1.6292123916628043e-07,
                    1.0000009536743164,
                    -6.388876272467314e-07
                ],
                "At": [
                    1.0,
                    -1.629206565212371e-07,
                    6.715444555993599e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -15.999732971191406,
                    27.999671936035156,
                    -60.50001525878906
                ],
                "Up": [
                    1.6292116811200685e-07,
                    1.0000009536743164,
                    -6.551857723025023e-07
                ],
                "At": [
                    1.0,
                    -1.629206565212371e-07,
                    5.523351660485787e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -15.999740600585938,
                    27.999618530273438,
                    -36.50013732910156
                ],
                "Up": [
                    1.6292136706397287e-07,
                    1.0000009536743164,
                    -6.225896527212171e-07
                ],
                "At": [
                    1.0,
                    -1.629206423103824e-07,
                    9.099630347009224e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -15.999755859375,
                    27.999618530273438,
                    -28.500137329101562
                ],
                "Up": [
                    1.629213954856823e-07,
                    1.0000009536743164,
                    -6.626362960560073e-07
                ],
                "At": [
                    1.0,
                    -1.629206423103824e-07,
                    9.099630347009224e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -15.999755859375,
                    27.99962615966797,
                    -20.500198364257812
                ],
                "Up": [
                    1.629213954856823e-07,
                    1.0000009536743164,
                    -6.523919182654936e-07
                ],
                "At": [
                    1.0,
                    -1.629206423103824e-07,
                    9.099630347009224e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -15.999778747558594,
                    27.9996337890625,
                    -12.500194549560547
                ],
                "Up": [
                    2.8213077030159184e-07,
                    1.0000009536743164,
                    -6.521590307784209e-07
                ],
                "At": [
                    1.0,
                    -2.8212994607201836e-07,
                    9.099630915443413e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -7.999786376953125,
                    27.9996337890625,
                    -12.500133514404297
                ],
                "Up": [
                    1.6292146653995587e-07,
                    1.0000009536743164,
                    -6.523919751089124e-07
                ],
                "At": [
                    1.0,
                    -1.629206423103824e-07,
                    1.0291722674082848e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    0.00020599365234375,
                    27.9996337890625,
                    -12.500133514404297
                ],
                "Up": [
                    1.6292155180508416e-07,
                    1.0000009536743164,
                    -6.093180786592711e-07
                ],
                "At": [
                    1.0,
                    -1.6292062809952768e-07,
                    1.2675908465098473e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    8.000221252441406,
                    27.9996337890625,
                    -12.500133514404297
                ],
                "Up": [
                    1.629215802267936e-07,
                    1.0000009536743164,
                    -5.75790409129695e-07
                ],
                "At": [
                    1.0,
                    -1.6292062809952768e-07,
                    1.3868001360606286e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    16.000213623046875,
                    27.9996337890625,
                    -12.500072479248047
                ],
                "Up": [
                    1.6292173654619546e-07,
                    1.0000009536743164,
                    -6.002376267133513e-07
                ],
                "At": [
                    1.0,
                    -1.6292061388867296e-07,
                    1.625218715162191e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    24.000198364257812,
                    27.9996337890625,
                    -12.500072479248047
                ],
                "Up": [
                    1.788140622238643e-07,
                    1.000001072883606,
                    -5.642602900479687e-07
                ],
                "At": [
                    1.5815071492397692e-06,
                    -5.642599489874556e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    32.00019836425781,
                    27.9996337890625,
                    -12.500011444091797
                ],
                "Up": [
                    1.1920963061129441e-07,
                    1.0000011920928955,
                    -6.834698638158443e-07
                ],
                "At": [
                    1.5815071492397692e-06,
                    -6.834692385382368e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    32.00022888183594,
                    27.99962615966797,
                    -20.500015258789062
                ],
                "Up": [
                    1.1920964482214913e-07,
                    1.0000009536743164,
                    -6.834696932855877e-07
                ],
                "At": [
                    1.8199257283413317e-06,
                    -6.834692953816557e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    8.000190734863281,
                    27.999855041503906,
                    -44.50001525878906
                ],
                "Up": [
                    7.549812153229141e-08,
                    1.0000009536743164,
                    -5.806800800201017e-07
                ],
                "At": [
                    -1.0,
                    7.54978870531886e-08,
                    -2.821300029154372e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    16.00018310546875,
                    27.999855041503906,
                    -44.50001525878906
                ],
                "Up": [
                    7.549817837571027e-08,
                    1.0000009536743164,
                    -5.643819349643309e-07
                ],
                "At": [
                    -1.0,
                    7.54978870531886e-08,
                    -4.0133929246621847e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    24.00018310546875,
                    27.999855041503906,
                    -44.49995422363281
                ],
                "Up": [
                    7.549819969199234e-08,
                    1.0000009536743164,
                    -6.076883778405318e-07
                ],
                "At": [
                    -1.0,
                    7.54978870531886e-08,
                    -4.0133929246621847e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    32.000274658203125,
                    27.999496459960938,
                    -28.499954223632812
                ],
                "Up": [
                    7.549916603011297e-08,
                    1.0000011920928955,
                    -6.852211527075269e-07
                ],
                "At": [
                    -1.0,
                    7.549782310434239e-08,
                    -1.831850795497303e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    32.00032043457031,
                    27.999496459960938,
                    -36.49995422363281
                ],
                "Up": [
                    7.549916603011297e-08,
                    1.000001072883606,
                    -6.910416914251982e-07
                ],
                "At": [
                    -1.0,
                    7.549782310434239e-08,
                    -1.831850795497303e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    32.00019836425781,
                    27.999855041503906,
                    -44.49995422363281
                ],
                "Up": [
                    7.549819258656498e-08,
                    1.0000009536743164,
                    -5.941842573520262e-07
                ],
                "At": [
                    -1.0,
                    7.54978870531886e-08,
                    -4.0133929246621847e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    24.000335693359375,
                    27.999496459960938,
                    -36.49995422363281
                ],
                "Up": [
                    7.549928682237805e-08,
                    1.0000009536743164,
                    -7.201455218819319e-07
                ],
                "At": [
                    -1.0,
                    7.549781599891503e-08,
                    -1.951060085048084e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    24.000289916992188,
                    27.999435424804688,
                    -28.499954223632812
                ],
                "Up": [
                    1.19209701665568e-07,
                    1.0000009536743164,
                    -6.834696932855877e-07
                ],
                "At": [
                    2.058344307442894e-06,
                    -6.834692953816557e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    16.00030517578125,
                    27.999374389648438,
                    -28.500015258789062
                ],
                "Up": [
                    1.4901209510753688e-07,
                    1.0000009536743164,
                    -6.8346957959875e-07
                ],
                "At": [
                    2.2967628865444567e-06,
                    -6.834692953816557e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    8.000328063964844,
                    27.999313354492188,
                    -28.500076293945312
                ],
                "Up": [
                    1.6292246129978594e-07,
                    1.0000009536743164,
                    -7.369091008513351e-07
                ],
                "At": [
                    1.0,
                    -1.6292058546696353e-07,
                    2.3404745661537163e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    0.00032806396484375,
                    27.999252319335938,
                    -28.500076293945312
                ],
                "Up": [
                    1.6292240445636708e-07,
                    1.0000009536743164,
                    -7.122295073713758e-07
                ],
                "At": [
                    1.0,
                    -1.6292058546696353e-07,
                    2.3404745661537163e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -7.999786376953125,
                    27.999855041503906,
                    -44.50001525878906
                ],
                "Up": [
                    5.960468030252741e-08,
                    1.0000009536743164,
                    -5.960470161880949e-07
                ],
                "At": [
                    -3.4924559599858185e-07,
                    5.960464477539062e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    24.000244140625,
                    27.99956512451172,
                    -20.500015258789062
                ],
                "Up": [
                    1.4901203826411802e-07,
                    1.0000009536743164,
                    -6.834696364421688e-07
                ],
                "At": [
                    2.058344307442894e-06,
                    -6.834692953816557e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    16.000244140625,
                    27.99962615966797,
                    -20.500076293945312
                ],
                "Up": [
                    1.6292192128730676e-07,
                    1.0000009536743164,
                    -6.22589709564636e-07
                ],
                "At": [
                    1.0,
                    -1.6292059967781825e-07,
                    1.8636372942637536e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    0.0002288818359375,
                    27.99956512451172,
                    -20.500076293945312
                ],
                "Up": [
                    2.8213108294039557e-07,
                    1.0000009536743164,
                    -6.188638508319855e-07
                ],
                "At": [
                    1.0,
                    -2.821299176503089e-07,
                    1.5060095392982475e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -7.999664306640625,
                    27.999252319335938,
                    -28.500076293945312
                ],
                "Up": [
                    2.086168393589105e-07,
                    1.0000009536743164,
                    -7.152559646783629e-07
                ],
                "At": [
                    -2.322715772606898e-06,
                    7.152557373046875e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    32.00018310546875,
                    27.999794006347656,
                    -52.49989318847656
                ],
                "Up": [
                    7.549812863771876e-08,
                    1.0000009536743164,
                    -5.941842573520262e-07
                ],
                "At": [
                    -1.0,
                    7.54978870531886e-08,
                    -2.821300029154372e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    32.00018310546875,
                    27.999732971191406,
                    -60.49989318847656
                ],
                "Up": [
                    7.549813574314612e-08,
                    1.0000009536743164,
                    -6.28410361969145e-07
                ],
                "At": [
                    -1.0,
                    7.54978870531886e-08,
                    -2.821300029154372e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    24.000198364257812,
                    27.999732971191406,
                    -60.49995422363281
                ],
                "Up": [
                    7.549827785169327e-08,
                    1.0000009536743164,
                    -6.321355954241881e-07
                ],
                "At": [
                    -1.0,
                    7.549787994776125e-08,
                    -5.205486104387091e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    16.000198364257812,
                    27.999732971191406,
                    -60.50001525878906
                ],
                "Up": [
                    2.980236502025946e-08,
                    1.0000009536743164,
                    -5.960470161880949e-07
                ],
                "At": [
                    -3.6414678561413893e-07,
                    5.960464477539062e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    16.000198364257812,
                    27.999794006347656,
                    -52.50001525878906
                ],
                "Up": [
                    7.549812153229141e-08,
                    1.0000009536743164,
                    -5.862680154677946e-07
                ],
                "At": [
                    -1.0,
                    7.54978870531886e-08,
                    -2.821300029154372e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    24.000198364257812,
                    27.999732971191406,
                    -52.49995422363281
                ],
                "Up": [
                    7.549824942998384e-08,
                    1.0000009536743164,
                    -5.8230983768226e-07
                ],
                "At": [
                    -1.0,
                    7.549787994776125e-08,
                    -5.205486104387091e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    8.000205993652344,
                    27.999732971191406,
                    -60.49995422363281
                ],
                "Up": [
                    1.4901158351676713e-07,
                    1.0000009536743164,
                    -5.96046959344676e-07
                ],
                "At": [
                    -3.147866323160997e-07,
                    5.960464477539062e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    8.000221252441406,
                    27.999794006347656,
                    -52.49995422363281
                ],
                "Up": [
                    1.192093463942001e-07,
                    1.0000011920928955,
                    -5.960471298749326e-07
                ],
                "At": [
                    -3.7159728094593447e-07,
                    5.960464477539062e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    16.000350952148438,
                    27.999313354492188,
                    -36.50001525878906
                ],
                "Up": [
                    1.6292247551064065e-07,
                    1.0000009536743164,
                    -7.452910040228744e-07
                ],
                "At": [
                    1.0,
                    -1.6292058546696353e-07,
                    2.3404745661537163e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    0.0003662109375,
                    27.999252319335938,
                    -36.50001525878906
                ],
                "Up": [
                    1.6292247551064065e-07,
                    1.0000009536743164,
                    -6.821944111834455e-07
                ],
                "At": [
                    1.0,
                    -1.6292057125610881e-07,
                    2.578893145255279e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -7.999641418457031,
                    27.999191284179688,
                    -36.50001525878906
                ],
                "Up": [
                    1.6292237603465765e-07,
                    1.0000011920928955,
                    -6.821945817137021e-07
                ],
                "At": [
                    1.0,
                    -1.6292058546696353e-07,
                    2.3404745661537163e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -7.999763488769531,
                    27.99968719482422,
                    -20.500137329101562
                ],
                "Up": [
                    1.629214807508106e-07,
                    1.0000009536743164,
                    -6.64964602492546e-07
                ],
                "At": [
                    1.0,
                    -1.629206423103824e-07,
                    1.0291722674082848e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    8.000221252441406,
                    27.99956512451172,
                    -20.500137329101562
                ],
                "Up": [
                    2.384186927884002e-07,
                    1.0000009536743164,
                    -5.642601195177122e-07
                ],
                "At": [
                    1.5815071492397692e-06,
                    -5.642600058308744e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    32.000244140625,
                    4.000417709350586,
                    -20.49981689453125
                ],
                "Up": [
                    -4.3711455788297826e-08,
                    1.0000009536743164,
                    -3.5204038795200177e-07
                ],
                "At": [
                    -1.0,
                    -4.371138473402425e-08,
                    7.549791547489804e-08
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^CEILINGLIGHT",
                "UserData": 0,
                "Position": [
                    7.885589599609375,
                    11.092456817626953,
                    -21.2979736328125
                ],
                "Up": [
                    -0.005051276180893183,
                    -0.9999717473983765,
                    -0.004288622178137302
                ],
                "At": [
                    0.003077085828408599,
                    0.004273140337318182,
                    -0.9999861121177673
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^CEILINGLIGHT",
                "UserData": 0,
                "Position": [
                    -0.35279083251953125,
                    11.074024200439453,
                    -21.2120361328125
                ],
                "Up": [
                    -0.016070730984210968,
                    -0.9996073842048645,
                    -0.018212495371699333
                ],
                "At": [
                    0.14631387591362,
                    0.015669016167521477,
                    -0.9891141653060913
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^CEILINGLIGHT",
                "UserData": 0,
                "Position": [
                    7.928489685058594,
                    11.054847717285156,
                    -48.18902587890625
                ],
                "Up": [
                    0.02420315332710743,
                    -0.9995266199111938,
                    0.011207494884729385
                ],
                "At": [
                    0.9948009848594666,
                    0.02297627180814743,
                    -0.09921269118785858
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^CEILINGLIGHT",
                "UserData": 0,
                "Position": [
                    15.688140869140625,
                    11.045814514160156,
                    -48.53826904296875
                ],
                "Up": [
                    0.024203108623623848,
                    -0.9995266795158386,
                    0.011207436211407185
                ],
                "At": [
                    -0.0461798831820488,
                    -0.01231815479695797,
                    -0.9988572001457214
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^CEILINGLIGHT",
                "UserData": 0,
                "Position": [
                    0.36669158935546875,
                    11.078590393066406,
                    -48.4141845703125
                ],
                "Up": [
                    0.024203119799494743,
                    -0.9995266795158386,
                    0.011207468807697296
                ],
                "At": [
                    0.9904111623764038,
                    0.022453930228948593,
                    -0.1363142430782318
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^CEILINGLIGHT",
                "UserData": 0,
                "Position": [
                    6.014717102050781,
                    19.063941955566406,
                    -52.7608642578125
                ],
                "Up": [
                    -0.016070706769824028,
                    -0.9996073842048645,
                    -0.018212437629699707
                ],
                "At": [
                    0.016043443232774734,
                    0.017956379801034927,
                    -0.9997100830078125
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^CEILINGLIGHT",
                "UserData": 0,
                "Position": [
                    7.974815368652344,
                    19.04088592529297,
                    -19.34455108642578
                ],
                "Up": [
                    -0.05636560916900635,
                    -0.9966046810150146,
                    0.04365742206573486
                ],
                "At": [
                    -0.06543939560651779,
                    -0.03997606784105301,
                    -0.9970555305480957
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^U_MINIPORTAL",
                "UserData": 0,
                "Position": [
                    10.288116455078125,
                    3.9490842819213867,
                    -25.6829833984375
                ],
                "Up": [
                    -3.924028213475594e-09,
                    1.0000009536743164,
                    -6.941836545593105e-07
                ],
                "At": [
                    -0.7420533895492554,
                    4.624272946784913e-07,
                    0.6703407764434814
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_DOOR_A",
                "UserData": 51,
                "Position": [
                    28.000213623046875,
                    4.000417709350586,
                    -20.49981689453125
                ],
                "Up": [
                    4.371142026116104e-08,
                    1.0000009536743164,
                    -3.5762832339969464e-07
                ],
                "At": [
                    1.0,
                    -4.371139183945161e-08,
                    -4.3711374075883214e-08
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    72.00038146972656,
                    4.000360488891602,
                    -12.49969482421875
                ],
                "Up": [
                    4.371141670844736e-08,
                    1.0000009536743164,
                    -3.7904874261585064e-07
                ],
                "At": [
                    1.0,
                    -4.371139183945161e-08,
                    -4.3711370523169535e-08
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    48.000091552734375,
                    4.000055313110352,
                    -12.49993896484375
                ],
                "Up": [
                    4.371159789684498e-08,
                    1.0000009536743164,
                    -5.711340236302931e-07
                ],
                "At": [
                    1.0,
                    -4.3711374075883214e-08,
                    3.139165016818879e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    56.000091552734375,
                    3.9999942779541016,
                    -12.49993896484375
                ],
                "Up": [
                    4.371171868911006e-08,
                    1.0000009536743164,
                    -5.646147656079847e-07
                ],
                "At": [
                    1.0,
                    -4.371136341774218e-08,
                    5.52335052361741e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    64.00041198730469,
                    4.000299453735352,
                    -12.4996337890625
                ],
                "Up": [
                    7.857213991035398e-15,
                    1.0000009536743164,
                    -3.576282097128569e-07
                ],
                "At": [
                    6.146722597577536e-08,
                    3.5762786865234375e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -71.99969482421875,
                    4.000356674194336,
                    -20.499755859375
                ],
                "Up": [
                    -7.549795810746218e-08,
                    1.0000009536743164,
                    -1.9907065507140942e-07
                ],
                "At": [
                    1.0,
                    7.549790126404332e-08,
                    7.54978870531886e-08
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -23.999755859375,
                    3.9997501373291016,
                    -12.49993896484375
                ],
                "Up": [
                    -1.6292041493670695e-07,
                    1.0000009536743164,
                    -7.003549740147719e-07
                ],
                "At": [
                    -1.0,
                    -1.6292071336465597e-07,
                    -6.397577294592338e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -31.999740600585938,
                    4.000238418579102,
                    -12.49993896484375
                ],
                "Up": [
                    -7.549797942374425e-08,
                    1.0000009536743164,
                    -2.945312473912054e-07
                ],
                "At": [
                    1.0,
                    7.549790126404332e-08,
                    -4.371141315573368e-08
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -39.99974060058594,
                    4.000360488891602,
                    -12.49981689453125
                ],
                "Up": [
                    -7.549797942374425e-08,
                    1.0000009536743164,
                    -2.377205703396612e-07
                ],
                "At": [
                    1.0,
                    7.549790126404332e-08,
                    -4.371140960302e-08
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -47.999725341796875,
                    4.000299453735352,
                    -12.49981689453125
                ],
                "Up": [
                    -7.549797942374425e-08,
                    1.0000009536743164,
                    -2.3795337256160565e-07
                ],
                "At": [
                    1.0,
                    7.549790126404332e-08,
                    -4.371140960302e-08
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -55.99971008300781,
                    4.000238418579102,
                    -12.49981689453125
                ],
                "Up": [
                    -7.549797942374425e-08,
                    1.0000009536743164,
                    -2.400488483544905e-07
                ],
                "At": [
                    1.0,
                    7.549790126404332e-08,
                    -4.371140960302e-08
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -63.99971008300781,
                    4.000177383422852,
                    -12.49981689453125
                ],
                "Up": [
                    -1.9470738266136323e-07,
                    1.0000009536743164,
                    -2.780002432700712e-07
                ],
                "At": [
                    1.0,
                    1.9470718370939721e-07,
                    -4.371144157744311e-08
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -71.99969482421875,
                    4.000055313110352,
                    -12.49981689453125
                ],
                "Up": [
                    -1.9470738266136323e-07,
                    1.0000009536743164,
                    -3.0803542472312984e-07
                ],
                "At": [
                    1.0,
                    1.9470718370939721e-07,
                    -4.371144868287047e-08
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -23.999603271484375,
                    4.000162124633789,
                    -44.5
                ],
                "Up": [
                    1.9470776635444054e-07,
                    1.0000009536743164,
                    -4.321341009472235e-07
                ],
                "At": [
                    -1.0,
                    1.9470714107683307e-07,
                    -9.973857686418341e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -31.999649047851562,
                    4.000226974487305,
                    -36.5
                ],
                "Up": [
                    2.3841842278216063e-07,
                    1.0000009536743164,
                    -3.5762795391747204e-07
                ],
                "At": [
                    -1.1548386282811407e-06,
                    3.5762786865234375e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -39.99971008300781,
                    3.9999818801879883,
                    -36.49981689453125
                ],
                "Up": [
                    1.1920927533992653e-07,
                    1.0000009536743164,
                    -4.76837556107057e-07
                ],
                "At": [
                    -6.8917790940759e-07,
                    4.76837158203125e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -47.99967956542969,
                    4.000410079956055,
                    -36.49981689453125
                ],
                "Up": [
                    -9.9253938401489e-14,
                    1.0000009536743164,
                    -2.3841880647523794e-07
                ],
                "At": [
                    -4.16300736105768e-07,
                    2.384185791015625e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -71.99969482421875,
                    4.000059127807617,
                    -4.499818801879883
                ],
                "Up": [
                    -1.9470738266136323e-07,
                    1.0000009536743164,
                    -2.982565092679579e-07
                ],
                "At": [
                    1.0,
                    1.9470718370939721e-07,
                    -4.371144513015679e-08
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -71.99969482421875,
                    4.000062942504883,
                    3.500181198120117
                ],
                "Up": [
                    -1.9470738266136323e-07,
                    1.0000009536743164,
                    -3.164172994729597e-07
                ],
                "At": [
                    1.0,
                    1.9470718370939721e-07,
                    -4.371144868287047e-08
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -71.99971008300781,
                    4.000066757202148,
                    11.50018310546875
                ],
                "Up": [
                    -1.9470738266136323e-07,
                    1.0000009536743164,
                    -3.2852449294296093e-07
                ],
                "At": [
                    1.0,
                    1.9470718370939721e-07,
                    -4.371145223558415e-08
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -71.99971008300781,
                    4.000009536743164,
                    19.50018310546875
                ],
                "Up": [
                    -3.1391684274240106e-07,
                    1.000001072883606,
                    -3.583268437523657e-07
                ],
                "At": [
                    1.0,
                    3.1391647326017846e-07,
                    -4.371150197357565e-08
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -71.99971008300781,
                    4.00001335144043,
                    27.50018310546875
                ],
                "Up": [
                    -3.1391684274240106e-07,
                    1.0000009536743164,
                    -3.511090085339674e-07
                ],
                "At": [
                    1.0,
                    3.1391647326017846e-07,
                    -1.6292078441892954e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -71.99971008300781,
                    4.000017166137695,
                    35.50018310546875
                ],
                "Up": [
                    -1.5099598726919794e-07,
                    1.0000009536743164,
                    -3.576281812911475e-07
                ],
                "At": [
                    -1.5099581673894136e-07,
                    -3.5762786865234375e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^CUBEROOM_SPACE",
                "UserData": 0,
                "Position": [
                    16.000213623046875,
                    19.99993896484375,
                    -4.499933242797852
                ],
                "Up": [
                    -1.509958593715055e-07,
                    1.0000009536743164,
                    -5.960470161880949e-07
                ],
                "At": [
                    1.5099588779321493e-07,
                    -5.960464477539062e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_DOOR_A",
                "UserData": 51,
                "Position": [
                    -11.999755859375,
                    19.999862670898438,
                    -28.499977111816406
                ],
                "Up": [
                    7.549823521912913e-08,
                    1.0000009536743164,
                    -5.587939426732191e-07
                ],
                "At": [
                    -1.0,
                    7.549787994776125e-08,
                    -5.205486104387091e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^U_PORTALLINE",
                "UserData": 0,
                "Position": [
                    10.947929382324219,
                    5.542774200439453,
                    -26.27899169921875
                ],
                "Up": [
                    0.5088004469871521,
                    0.8121059536933899,
                    -0.28567081689834595
                ],
                "At": [
                    -29.868656158447266,
                    24.612422943115234,
                    16.770034790039062
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    16.000259399414062,
                    19.999610900878906,
                    -60.499908447265625
                ],
                "Up": [
                    1.9470765266760282e-07,
                    1.0000009536743164,
                    -5.736950470236479e-07
                ],
                "At": [
                    -1.0,
                    1.9470715528768778e-07,
                    -5.20548667282128e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_DOOR_A",
                "UserData": 51,
                "Position": [
                    28.000274658203125,
                    19.99951934814453,
                    -44.499847412109375
                ],
                "Up": [
                    1.6292133864226344e-07,
                    1.0000009536743164,
                    -6.780032322240004e-07
                ],
                "At": [
                    1.0,
                    -1.629206565212371e-07,
                    7.907537451501412e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^U_MINIPORTAL",
                "UserData": 0,
                "Position": [
                    -17.54931640625,
                    27.97802734375,
                    -10.498668670654297
                ],
                "Up": [
                    1.1398961419217812e-07,
                    1.0000009536743164,
                    -5.186731186768156e-07
                ],
                "At": [
                    0.7459890246391296,
                    -4.304492335904797e-07,
                    -0.6659582257270813
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    64.00057983398438,
                    4.000261306762695,
                    35.50022888183594
                ],
                "Up": [
                    2.8213040081936924e-07,
                    1.0000011920928955,
                    -1.490119245772803e-07
                ],
                "At": [
                    1.0,
                    -2.8212994607201836e-07,
                    7.907536883067223e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_W_STA",
                "UserData": 51,
                "Position": [
                    56.00054931640625,
                    4.000261306762695,
                    35.50022888183594
                ],
                "Up": [
                    2.821304576627881e-07,
                    1.0000011920928955,
                    -2.011660029666018e-07
                ],
                "At": [
                    1.0,
                    -2.8212994607201836e-07,
                    9.099629778575036e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_WALKWAY",
                "UserData": 51,
                "Position": [
                    40.00054931640625,
                    12.000202178955078,
                    35.50022888183594
                ],
                "Up": [
                    2.8213051450620696e-07,
                    1.0000011920928955,
                    -2.5332002451250446e-07
                ],
                "At": [
                    1.0,
                    -2.8212994607201836e-07,
                    9.099629778575036e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_WALKWAY",
                "UserData": 51,
                "Position": [
                    24.000106811523438,
                    11.999164581298828,
                    35.50044250488281
                ],
                "Up": [
                    -7.549627412117843e-08,
                    1.0000011920928955,
                    -9.089717423194088e-07
                ],
                "At": [
                    1.0,
                    7.549798652917161e-08,
                    1.982846470127697e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_WALKWAY",
                "UserData": 51,
                "Position": [
                    32.00050354003906,
                    12.000141143798828,
                    35.50025939941406
                ],
                "Up": [
                    2.821305429279164e-07,
                    1.0000011920928955,
                    -2.7567205052037025e-07
                ],
                "At": [
                    1.0,
                    -2.821299176503089e-07,
                    1.0291722674082848e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_W_STA",
                "UserData": 51,
                "Position": [
                    -55.99971008300781,
                    3.9999561309814453,
                    35.50018310546875
                ],
                "Up": [
                    -2.821302871325315e-07,
                    1.0000011920928955,
                    -4.3958488049611333e-07
                ],
                "At": [
                    -1.0,
                    -2.821299744937278e-07,
                    -4.371126749447285e-08
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_WALKWAY",
                "UserData": 51,
                "Position": [
                    -39.99969482421875,
                    11.999897003173828,
                    35.50019836425781
                ],
                "Up": [
                    -4.013397187918599e-07,
                    1.0000011920928955,
                    -4.6193665070859424e-07
                ],
                "At": [
                    -1.0,
                    -4.0133926404450904e-07,
                    -4.371120354562663e-08
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -15.999969482421875,
                    11.999408721923828,
                    35.50044250488281
                ],
                "Up": [
                    -4.3710063124535736e-08,
                    1.0000011920928955,
                    -8.493670407005993e-07
                ],
                "At": [
                    -1.0,
                    -4.3711462893725184e-08,
                    -1.712641392259684e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -63.99969482421875,
                    3.9999561309814453,
                    35.50018310546875
                ],
                "Up": [
                    -2.821303439759504e-07,
                    1.0000011920928955,
                    -4.0233194908978476e-07
                ],
                "At": [
                    -1.0,
                    -2.821299744937278e-07,
                    7.549801495088104e-08
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_WALKWAY",
                "UserData": 51,
                "Position": [
                    -7.9999237060546875,
                    11.999408721923828,
                    35.50041198730469
                ],
                "Up": [
                    -4.371027984007014e-08,
                    1.0000011920928955,
                    -7.748610642011045e-07
                ],
                "At": [
                    -1.0,
                    -4.3711459341011505e-08,
                    -1.5934321027089027e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_WALKWAY",
                "UserData": 51,
                "Position": [
                    -31.99969482421875,
                    11.999774932861328,
                    35.50019836425781
                ],
                "Up": [
                    -4.013396051050222e-07,
                    1.0000009536743164,
                    -5.215410396886e-07
                ],
                "At": [
                    -1.0,
                    -4.0133926404450904e-07,
                    -4.371118222934456e-08
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_WALKWAY",
                "UserData": 51,
                "Position": [
                    7.62939453125e-05,
                    11.999408721923828,
                    35.50041198730469
                ],
                "Up": [
                    -1.629196191288429e-07,
                    1.0000011920928955,
                    -8.344658795067517e-07
                ],
                "At": [
                    -1.0,
                    -1.629207559972201e-07,
                    -1.593431989022065e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_WALKWAY",
                "UserData": 51,
                "Position": [
                    8.000091552734375,
                    11.999347686767578,
                    35.50044250488281
                ],
                "Up": [
                    -1.6291960491798818e-07,
                    1.0000011920928955,
                    -8.419165169470944e-07
                ],
                "At": [
                    -1.0,
                    -1.629207559972201e-07,
                    -1.593431989022065e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_WALKWAY",
                "UserData": 51,
                "Position": [
                    -23.99969482421875,
                    11.999713897705078,
                    35.500213623046875
                ],
                "Up": [
                    -4.0133966194844106e-07,
                    1.0000011920928955,
                    -5.438930088530469e-07
                ],
                "At": [
                    -1.0,
                    -4.0133926404450904e-07,
                    -1.629204575692711e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    16.000106811523438,
                    11.999286651611328,
                    35.50044250488281
                ],
                "Up": [
                    -7.549657254912745e-08,
                    1.000001072883606,
                    -8.493668701703427e-07
                ],
                "At": [
                    1.0,
                    7.549797942374425e-08,
                    1.7444278910261346e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_DOOR_A",
                "UserData": 51,
                "Position": [
                    0.00018310546875,
                    11.99997329711914,
                    -56.5
                ],
                "Up": [
                    1.5099610095603566e-07,
                    1.0000011920928955,
                    -5.960471867183514e-07
                ],
                "At": [
                    2.0861591565335402e-07,
                    -5.960464477539062e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_DOOR_A",
                "UserData": 51,
                "Position": [
                    28.000106811523438,
                    11.999732971191406,
                    -44.49993896484375
                ],
                "Up": [
                    4.3711697372827985e-08,
                    1.0000011920928955,
                    -6.332999760161329e-07
                ],
                "At": [
                    1.0,
                    -4.3711370523169535e-08,
                    4.3312579123266914e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_DOOR_A",
                "UserData": 51,
                "Position": [
                    -11.9998779296875,
                    12.000099182128906,
                    -44.50006103515625
                ],
                "Up": [
                    7.549814995400084e-08,
                    1.0000011920928955,
                    -6.109482342253614e-07
                ],
                "At": [
                    -1.0,
                    7.54978870531886e-08,
                    -2.821300029154372e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^U_PORTALLINE",
                "UserData": 0,
                "Position": [
                    3.524017333984375,
                    5.589599609375,
                    -17.8424072265625
                ],
                "Up": [
                    1.7344951629638672e-05,
                    0.9999994039535522,
                    -0.001969575881958008
                ],
                "At": [
                    -0.5511108040809631,
                    0.1229563057422638,
                    62.422916412353516
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^U_MINIPORTAL",
                "UserData": 0,
                "Position": [
                    2.955718994140625,
                    3.9958410263061523,
                    -18.52618408203125
                ],
                "Up": [
                    -5.038549488745048e-08,
                    1.0000011920928955,
                    -5.236728952695557e-07
                ],
                "At": [
                    -0.6391324996948242,
                    -4.349575704054587e-07,
                    -0.7690966725349426
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_DOOR_A",
                "UserData": 51,
                "Position": [
                    -11.99957275390625,
                    3.9998645782470703,
                    -28.499969482421875
                ],
                "Up": [
                    1.9470799372811598e-07,
                    1.0000011920928955,
                    -5.122278139424452e-07
                ],
                "At": [
                    -1.0,
                    1.9470712686597835e-07,
                    -1.2358043477433966e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_DOOR_A",
                "UserData": 51,
                "Position": [
                    28.000274658203125,
                    3.9997425079345703,
                    -28.50018310546875
                ],
                "Up": [
                    -7.549662228711895e-08,
                    1.0000011920928955,
                    -8.884825319910306e-07
                ],
                "At": [
                    1.0,
                    7.54979723183169e-08,
                    1.6252186014753534e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_DOOR_A",
                "UserData": 51,
                "Position": [
                    16.000396728515625,
                    3.9999732971191406,
                    -56.500152587890625
                ],
                "Up": [
                    1.5273684539351962e-07,
                    1.0000011920928955,
                    -3.258415972595685e-07
                ],
                "At": [
                    1.104670104723482e-06,
                    -3.2584136988589307e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_DOOR_A",
                "UserData": 51,
                "Position": [
                    0.0004730224609375,
                    3.9999732971191406,
                    -56.500030517578125
                ],
                "Up": [
                    1.0058283805847168e-07,
                    1.0000011920928955,
                    -4.450511141840252e-07
                ],
                "At": [
                    8.662514687785006e-07,
                    -4.450506594366743e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_DOOR_A",
                "UserData": 51,
                "Position": [
                    8.00042724609375,
                    3.9999732971191406,
                    -56.5
                ],
                "Up": [
                    2.1979202813326992e-07,
                    1.0000011920928955,
                    -3.258415688378591e-07
                ],
                "At": [
                    8.662514687785006e-07,
                    -3.2584136988589307e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_DOOR_A",
                "UserData": 51,
                "Position": [
                    -11.99969482421875,
                    3.9999818801879883,
                    -36.500030517578125
                ],
                "Up": [
                    1.9470793688469712e-07,
                    1.0000011920928955,
                    -4.2282081835764984e-07
                ],
                "At": [
                    -1.0,
                    1.9470712686597835e-07,
                    -1.355013637294178e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_DOOR_A",
                "UserData": 51,
                "Position": [
                    -11.99957275390625,
                    4.000101089477539,
                    -44.50006103515625
                ],
                "Up": [
                    1.9470769530016696e-07,
                    1.0000011920928955,
                    -4.116450611491018e-07
                ],
                "At": [
                    -1.0,
                    1.9470715528768778e-07,
                    -7.589671895402716e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_BIO",
                "UserData": 51,
                "Position": [
                    -15.999801635742188,
                    11.999866485595703,
                    -28.5
                ],
                "Up": [
                    1.5099624306458281e-07,
                    1.0000011920928955,
                    -7.152565331125516e-07
                ],
                "At": [
                    3.8941428215366614e-07,
                    -7.152557373046875e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_DOOR_A",
                "UserData": 51,
                "Position": [
                    0.0001220703125,
                    11.999870300292969,
                    -16.500091552734375
                ],
                "Up": [
                    1.564622920113834e-07,
                    1.0000011920928955,
                    -7.152565331125516e-07
                ],
                "At": [
                    -3.278251483607164e-07,
                    7.152557373046875e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_IND",
                "UserData": 51,
                "Position": [
                    -15.999984741210938,
                    3.999876022338867,
                    -4.500062942504883
                ],
                "Up": [
                    -7.549770231207731e-08,
                    1.0000011920928955,
                    -5.699700977856992e-07
                ],
                "At": [
                    1.0,
                    7.54979225803254e-08,
                    5.523349955183221e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_IND",
                "UserData": 51,
                "Position": [
                    16.019332885742188,
                    3.9990978240966797,
                    27.490692138671875
                ],
                "Up": [
                    -4.371123907276342e-08,
                    1.0000009536743164,
                    -4.172329965967947e-07
                ],
                "At": [
                    -1.0,
                    -4.371140960302e-08,
                    -5.205485535952903e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_SCAN",
                "UserData": 51,
                "Position": [
                    16.01934814453125,
                    3.999088764190674,
                    35.49064636230469
                ],
                "Up": [
                    -4.3711189334771916e-08,
                    1.000001072883606,
                    -3.6694120808533626e-07
                ],
                "At": [
                    -1.0,
                    -4.371142026116104e-08,
                    -7.589671326968528e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    0.0001220703125,
                    11.99993896484375,
                    -4.500066757202148
                ],
                "Up": [
                    1.5099621464287338e-07,
                    1.000001072883606,
                    -7.152564762691327e-07
                ],
                "At": [
                    3.8941428215366614e-07,
                    -7.152557373046875e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -7.999908447265625,
                    12.0,
                    -4.500127792358398
                ],
                "Up": [
                    1.62921409696537e-07,
                    1.000001072883606,
                    -7.599596756335814e-07
                ],
                "At": [
                    1.0,
                    -1.629206565212371e-07,
                    7.907537451501412e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    8.000152587890625,
                    11.9998779296875,
                    -4.500036239624023
                ],
                "Up": [
                    7.549832048425742e-08,
                    1.000001072883606,
                    -7.003550877016096e-07
                ],
                "At": [
                    -1.0,
                    7.549787994776125e-08,
                    -5.205486104387091e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    16.000152587890625,
                    11.99981689453125,
                    -4.500005722045898
                ],
                "Up": [
                    7.549832048425742e-08,
                    1.000001072883606,
                    -7.003550877016096e-07
                ],
                "At": [
                    -1.0,
                    7.549787994776125e-08,
                    -5.205486104387091e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    24.000137329101562,
                    12.00018310546875,
                    -4.500005722045898
                ],
                "Up": [
                    7.549806468887255e-08,
                    1.000001072883606,
                    -5.662446369569807e-07
                ],
                "At": [
                    -1.0,
                    7.549789415861596e-08,
                    -1.6292071336465597e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -23.999786376953125,
                    4.000173568725586,
                    -20.499755859375
                ],
                "Up": [
                    7.549846969823193e-08,
                    1.0000011920928955,
                    -5.215413239056943e-07
                ],
                "At": [
                    -1.0,
                    7.549785863147918e-08,
                    -9.973857686418341e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_DOOR_A",
                "UserData": 51,
                "Position": [
                    -27.99981689453125,
                    4.000234603881836,
                    -20.499786376953125
                ],
                "Up": [
                    4.371199935349068e-08,
                    1.0000009536743164,
                    -5.364422577258665e-07
                ],
                "At": [
                    1.0,
                    -4.3711338548746426e-08,
                    1.148381556959066e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_DOOR_A",
                "UserData": 51,
                "Position": [
                    44.000213623046875,
                    4.000295639038086,
                    -20.499755859375
                ],
                "Up": [
                    -4.371138473402425e-08,
                    1.000001072883606,
                    -3.5762835182140407e-07
                ],
                "At": [
                    -1.0,
                    -4.3711395392165286e-08,
                    -1.6292067073209182e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    48.000396728515625,
                    4.0005340576171875,
                    -28.4998779296875
                ],
                "Up": [
                    1.4901161193847656e-07,
                    1.0000009536743164,
                    -4.768376129504759e-07
                ],
                "At": [
                    -2.0116540611070377e-07,
                    4.76837158203125e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^CEILINGLIGHT",
                "UserData": 0,
                "Position": [
                    8.613327026367188,
                    27.020187377929688,
                    -34.03480529785156
                ],
                "Up": [
                    0.14669068157672882,
                    -4.996431827545166,
                    0.072608582675457
                ],
                "At": [
                    0.08039659261703491,
                    -0.012123605236411095,
                    -0.9966892600059509
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^CEILINGLIGHT",
                "UserData": 0,
                "Position": [
                    8.653640747070312,
                    27.020187377929688,
                    -34.26057434082031
                ],
                "Up": [
                    0.10608834028244019,
                    -3.613478660583496,
                    0.052511781454086304
                ],
                "At": [
                    0.12328987568616867,
                    -0.010800798423588276,
                    -0.9923118948936462
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^CEILINGLIGHT",
                "UserData": 0,
                "Position": [
                    8.914688110351562,
                    27.020187377929688,
                    -34.21836853027344
                ],
                "Up": [
                    0.0734054297208786,
                    -2.5002641677856445,
                    0.036334335803985596
                ],
                "At": [
                    0.12328990548849106,
                    -0.010800797492265701,
                    -0.992311954498291
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^CEILINGLIGHT",
                "UserData": 0,
                "Position": [
                    8.852630615234375,
                    27.020248413085938,
                    -34.41191101074219
                ],
                "Up": [
                    0.04920408874750137,
                    -1.675942063331604,
                    0.024355124682188034
                ],
                "At": [
                    0.12328995764255524,
                    -0.010800798423588276,
                    -0.992311954498291
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^U_MINIPORTAL",
                "UserData": 0,
                "Position": [
                    26.635498046875,
                    19.995338439941406,
                    -59.47735595703125
                ],
                "Up": [
                    -2.1676058281627775e-08,
                    1.0000009536743164,
                    -5.300295242705033e-07
                ],
                "At": [
                    -0.9989708662033081,
                    -4.569398370790623e-08,
                    -0.04535648599267006
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^U_MINIPORTAL",
                "UserData": 0,
                "Position": [
                    10.13909912109375,
                    3.9960803985595703,
                    -29.3868408203125
                ],
                "Up": [
                    -1.205649908797568e-07,
                    1.0000009536743164,
                    -4.684392820308858e-07
                ],
                "At": [
                    -0.9011276364326477,
                    9.444914184086883e-08,
                    0.43355390429496765
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^U_PORTALLINE",
                "UserData": 0,
                "Position": [
                    27.523712158203125,
                    21.589088439941406,
                    -59.43702697753906
                ],
                "Up": [
                    -0.20783653855323792,
                    0.9047567248344421,
                    0.3717796206474304
                ],
                "At": [
                    -17.024961471557617,
                    -16.425107955932617,
                    30.454383850097656
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_DOOR_A",
                "UserData": 51,
                "Position": [
                    16.000213623046875,
                    19.99993133544922,
                    -16.499916076660156
                ],
                "Up": [
                    2.980235080940474e-08,
                    1.0000009536743164,
                    -5.960470161880949e-07
                ],
                "At": [
                    -2.682206172721635e-07,
                    5.960464477539062e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1721767807,
                "ObjectID": "^BASE_COLDPLANT3",
                "UserData": 11,
                "Position": [
                    25.77557373046875,
                    12.000114440917969,
                    -17.9111328125
                ],
                "Up": [
                    1.9275019358389045e-09,
                    0.7586881518363953,
                    -4.348511879470607e-07
                ],
                "At": [
                    -0.17794667184352875,
                    -5.635623097077769e-07,
                    -0.9840400815010071
                ],
                "Message": ""
            },
            {
                "Timestamp": 1721767797,
                "ObjectID": "^BASE_TREE01",
                "UserData": 11,
                "Position": [
                    -9.980178833007812,
                    11.999870300292969,
                    -18.34033203125
                ],
                "Up": [
                    1.2633931589789427e-07,
                    0.8674043416976929,
                    -5.129838882567128e-07
                ],
                "At": [
                    0.8643290400505066,
                    -4.2332291627644736e-07,
                    -0.5029269456863403
                ],
                "Message": ""
            },
            {
                "Timestamp": 1721767942,
                "ObjectID": "^BASE_TREE02",
                "UserData": 0,
                "Position": [
                    26.675979614257812,
                    11.99985122680664,
                    -55.1646728515625
                ],
                "Up": [
                    5.4305104413288063e-08,
                    0.6651593446731567,
                    -4.477807067360118e-07
                ],
                "At": [
                    -0.8127160668373108,
                    4.5859465558351076e-07,
                    0.5826599597930908
                ],
                "Message": ""
            },
            {
                "Timestamp": 1721767873,
                "ObjectID": "^BASE_DUSTPLANT3",
                "UserData": 0,
                "Position": [
                    -10.196258544921875,
                    12.00003433227539,
                    -55.1475830078125
                ],
                "Up": [
                    -5.928733770588224e-08,
                    1.0000009536743164,
                    -4.194668292711867e-07
                ],
                "At": [
                    -0.9371986985206604,
                    9.074425832977795e-08,
                    0.348796010017395
                ],
                "Message": ""
            },
            {
                "Timestamp": 1721767983,
                "ObjectID": "^BASE_COLDPLANT3",
                "UserData": 11,
                "Position": [
                    -8.9208984375,
                    4.000234603881836,
                    -17.858673095703125
                ],
                "Up": [
                    -6.370557770196683e-08,
                    0.6311447620391846,
                    -2.541596870742069e-07
                ],
                "At": [
                    0.9243057370185852,
                    -6.039396538426445e-08,
                    -0.3816528618335724
                ],
                "Message": ""
            },
            {
                "Timestamp": 1721767992,
                "ObjectID": "^BASE_COLDPLANT3",
                "UserData": 11,
                "Position": [
                    -10.518173217773438,
                    4.000095367431641,
                    -54.81793212890625
                ],
                "Up": [
                    -2.538372623206442e-09,
                    0.8651565909385681,
                    -4.229323167237453e-07
                ],
                "At": [
                    0.23725196719169617,
                    4.755891040986171e-07,
                    0.9714481830596924
                ],
                "Message": ""
            },
            {
                "Timestamp": 1721767999,
                "ObjectID": "^BASE_COLDPLANT3",
                "UserData": 11,
                "Position": [
                    25.946823120117188,
                    4.000278472900391,
                    -54.238525390625
                ],
                "Up": [
                    1.7132569141153908e-08,
                    0.8651565313339233,
                    -4.873069769928406e-07
                ],
                "At": [
                    -0.5845182538032532,
                    4.6859233293616853e-07,
                    0.8113805055618286
                ],
                "Message": ""
            },
            {
                "Timestamp": 1721768015,
                "ObjectID": "^BASE_COLDPLANT3",
                "UserData": 11,
                "Position": [
                    25.8873291015625,
                    3.996204376220703,
                    -24.311767578125
                ],
                "Up": [
                    5.7506095885173636e-08,
                    0.8651565313339233,
                    -4.961990498486557e-07
                ],
                "At": [
                    -0.6812859177589417,
                    4.6512329276993114e-07,
                    0.7320173978805542
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    24.000259399414062,
                    19.999610900878906,
                    -60.499908447265625
                ],
                "Up": [
                    1.9470762424589338e-07,
                    1.0000009536743164,
                    -5.234036279944121e-07
                ],
                "At": [
                    -1.0,
                    1.9470715528768778e-07,
                    -5.20548667282128e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_W_STA",
                "UserData": 51,
                "Position": [
                    24.00030517578125,
                    11.999603271484375,
                    -68.49996948242188
                ],
                "Up": [
                    1.629211254794427e-07,
                    1.0000009536743164,
                    -4.6938691866671434e-07
                ],
                "At": [
                    1.0,
                    -1.629206565212371e-07,
                    6.715443987559411e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    32.00028991699219,
                    19.999595642089844,
                    -68.49984741210938
                ],
                "Up": [
                    1.9470768108931225e-07,
                    1.0000009536743164,
                    -6.295744015005766e-07
                ],
                "At": [
                    -1.0,
                    1.9470715528768778e-07,
                    -5.20548667282128e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    40.00028991699219,
                    19.999595642089844,
                    -68.49984741210938
                ],
                "Up": [
                    1.9470768108931225e-07,
                    1.0000009536743164,
                    -6.407502155525435e-07
                ],
                "At": [
                    -1.0,
                    1.9470715528768778e-07,
                    -5.20548667282128e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    48.00028991699219,
                    19.999595642089844,
                    -68.49984741210938
                ],
                "Up": [
                    1.9470769530016696e-07,
                    1.0000009536743164,
                    -6.57514078739041e-07
                ],
                "At": [
                    -1.0,
                    1.9470715528768778e-07,
                    -5.20548667282128e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -15.999740600585938,
                    19.999595642089844,
                    -68.50006103515625
                ],
                "Up": [
                    2.821304576627881e-07,
                    1.0000009536743164,
                    -4.787001444128691e-07
                ],
                "At": [
                    1.0,
                    -2.8212994607201836e-07,
                    5.523351660485787e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -31.999740600585938,
                    19.999717712402344,
                    -68.50009155273438
                ],
                "Up": [
                    2.821304576627881e-07,
                    1.0000009536743164,
                    -4.82425434711331e-07
                ],
                "At": [
                    1.0,
                    -2.8212994607201836e-07,
                    5.523351660485787e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -23.999740600585938,
                    19.999549865722656,
                    -60.50006103515625
                ],
                "Up": [
                    1.629210260034597e-07,
                    1.0000009536743164,
                    -4.880134270024428e-07
                ],
                "At": [
                    1.0,
                    -1.6292067073209182e-07,
                    4.33125848076088e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -31.999740600585938,
                    19.999794006347656,
                    -60.500091552734375
                ],
                "Up": [
                    2.821304576627881e-07,
                    1.0000009536743164,
                    -4.563483742003882e-07
                ],
                "At": [
                    1.0,
                    -2.8212994607201836e-07,
                    5.523351660485787e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -39.99974060058594,
                    19.999855041503906,
                    -60.500091552734375
                ],
                "Up": [
                    2.8213042924107867e-07,
                    1.0000009536743164,
                    -4.265460518126929e-07
                ],
                "At": [
                    1.0,
                    -2.8212994607201836e-07,
                    5.523351660485787e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -39.999725341796875,
                    19.999839782714844,
                    -68.50009155273438
                ],
                "Up": [
                    2.821304576627881e-07,
                    1.0000009536743164,
                    -4.842880230171431e-07
                ],
                "At": [
                    1.0,
                    -2.8212994607201836e-07,
                    5.523351660485787e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -47.99974060058594,
                    19.999900817871094,
                    -68.50009155273438
                ],
                "Up": [
                    2.821304576627881e-07,
                    1.0000009536743164,
                    -4.86150725009793e-07
                ],
                "At": [
                    1.0,
                    -2.8212994607201836e-07,
                    5.523351660485787e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -55.99974060058594,
                    19.999961853027344,
                    -68.50009155273438
                ],
                "Up": [
                    2.821304576627881e-07,
                    1.0000009536743164,
                    -4.86150725009793e-07
                ],
                "At": [
                    1.0,
                    -2.8212994607201836e-07,
                    5.523351660485787e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -47.999755859375,
                    19.999977111816406,
                    -60.50006103515625
                ],
                "Up": [
                    2.682208162241295e-07,
                    1.0000009536743164,
                    -4.4505088681034977e-07
                ],
                "At": [
                    6.278328328335192e-07,
                    -4.450506310149649e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -55.999755859375,
                    19.999977111816406,
                    -60.500091552734375
                ],
                "Up": [
                    2.682208162241295e-07,
                    1.0000009536743164,
                    -4.4505088681034977e-07
                ],
                "At": [
                    6.278328328335192e-07,
                    -4.450506310149649e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -63.99974060058594,
                    20.000038146972656,
                    -60.500091552734375
                ],
                "Up": [
                    2.980231954552437e-07,
                    1.0000009536743164,
                    -4.450508015452215e-07
                ],
                "At": [
                    8.662514119350817e-07,
                    -4.450506310149649e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -63.99974060058594,
                    20.000022888183594,
                    -68.50006103515625
                ],
                "Up": [
                    2.821304576627881e-07,
                    1.0000009536743164,
                    -4.86150725009793e-07
                ],
                "At": [
                    1.0,
                    -2.8212994607201836e-07,
                    5.523351660485787e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    56.00028991699219,
                    19.999595642089844,
                    -68.49984741210938
                ],
                "Up": [
                    3.1391709853778593e-07,
                    1.0000009536743164,
                    -6.277116995079268e-07
                ],
                "At": [
                    -1.0,
                    3.1391644483846903e-07,
                    -5.205487241255469e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    40.000274658203125,
                    19.999671936035156,
                    -60.499847412109375
                ],
                "Up": [
                    1.5099635675142054e-07,
                    1.0000009536743164,
                    -7.152563057388761e-07
                ],
                "At": [
                    6.278329465203569e-07,
                    -7.152557373046875e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    48.00025939941406,
                    19.999732971191406,
                    -60.49981689453125
                ],
                "Up": [
                    1.5099635675142054e-07,
                    1.0000009536743164,
                    -7.152563057388761e-07
                ],
                "At": [
                    6.278328896769381e-07,
                    -7.152557373046875e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    56.00028991699219,
                    19.999610900878906,
                    -60.499847412109375
                ],
                "Up": [
                    3.894151632266585e-07,
                    1.0000009536743164,
                    -7.152561920520384e-07
                ],
                "At": [
                    6.278327759901003e-07,
                    -7.152557373046875e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    64.00028991699219,
                    19.999610900878906,
                    -60.499847412109375
                ],
                "Up": [
                    4.3312664388395206e-07,
                    1.0000009536743164,
                    -6.314368192761322e-07
                ],
                "At": [
                    -1.0,
                    4.331257343892503e-07,
                    -7.589673600705282e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    64.00032043457031,
                    19.999595642089844,
                    -68.49984741210938
                ],
                "Up": [
                    3.1391709853778593e-07,
                    1.0000009536743164,
                    -6.258490543586959e-07
                ],
                "At": [
                    -1.0,
                    3.1391644483846903e-07,
                    -5.205487241255469e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -55.99974060058594,
                    19.999961853027344,
                    -76.5001220703125
                ],
                "Up": [
                    2.682209014892578e-07,
                    1.0000009536743164,
                    -4.768374424202193e-07
                ],
                "At": [
                    -7.525079013248615e-07,
                    4.76837158203125e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -55.99971008300781,
                    20.000083923339844,
                    -84.50015258789062
                ],
                "Up": [
                    2.980231954552437e-07,
                    1.0000009536743164,
                    -4.768373855768004e-07
                ],
                "At": [
                    -7.599583682349476e-07,
                    4.76837158203125e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -55.99971008300781,
                    20.000137329101562,
                    -92.50015258789062
                ],
                "Up": [
                    3.27825517842939e-07,
                    1.0000009536743164,
                    -4.768373855768004e-07
                ],
                "At": [
                    -7.674089488318714e-07,
                    4.76837158203125e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -55.99969482421875,
                    20.000198364257812,
                    -100.50018310546875
                ],
                "Up": [
                    3.8743016261832963e-07,
                    1.0000009536743164,
                    -4.768373287333816e-07
                ],
                "At": [
                    -7.67409119362128e-07,
                    4.76837158203125e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -55.99964904785156,
                    20.000259399414062,
                    -108.50018310546875
                ],
                "Up": [
                    4.172323713191872e-07,
                    1.0000009536743164,
                    -3.576278970740532e-07
                ],
                "At": [
                    -7.674091762055468e-07,
                    3.5762786865234375e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -63.99964904785156,
                    12.000251770019531,
                    -108.50021362304688
                ],
                "Up": [
                    4.331264733536955e-07,
                    1.0000009536743164,
                    -3.5390266361901013e-07
                ],
                "At": [
                    -1.0,
                    4.331257343892503e-07,
                    -8.781765359344718e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -63.99961853027344,
                    12.000373840332031,
                    -116.50021362304688
                ],
                "Up": [
                    4.3312644493198604e-07,
                    1.0000009536743164,
                    -3.427267927236244e-07
                ],
                "At": [
                    -1.0,
                    4.331257343892503e-07,
                    -8.781765359344718e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -55.99961853027344,
                    12.000434875488281,
                    -116.50021362304688
                ],
                "Up": [
                    5.52335848169605e-07,
                    1.0000009536743164,
                    -3.4272667903678666e-07
                ],
                "At": [
                    -1.0,
                    5.523349955183221e-07,
                    -8.781765927778906e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -47.99961853027344,
                    12.000495910644531,
                    -116.50021362304688
                ],
                "Up": [
                    5.52335848169605e-07,
                    1.0000009536743164,
                    -3.4272667903678666e-07
                ],
                "At": [
                    -1.0,
                    5.523349955183221e-07,
                    -8.781765927778906e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    32.000457763671875,
                    20.000686645507812,
                    -108.50018310546875
                ],
                "Up": [
                    9.099638305087865e-07,
                    1.0000009536743164,
                    -9.313160376223095e-08
                ],
                "At": [
                    -1.0,
                    9.099628641706659e-07,
                    -1.2358043477433966e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    40.00047302246094,
                    20.000747680664062,
                    -108.50018310546875
                ],
                "Up": [
                    9.099638305087865e-07,
                    1.0000009536743164,
                    -8.009308771761425e-08
                ],
                "At": [
                    -1.0,
                    9.099628641706659e-07,
                    -1.2358043477433966e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    48.00041198730469,
                    20.000625610351562,
                    -108.50018310546875
                ],
                "Up": [
                    9.099637168219488e-07,
                    1.0000009536743164,
                    -9.31258981040628e-09
                ],
                "At": [
                    -1.0,
                    9.099628641706659e-07,
                    -1.235804234056559e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -15.999649047851562,
                    20.00042724609375,
                    -116.50015258789062
                ],
                "Up": [
                    5.960459930065554e-07,
                    1.0000009536743164,
                    -2.0663145505750435e-07
                ],
                "At": [
                    1.3430885701382067e-06,
                    -2.0663208033511182e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    64.00032043457031,
                    19.999595642089844,
                    -76.49984741210938
                ],
                "Up": [
                    3.139170701160765e-07,
                    1.0000009536743164,
                    -5.997720222694625e-07
                ],
                "At": [
                    -1.0,
                    3.1391644483846903e-07,
                    -5.205487241255469e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    64.00032043457031,
                    19.999656677246094,
                    -84.49984741210938
                ],
                "Up": [
                    4.331264165102766e-07,
                    1.0000009536743164,
                    -5.699696998817672e-07
                ],
                "At": [
                    -1.0,
                    4.331257343892503e-07,
                    -4.013395198398939e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    64.00035095214844,
                    19.999710083007812,
                    -92.4998779296875
                ],
                "Up": [
                    4.331263880885672e-07,
                    1.0000009536743164,
                    -5.271288614494551e-07
                ],
                "At": [
                    -1.0,
                    4.331257343892503e-07,
                    -4.013394914181845e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    64.00035095214844,
                    19.999771118164062,
                    -100.4998779296875
                ],
                "Up": [
                    4.3312635966685775e-07,
                    1.0000009536743164,
                    -4.805627327186812e-07
                ],
                "At": [
                    -1.0,
                    4.331257343892503e-07,
                    -4.0133946299647505e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    64.00035095214844,
                    19.999832153320312,
                    -108.49990844726562
                ],
                "Up": [
                    5.523356776393484e-07,
                    1.0000009536743164,
                    -4.5076043875269534e-07
                ],
                "At": [
                    -1.0,
                    5.52335052361741e-07,
                    -2.8213023028911266e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    64.00038146972656,
                    19.9998779296875,
                    -116.49990844726562
                ],
                "Up": [
                    5.523356776393484e-07,
                    1.0000009536743164,
                    -4.0978221704790485e-07
                ],
                "At": [
                    -1.0,
                    5.52335052361741e-07,
                    -2.8213020186740323e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -7.9996185302734375,
                    20.00048828125,
                    -116.50015258789062
                ],
                "Up": [
                    5.960459930065554e-07,
                    1.0000009536743164,
                    -2.0663145505750435e-07
                ],
                "At": [
                    1.3430885701382067e-06,
                    -2.0663208033511182e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    0.0003814697265625,
                    20.0006103515625,
                    -116.50021362304688
                ],
                "Up": [
                    8.94068989509833e-07,
                    1.0000009536743164,
                    -8.742166102138071e-08
                ],
                "At": [
                    1.3430886838250444e-06,
                    -8.742277657347586e-08,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    8.000411987304688,
                    20.00048828125,
                    -116.50018310546875
                ],
                "Up": [
                    9.83475956672919e-07,
                    1.0000009536743164,
                    -8.742154022911564e-08
                ],
                "At": [
                    1.3430886838250444e-06,
                    -8.742277657347586e-08,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    56.00041198730469,
                    20.000564575195312,
                    -108.50018310546875
                ],
                "Up": [
                    8.940691600400896e-07,
                    1.0000009536743164,
                    3.178752905341753e-08
                ],
                "At": [
                    1.1046702184103196e-06,
                    3.1786509424591713e-08,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    56.00038146972656,
                    20.000564575195312,
                    -100.50018310546875
                ],
                "Up": [
                    8.940691600400896e-07,
                    1.0000009536743164,
                    3.178752905341753e-08
                ],
                "At": [
                    1.1046702184103196e-06,
                    3.1786509424591713e-08,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    56.00035095214844,
                    20.000625610351562,
                    -92.50018310546875
                ],
                "Up": [
                    8.940697284742782e-07,
                    1.0000009536743164,
                    3.178752905341753e-08
                ],
                "At": [
                    1.1046702184103196e-06,
                    3.1786509424591713e-08,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    56.00035095214844,
                    20.000694274902344,
                    -84.50018310546875
                ],
                "Up": [
                    9.238714255843661e-07,
                    1.0000009536743164,
                    3.1787337206878874e-08
                ],
                "At": [
                    8.662515824653383e-07,
                    3.1786509424591713e-08,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    56.00035095214844,
                    19.999656677246094,
                    -76.49984741210938
                ],
                "Up": [
                    3.894151632266585e-07,
                    1.0000009536743164,
                    -7.152561920520384e-07
                ],
                "At": [
                    6.278327759901003e-07,
                    -7.152557373046875e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    16.000442504882812,
                    20.00054931640625,
                    -116.50021362304688
                ],
                "Up": [
                    9.83475956672919e-07,
                    1.0000009536743164,
                    -8.742154022911564e-08
                ],
                "At": [
                    1.3430886838250444e-06,
                    -8.742277657347586e-08,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    24.000473022460938,
                    20.0006103515625,
                    -116.50021362304688
                ],
                "Up": [
                    9.834758429860813e-07,
                    1.0000009536743164,
                    3.1787863008503336e-08
                ],
                "At": [
                    1.3430887975118821e-06,
                    3.1786509424591713e-08,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    32.00047302246094,
                    20.000732421875,
                    -116.50018310546875
                ],
                "Up": [
                    9.238716529580415e-07,
                    1.0000009536743164,
                    -8.742162549424393e-08
                ],
                "At": [
                    1.3430886838250444e-06,
                    -8.742277657347586e-08,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    40.000518798828125,
                    20.00079345703125,
                    -116.50018310546875
                ],
                "Up": [
                    1.0132781653737766e-06,
                    1.0000009536743164,
                    -8.742149759655149e-08
                ],
                "At": [
                    1.3430886838250444e-06,
                    -8.742277657347586e-08,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    48.00041198730469,
                    20.00067138671875,
                    -116.50018310546875
                ],
                "Up": [
                    9.834758429860813e-07,
                    1.0000009536743164,
                    3.1787863008503336e-08
                ],
                "At": [
                    1.3430887975118821e-06,
                    3.1786509424591713e-08,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    56.00041198730469,
                    20.0006103515625,
                    -116.50021362304688
                ],
                "Up": [
                    9.099637736653676e-07,
                    1.0000009536743164,
                    -1.1175426806175892e-08
                ],
                "At": [
                    -1.0,
                    9.099628641706659e-07,
                    -9.973856549549964e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    48.000396728515625,
                    12.000740051269531,
                    -116.50021362304688
                ],
                "Up": [
                    9.099636599785299e-07,
                    1.0000009536743164,
                    3.166567807966203e-08
                ],
                "At": [
                    -1.0,
                    9.099628641706659e-07,
                    -1.235804234056559e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    40.00059509277344,
                    4.000696182250977,
                    -76.5
                ],
                "Up": [
                    6.25848599611345e-07,
                    1.0000009536743164,
                    -2.0663156874434208e-07
                ],
                "At": [
                    1.1046699910366442e-06,
                    -2.0663208033511182e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    56.00041198730469,
                    12.000679016113281,
                    -116.50021362304688
                ],
                "Up": [
                    9.099637168219488e-07,
                    1.0000009536743164,
                    1.67642610904295e-08
                ],
                "At": [
                    -1.0,
                    9.099628641706659e-07,
                    -9.973856549549964e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    64.00041198730469,
                    12.000740051269531,
                    -116.50021362304688
                ],
                "Up": [
                    8.781772180554981e-07,
                    1.0000009536743164,
                    -1.8620980313244218e-09
                ],
                "At": [
                    1.0,
                    -8.781763654042152e-07,
                    1.1483814432722284e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    64.00038146972656,
                    12.000801086425781,
                    -108.50021362304688
                ],
                "Up": [
                    9.973865644496982e-07,
                    1.0000009536743164,
                    7.451152583826115e-09
                ],
                "At": [
                    1.0,
                    -9.973856549549964e-07,
                    1.029172153721447e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    64.00050354003906,
                    4.000436782836914,
                    -108.499755859375
                ],
                "Up": [
                    5.205490083426412e-07,
                    1.0000009536743164,
                    4.284066790205543e-08
                ],
                "At": [
                    1.0,
                    -5.205485535952903e-07,
                    5.523349955183221e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -63.9996337890625,
                    20.000259399414062,
                    -108.50018310546875
                ],
                "Up": [
                    4.331264733536955e-07,
                    1.0000009536743164,
                    -3.5576528034653165e-07
                ],
                "At": [
                    -1.0,
                    4.331257343892503e-07,
                    -8.781765359344718e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -63.99969482421875,
                    20.000259399414062,
                    -100.50018310546875
                ],
                "Up": [
                    4.331265017754049e-07,
                    1.0000009536743164,
                    -3.855676311559364e-07
                ],
                "At": [
                    -1.0,
                    4.331257343892503e-07,
                    -8.781765927778906e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -63.99969482421875,
                    20.000137329101562,
                    -92.50015258789062
                ],
                "Up": [
                    4.3312653019711433e-07,
                    1.0000009536743164,
                    -4.2282053414055554e-07
                ],
                "At": [
                    -1.0,
                    4.331257343892503e-07,
                    -8.781765927778906e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -63.99974060058594,
                    20.000083923339844,
                    -76.50006103515625
                ],
                "Up": [
                    3.139170701160765e-07,
                    1.0000009536743164,
                    -4.805627327186812e-07
                ],
                "At": [
                    -1.0,
                    3.1391644483846903e-07,
                    -6.397579568329093e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -63.99967956542969,
                    20.000144958496094,
                    -84.50015258789062
                ],
                "Up": [
                    3.1391712695949536e-07,
                    1.0000009536743164,
                    -4.190953291072219e-07
                ],
                "At": [
                    -1.0,
                    3.1391644483846903e-07,
                    -8.781765359344718e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -23.999740600585938,
                    11.999542236328125,
                    -60.50006103515625
                ],
                "Up": [
                    1.947076384567481e-07,
                    1.0000009536743164,
                    -5.438927246359526e-07
                ],
                "At": [
                    -1.0,
                    1.9470715528768778e-07,
                    -5.20548667282128e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -31.999740600585938,
                    11.999542236328125,
                    -60.50006103515625
                ],
                "Up": [
                    3.1391709853778593e-07,
                    1.0000009536743164,
                    -5.140902885614196e-07
                ],
                "At": [
                    -1.0,
                    3.1391644483846903e-07,
                    -6.397580136763281e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -39.99974060058594,
                    11.999603271484375,
                    -60.50006103515625
                ],
                "Up": [
                    3.1391721222462365e-07,
                    1.0000009536743164,
                    -5.178155220164626e-07
                ],
                "At": [
                    -1.0,
                    3.1391644483846903e-07,
                    -8.781765927778906e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -47.99974060058594,
                    11.999603271484375,
                    -60.50006103515625
                ],
                "Up": [
                    3.139172690680425e-07,
                    1.0000009536743164,
                    -5.327166263668914e-07
                ],
                "At": [
                    -1.0,
                    3.139164164167596e-07,
                    -9.973858823286719e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -63.99974060058594,
                    12.000030517578125,
                    -60.5001220703125
                ],
                "Up": [
                    2.682209014892578e-07,
                    1.0000009536743164,
                    -4.450508299669309e-07
                ],
                "At": [
                    8.662514119350817e-07,
                    -4.450506310149649e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -55.999725341796875,
                    11.999603271484375,
                    -60.50006103515625
                ],
                "Up": [
                    4.172324281626061e-07,
                    1.0000009536743164,
                    -4.768372150465439e-07
                ],
                "At": [
                    -1.0207281775365118e-06,
                    4.76837158203125e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -23.999496459960938,
                    4.000091552734375,
                    -60.499969482421875
                ],
                "Up": [
                    2.0861610039446532e-07,
                    1.0000009536743164,
                    -3.5762798233918147e-07
                ],
                "At": [
                    -1.1548387419679784e-06,
                    3.5762786865234375e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -31.999465942382812,
                    4.000213623046875,
                    -60.49993896484375
                ],
                "Up": [
                    2.0861610039446532e-07,
                    1.0000009536743164,
                    -3.5762798233918147e-07
                ],
                "At": [
                    -1.1250363058934454e-06,
                    3.5762786865234375e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -39.999481201171875,
                    4.000274658203125,
                    -60.49993896484375
                ],
                "Up": [
                    2.0861610039446532e-07,
                    1.0000009536743164,
                    -3.5762798233918147e-07
                ],
                "At": [
                    -1.087783516595664e-06,
                    3.5762786865234375e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -47.99949645996094,
                    4.000274658203125,
                    -60.49993896484375
                ],
                "Up": [
                    2.086160719727559e-07,
                    1.0000009536743164,
                    -3.5762798233918147e-07
                ],
                "At": [
                    -1.0579813078948064e-06,
                    3.5762786865234375e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -55.99971008300781,
                    3.999605178833008,
                    -60.500091552734375
                ],
                "Up": [
                    4.470347505503014e-07,
                    1.0000009536743164,
                    -4.76837158203125e-07
                ],
                "At": [
                    -1.0132778243132634e-06,
                    4.76837158203125e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -63.99971008300781,
                    3.999605178833008,
                    -60.5001220703125
                ],
                "Up": [
                    4.7683710135970614e-07,
                    1.0000009536743164,
                    -4.76837158203125e-07
                ],
                "At": [
                    -9.685742270448827e-07,
                    4.76837158203125e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -47.99967956542969,
                    20.000259399414062,
                    -108.50018310546875
                ],
                "Up": [
                    4.331264733536955e-07,
                    1.0000009536743164,
                    -3.501773448988388e-07
                ],
                "At": [
                    -1.0,
                    4.331257343892503e-07,
                    -8.781765359344718e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -63.99876403808594,
                    4.000272750854492,
                    -68.500244140625
                ],
                "Up": [
                    2.44379020841734e-06,
                    1.0000009536743164,
                    9.854657037067227e-07
                ],
                "At": [
                    1.5815097640370368e-06,
                    9.854609288595384e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    64.00038146972656,
                    12.001007080078125,
                    -68.500244140625
                ],
                "Up": [
                    9.973865644496982e-07,
                    1.0000009536743164,
                    3.5391053643252235e-08
                ],
                "At": [
                    1.0,
                    -9.973856549549964e-07,
                    1.2675907328230096e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -39.9996337890625,
                    20.000442504882812,
                    -108.50018310546875
                ],
                "Up": [
                    5.52335848169605e-07,
                    1.0000009536743164,
                    -2.5518212964925624e-07
                ],
                "At": [
                    -1.0,
                    5.523349955183221e-07,
                    -1.355013637294178e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -31.999649047851562,
                    20.000503540039062,
                    -108.50015258789062
                ],
                "Up": [
                    5.523357913261862e-07,
                    1.0000009536743164,
                    -2.2724242398908245e-07
                ],
                "At": [
                    -1.0,
                    5.523349955183221e-07,
                    -1.355013637294178e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -23.999679565429688,
                    20.000442504882812,
                    -108.5001220703125
                ],
                "Up": [
                    5.523357913261862e-07,
                    1.0000009536743164,
                    -2.2351716211232997e-07
                ],
                "At": [
                    -1.0,
                    5.523349955183221e-07,
                    -1.355013637294178e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -15.999679565429688,
                    20.000442504882812,
                    -108.50015258789062
                ],
                "Up": [
                    5.523357913261862e-07,
                    1.0000009536743164,
                    -2.2351716211232997e-07
                ],
                "At": [
                    -1.0,
                    5.523349955183221e-07,
                    -1.355013637294178e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -63.99980163574219,
                    12.000579833984375,
                    -68.50021362304688
                ],
                "Up": [
                    9.099639441956242e-07,
                    1.0000009536743164,
                    -1.2479577549129317e-07
                ],
                "At": [
                    -1.0,
                    9.09962807327247e-07,
                    -2.0702693745988654e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -7.9996490478515625,
                    20.000503540039062,
                    -108.50015258789062
                ],
                "Up": [
                    5.523357913261862e-07,
                    1.0000009536743164,
                    -2.2351716211232997e-07
                ],
                "At": [
                    -1.0,
                    5.523349955183221e-07,
                    -1.355013637294178e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    0.0003662109375,
                    20.000564575195312,
                    -108.50021362304688
                ],
                "Up": [
                    9.099638873522053e-07,
                    1.0000009536743164,
                    -1.3969770407129545e-07
                ],
                "At": [
                    -1.0,
                    9.099628641706659e-07,
                    -1.2358043477433966e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    8.000411987304688,
                    20.000503540039062,
                    -108.50018310546875
                ],
                "Up": [
                    9.099638305087865e-07,
                    1.0000009536743164,
                    -1.0617009138513822e-07
                ],
                "At": [
                    -1.0,
                    9.099628641706659e-07,
                    -1.2358043477433966e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    16.00042724609375,
                    20.000625610351562,
                    -108.50015258789062
                ],
                "Up": [
                    9.099638305087865e-07,
                    1.0000009536743164,
                    -1.0617014822855708e-07
                ],
                "At": [
                    -1.0,
                    9.099628641706659e-07,
                    -1.2358043477433966e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    24.000442504882812,
                    20.000625610351562,
                    -108.50018310546875
                ],
                "Up": [
                    1.0291732905898243e-06,
                    1.0000009536743164,
                    -7.45050314776563e-08
                ],
                "At": [
                    -1.0,
                    1.0291722674082848e-06,
                    -1.2358043477433966e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    64.00047302246094,
                    4.000516891479492,
                    -68.49969482421875
                ],
                "Up": [
                    3.874300205097825e-07,
                    1.0000009536743164,
                    -2.0663210875682125e-07
                ],
                "At": [
                    3.8941431057537557e-07,
                    -2.0663208033511182e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    56.00053405761719,
                    4.000494003295898,
                    -116.49972534179688
                ],
                "Up": [
                    7.589678148178791e-07,
                    1.0000009536743164,
                    5.0291369291244337e-08
                ],
                "At": [
                    1.0,
                    -7.589671326968528e-07,
                    5.52335052361741e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    48.00065612792969,
                    4.000555038452148,
                    -116.49984741210938
                ],
                "Up": [
                    1.0291729495293112e-06,
                    1.0000009536743164,
                    2.421443241473753e-07
                ],
                "At": [
                    -1.0,
                    1.0291722674082848e-06,
                    -8.781761948739586e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    64.00038146972656,
                    12.000946044921875,
                    -60.500213623046875
                ],
                "Up": [
                    8.642668376523943e-07,
                    1.0000009536743164,
                    3.178749352628074e-08
                ],
                "At": [
                    1.1046702184103196e-06,
                    3.1786509424591713e-08,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    56.00038146972656,
                    12.000946044921875,
                    -60.500244140625
                ],
                "Up": [
                    9.238711413672718e-07,
                    1.0000009536743164,
                    3.1787777743375045e-08
                ],
                "At": [
                    1.3430887975118821e-06,
                    3.1786509424591713e-08,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    48.0003662109375,
                    12.001007080078125,
                    -60.500244140625
                ],
                "Up": [
                    9.973864507628605e-07,
                    1.0000009536743164,
                    7.078156016859793e-08
                ],
                "At": [
                    1.0,
                    -9.973855412681587e-07,
                    1.506009311924572e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    40.00016784667969,
                    11.999847412109375,
                    -60.4998779296875
                ],
                "Up": [
                    1.6292153759422945e-07,
                    1.0000009536743164,
                    -5.941840299783507e-07
                ],
                "At": [
                    1.0,
                    -1.6292062809952768e-07,
                    1.2675908465098473e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    40.00013732910156,
                    3.999910354614258,
                    -60.4998779296875
                ],
                "Up": [
                    1.6292150917252002e-07,
                    1.0000009536743164,
                    -5.792828687845031e-07
                ],
                "At": [
                    1.0,
                    -1.6292062809952768e-07,
                    1.2675908465098473e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    48.000152587890625,
                    3.999971389770508,
                    -60.4998779296875
                ],
                "Up": [
                    1.6292163707021246e-07,
                    1.0000009536743164,
                    -5.792828687845031e-07
                ],
                "At": [
                    1.0,
                    -1.6292061388867296e-07,
                    1.5060094256114098e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    56.00016784667969,
                    3.999971389770508,
                    -60.4998779296875
                ],
                "Up": [
                    1.6292170812448603e-07,
                    1.0000009536743164,
                    -5.774201667918533e-07
                ],
                "At": [
                    1.0,
                    -1.6292061388867296e-07,
                    1.625218715162191e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    64.00016784667969,
                    3.999910354614258,
                    -60.499847412109375
                ],
                "Up": [
                    2.8213108294039557e-07,
                    1.0000009536743164,
                    -5.289911655381729e-07
                ],
                "At": [
                    1.0,
                    -2.821298892285995e-07,
                    1.74442811839981e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    40.00065612792969,
                    4.000494003295898,
                    -116.4998779296875
                ],
                "Up": [
                    1.0291729495293112e-06,
                    1.0000009536743164,
                    2.682213562366087e-07
                ],
                "At": [
                    -1.0,
                    1.0291722674082848e-06,
                    -8.781761380305397e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    32.00068664550781,
                    4.000555038452148,
                    -116.49990844726562
                ],
                "Up": [
                    1.0291729495293112e-06,
                    1.0000009536743164,
                    3.0919954951968975e-07
                ],
                "At": [
                    -1.0,
                    1.0291722674082848e-06,
                    -8.781761380305397e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    24.000686645507812,
                    4.000677108764648,
                    -116.49990844726562
                ],
                "Up": [
                    1.0291729495293112e-06,
                    1.0000009536743164,
                    2.9243585686344886e-07
                ],
                "At": [
                    -1.0,
                    1.0291722674082848e-06,
                    -9.973853138944833e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    16.000717163085938,
                    4.000555038452148,
                    -116.49993896484375
                ],
                "Up": [
                    1.2675916423177114e-06,
                    1.0000009536743164,
                    3.7066590152790013e-07
                ],
                "At": [
                    -1.0,
                    1.2675908465098473e-06,
                    -8.781759675002832e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    32.00067138671875,
                    4.000619888305664,
                    -108.49990844726562
                ],
                "Up": [
                    1.116595626626804e-06,
                    1.0000009536743164,
                    3.352767237174703e-07
                ],
                "At": [
                    1.0,
                    -1.1165949445057777e-06,
                    9.099625799535715e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    64.00053405761719,
                    4.000432968139648,
                    -116.49972534179688
                ],
                "Up": [
                    6.397584115802601e-07,
                    1.0000009536743164,
                    4.6566015043936204e-08
                ],
                "At": [
                    1.0,
                    -6.397578431460715e-07,
                    5.523349955183221e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    8.000762939453125,
                    4.000555038452148,
                    -116.49996948242188
                ],
                "Up": [
                    1.116595626626804e-06,
                    1.0000009536743164,
                    5.010519998904783e-07
                ],
                "At": [
                    1.0,
                    -1.1165949445057777e-06,
                    7.907530630291149e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    0.0003509521484375,
                    4.000616073608398,
                    -116.50015258789062
                ],
                "Up": [
                    6.397586389539356e-07,
                    1.0000009536743164,
                    -1.7695077758617117e-07
                ],
                "At": [
                    1.0,
                    -6.397577863026527e-07,
                    1.5060094256114098e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -7.9996337890625,
                    4.000677108764648,
                    -116.50015258789062
                ],
                "Up": [
                    6.397586389539356e-07,
                    1.0000009536743164,
                    -1.4714845519847586e-07
                ],
                "At": [
                    1.0,
                    -6.397577863026527e-07,
                    1.5060094256114098e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -15.999618530273438,
                    4.000738143920898,
                    -116.50015258789062
                ],
                "Up": [
                    6.397586389539356e-07,
                    1.0000009536743164,
                    -1.4901110034770682e-07
                ],
                "At": [
                    1.0,
                    -6.397577863026527e-07,
                    1.5060094256114098e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -23.999160766601562,
                    4.000555038452148,
                    -116.50009155273438
                ],
                "Up": [
                    1.3550142057283665e-06,
                    1.0000009536743164,
                    6.649651140833157e-07
                ],
                "At": [
                    1.0,
                    -1.3550135236073402e-06,
                    9.099620115193829e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -31.9991455078125,
                    4.000494003295898,
                    -116.5001220703125
                ],
                "Up": [
                    1.3550142057283665e-06,
                    1.0000009536743164,
                    6.761398481103242e-07
                ],
                "At": [
                    1.0,
                    -1.3550135236073402e-06,
                    9.099620115193829e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -39.99913024902344,
                    4.000494003295898,
                    -116.5001220703125
                ],
                "Up": [
                    1.4742234952791478e-06,
                    1.0000009536743164,
                    7.227073979265697e-07
                ],
                "At": [
                    1.0,
                    -1.4742228131581214e-06,
                    1.0291712442267453e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -47.9991455078125,
                    4.000494003295898,
                    -116.50015258789062
                ],
                "Up": [
                    1.47422338159231e-06,
                    1.0000009536743164,
                    7.674108815081127e-07
                ],
                "At": [
                    1.0,
                    -1.4742228131581214e-06,
                    1.0291711305399076e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -55.9991455078125,
                    4.000555038452148,
                    -116.50015258789062
                ],
                "Up": [
                    1.47422338159231e-06,
                    1.0000009536743164,
                    7.394712042696483e-07
                ],
                "At": [
                    1.0,
                    -1.4742228131581214e-06,
                    1.0291711305399076e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -63.99916076660156,
                    4.000616073608398,
                    -116.50015258789062
                ],
                "Up": [
                    1.47422338159231e-06,
                    1.0000009536743164,
                    7.692736403441813e-07
                ],
                "At": [
                    1.0,
                    -1.4742228131581214e-06,
                    1.0291711305399076e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -63.998992919921875,
                    4.000436782836914,
                    -108.50021362304688
                ],
                "Up": [
                    2.1159630705369636e-06,
                    1.0000009536743164,
                    9.536780680718948e-07
                ],
                "At": [
                    -1.370905351905094e-06,
                    -9.536742027194123e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -63.9990234375,
                    4.00050163269043,
                    -100.50021362304688
                ],
                "Up": [
                    2.1020564417995047e-06,
                    1.0000009536743164,
                    9.555363931212923e-07
                ],
                "At": [
                    -1.0,
                    2.1020557596784784e-06,
                    -1.4742208804818802e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -63.99888610839844,
                    4.000322341918945,
                    -92.50021362304688
                ],
                "Up": [
                    2.2212659587239614e-06,
                    1.000001072883606,
                    9.834797083385638e-07
                ],
                "At": [
                    -1.0,
                    2.2212650492292596e-06,
                    -1.4742206531082047e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -63.99885559082031,
                    4.000265121459961,
                    -84.50027465820312
                ],
                "Up": [
                    2.3404752482747426e-06,
                    1.0000009536743164,
                    9.555400311000994e-07
                ],
                "At": [
                    -1.0,
                    2.340474338780041e-06,
                    -1.4742206531082047e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -63.998870849609375,
                    4.000329971313477,
                    -76.500244140625
                ],
                "Up": [
                    2.340475020901067e-06,
                    1.0000009536743164,
                    9.499527777734329e-07
                ],
                "At": [
                    -1.0,
                    2.340474338780041e-06,
                    -1.7126392322097672e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -55.99885559082031,
                    4.000329971313477,
                    -76.500244140625
                ],
                "Up": [
                    2.340475020901067e-06,
                    1.0000009536743164,
                    9.480901326242019e-07
                ],
                "At": [
                    -1.0,
                    2.340474338780041e-06,
                    -1.7126392322097672e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -55.99885559082031,
                    4.000326156616211,
                    -84.500244140625
                ],
                "Up": [
                    2.340475020901067e-06,
                    1.0000009536743164,
                    9.536778406982194e-07
                ],
                "At": [
                    -1.0,
                    2.340474338780041e-06,
                    -1.7126392322097672e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -55.99885559082031,
                    4.000322341918945,
                    -92.50018310546875
                ],
                "Up": [
                    2.2212659587239614e-06,
                    1.000001072883606,
                    9.983808695324115e-07
                ],
                "At": [
                    -1.0,
                    2.2212650492292596e-06,
                    -1.4742206531082047e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -47.99885559082031,
                    4.000322341918945,
                    -92.50018310546875
                ],
                "Up": [
                    2.2212659587239614e-06,
                    1.000001072883606,
                    9.983808695324115e-07
                ],
                "At": [
                    -1.0,
                    2.2212650492292596e-06,
                    -1.4742206531082047e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -47.99885559082031,
                    4.000326156616211,
                    -84.50018310546875
                ],
                "Up": [
                    2.340475020901067e-06,
                    1.0000009536743164,
                    1.037496645039937e-06
                ],
                "At": [
                    -1.0,
                    2.340474338780041e-06,
                    -1.5934297152853105e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -47.99885559082031,
                    4.000329971313477,
                    -76.500244140625
                ],
                "Up": [
                    2.340475020901067e-06,
                    1.0000009536743164,
                    9.406353456142824e-07
                ],
                "At": [
                    -1.0,
                    2.340474338780041e-06,
                    -1.7126392322097672e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -47.99885559082031,
                    4.000394821166992,
                    -68.50021362304688
                ],
                "Up": [
                    2.3404747935273917e-06,
                    1.0000009536743164,
                    9.853431492956588e-07
                ],
                "At": [
                    -1.0,
                    2.340474338780041e-06,
                    -1.8318484080737107e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -55.99970245361328,
                    3.9995949268341064,
                    -68.50006103515625
                ],
                "Up": [
                    5.205495767768298e-07,
                    1.0000009536743164,
                    -5.066390258434694e-07
                ],
                "At": [
                    1.0,
                    -5.205484967518714e-07,
                    1.1483817843327415e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_W_STA",
                "UserData": 51,
                "Position": [
                    -23.999435424804688,
                    4.000333786010742,
                    -68.49996948242188
                ],
                "Up": [
                    1.9470769530016696e-07,
                    1.0000009536743164,
                    -3.315510639367858e-07
                ],
                "At": [
                    -1.0,
                    1.9470714107683307e-07,
                    -1.1165950581926154e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -39.99945068359375,
                    4.000329971313477,
                    -76.49996948242188
                ],
                "Up": [
                    3.139170701160765e-07,
                    1.0000009536743164,
                    -3.222377529255027e-07
                ],
                "At": [
                    -1.0,
                    3.139164164167596e-07,
                    -9.973857686418341e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -31.999465942382812,
                    4.000329971313477,
                    -76.49996948242188
                ],
                "Up": [
                    3.1391704169436707e-07,
                    1.0000009536743164,
                    -3.0733659173165506e-07
                ],
                "At": [
                    -1.0,
                    3.139164164167596e-07,
                    -9.973857686418341e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -31.999435424804688,
                    4.000272750854492,
                    -68.49996948242188
                ],
                "Up": [
                    1.9470770951102168e-07,
                    1.0000009536743164,
                    -3.445895799814025e-07
                ],
                "At": [
                    -1.0,
                    1.9470714107683307e-07,
                    -1.1165950581926154e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    24.000198364257812,
                    3.999783515930176,
                    -68.4998779296875
                ],
                "Up": [
                    1.1920940323761897e-07,
                    1.0000009536743164,
                    -5.960469025012571e-07
                ],
                "At": [
                    -1.0803330496855779e-06,
                    5.960464477539062e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -23.999481201171875,
                    4.000329971313477,
                    -76.49996948242188
                ],
                "Up": [
                    3.1391701327265764e-07,
                    1.0000009536743164,
                    -2.756716241947288e-07
                ],
                "At": [
                    -1.0,
                    3.139164164167596e-07,
                    -9.973857686418341e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -15.999435424804688,
                    4.000391006469727,
                    -76.49996948242188
                ],
                "Up": [
                    4.331264165102766e-07,
                    1.0000009536743164,
                    -2.7194622020942916e-07
                ],
                "At": [
                    -1.0,
                    4.3312570596754085e-07,
                    -9.973857686418341e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -39.99946594238281,
                    4.000333786010742,
                    -68.49996948242188
                ],
                "Up": [
                    2.0861604355104646e-07,
                    1.0000009536743164,
                    -3.2584142672931193e-07
                ],
                "At": [
                    1.104670104723482e-06,
                    -3.2584134146418364e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -7.9994659423828125,
                    4.000150680541992,
                    -68.49990844726562
                ],
                "Up": [
                    1.947078231978594e-07,
                    1.0000009536743164,
                    -4.09782160204486e-07
                ],
                "At": [
                    -1.0,
                    1.9470712686597835e-07,
                    -1.2358043477433966e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -7.9994354248046875,
                    4.000391006469727,
                    -76.5
                ],
                "Up": [
                    4.331264165102766e-07,
                    1.0000009536743164,
                    -2.7008354663848877e-07
                ],
                "At": [
                    -1.0,
                    4.3312570596754085e-07,
                    -9.973857686418341e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    0.0005645751953125,
                    4.000391006469727,
                    -76.5
                ],
                "Up": [
                    4.331263880885672e-07,
                    1.0000009536743164,
                    -2.3469331722481002e-07
                ],
                "At": [
                    -1.0,
                    4.3312570596754085e-07,
                    -9.973857686418341e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    0.000518798828125,
                    4.000211715698242,
                    -68.49993896484375
                ],
                "Up": [
                    1.947078231978594e-07,
                    1.0000009536743164,
                    -4.09782160204486e-07
                ],
                "At": [
                    -1.0,
                    1.9470712686597835e-07,
                    -1.2358043477433966e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    8.000442504882812,
                    4.000211715698242,
                    -68.49996948242188
                ],
                "Up": [
                    1.947075389807651e-07,
                    1.0000009536743164,
                    -2.9988621008669725e-07
                ],
                "At": [
                    -1.0,
                    1.9470715528768778e-07,
                    -6.397578999894904e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    8.000579833984375,
                    4.000452041625977,
                    -76.5
                ],
                "Up": [
                    5.523357344827673e-07,
                    1.0000009536743164,
                    -2.0302826442275546e-07
                ],
                "At": [
                    -1.0,
                    5.523349955183221e-07,
                    -9.973857686418341e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    16.000595092773438,
                    4.000513076782227,
                    -76.5
                ],
                "Up": [
                    5.523356776393484e-07,
                    1.0000009536743164,
                    -1.6950068015830766e-07
                ],
                "At": [
                    -1.0,
                    5.523349955183221e-07,
                    -9.973857686418341e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    16.000442504882812,
                    4.000150680541992,
                    -68.5001220703125
                ],
                "Up": [
                    1.9470762424589338e-07,
                    1.0000009536743164,
                    -3.2223786661234044e-07
                ],
                "At": [
                    -1.0,
                    1.9470714107683307e-07,
                    -8.781764790910529e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    24.000579833984375,
                    4.000513076782227,
                    -76.49996948242188
                ],
                "Up": [
                    5.523356776393484e-07,
                    1.0000009536743164,
                    -1.4901152667334827e-07
                ],
                "At": [
                    -1.0,
                    5.523349955183221e-07,
                    -9.973857686418341e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_W_STA",
                "UserData": 51,
                "Position": [
                    40.00018310546875,
                    4.000089645385742,
                    -68.4998779296875
                ],
                "Up": [
                    1.6292160864850302e-07,
                    1.0000009536743164,
                    -5.234034574641555e-07
                ],
                "At": [
                    1.0,
                    -1.6292061388867296e-07,
                    1.625218715162191e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    8.000274658203125,
                    19.999595642089844,
                    -68.49996948242188
                ],
                "Up": [
                    1.7881393432617188e-07,
                    1.0000009536743164,
                    -4.4505094365376863e-07
                ],
                "At": [
                    6.278328896769381e-07,
                    -4.450506310149649e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    32.000579833984375,
                    4.000513076782227,
                    -76.5
                ],
                "Up": [
                    5.523356776393484e-07,
                    1.0000009536743164,
                    -1.4528629321830522e-07
                ],
                "At": [
                    -1.0,
                    5.523349955183221e-07,
                    -8.781764790910529e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_W_STA",
                "UserData": 51,
                "Position": [
                    -7.9997406005859375,
                    11.999664306640625,
                    -68.49996948242188
                ],
                "Up": [
                    1.947077237218764e-07,
                    1.0000009536743164,
                    -5.010518293602217e-07
                ],
                "At": [
                    -1.0,
                    1.9470715528768778e-07,
                    -7.589671895402716e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_DOOR_A",
                "UserData": 51,
                "Position": [
                    -31.999481201171875,
                    4.000213623046875,
                    -64.49996948242188
                ],
                "Up": [
                    2.0861610039446532e-07,
                    1.0000009536743164,
                    -3.5762798233918147e-07
                ],
                "At": [
                    -1.1250363058934454e-06,
                    3.5762786865234375e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    48.00018310546875,
                    4.000028610229492,
                    -68.4998779296875
                ],
                "Up": [
                    1.9470812162580842e-07,
                    1.0000009536743164,
                    -5.494804895533889e-07
                ],
                "At": [
                    -1.0,
                    1.9470711265512364e-07,
                    -1.4742229268449591e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    48.00059509277344,
                    4.000635147094727,
                    -76.5
                ],
                "Up": [
                    5.523356776393484e-07,
                    1.0000009536743164,
                    -1.4528629321830522e-07
                ],
                "At": [
                    -1.0,
                    5.523349955183221e-07,
                    -8.781764790910529e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    56.00016784667969,
                    3.999966621398926,
                    -68.49990844726562
                ],
                "Up": [
                    3.1391766697197454e-07,
                    1.0000009536743164,
                    -5.494802621797135e-07
                ],
                "At": [
                    -1.0,
                    3.1391638799505017e-07,
                    -1.7126416196333594e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    56.00062561035156,
                    4.000696182250977,
                    -76.5
                ],
                "Up": [
                    5.523356776393484e-07,
                    1.0000009536743164,
                    -1.4528629321830522e-07
                ],
                "At": [
                    -1.0,
                    5.523349955183221e-07,
                    -8.781764790910529e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    64.00044250488281,
                    4.000452041625977,
                    -76.49969482421875
                ],
                "Up": [
                    4.3312627440172946e-07,
                    1.0000009536743164,
                    -1.7136363794634235e-07
                ],
                "At": [
                    -1.0,
                    4.331257343892503e-07,
                    -5.205486104387091e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    64.00047302246094,
                    4.000509262084961,
                    -84.49972534179688
                ],
                "Up": [
                    5.523356207959296e-07,
                    1.0000009536743164,
                    -1.378359115733474e-07
                ],
                "At": [
                    -1.0,
                    5.52335052361741e-07,
                    -5.205486104387091e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    64.00047302246094,
                    4.000444412231445,
                    -92.49972534179688
                ],
                "Up": [
                    3.8742999208807305e-07,
                    1.0000009536743164,
                    1.7053025658242404e-13
                ],
                "At": [
                    -4.321332482959406e-07,
                    0.0,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    64.00047302246094,
                    4.00044059753418,
                    -100.49972534179688
                ],
                "Up": [
                    3.874299636663636e-07,
                    1.0000009536743164,
                    1.7053025658242404e-13
                ],
                "At": [
                    -4.321332482959406e-07,
                    0.0,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    56.00062561035156,
                    4.000814437866211,
                    -84.5
                ],
                "Up": [
                    5.960460498499742e-07,
                    1.0000009536743164,
                    -1.19208827698003e-07
                ],
                "At": [
                    -9.611237601347966e-07,
                    1.1920928955078125e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    56.00065612792969,
                    4.000871658325195,
                    -92.50003051757812
                ],
                "Up": [
                    5.960461066933931e-07,
                    1.0000009536743164,
                    -1.19208827698003e-07
                ],
                "At": [
                    -9.611237601347966e-07,
                    1.1920928955078125e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    56.00068664550781,
                    4.00092887878418,
                    -100.50003051757812
                ],
                "Up": [
                    5.960461066933931e-07,
                    1.0000009536743164,
                    -1.19208827698003e-07
                ],
                "At": [
                    -9.611237601347966e-07,
                    1.1920928955078125e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    56.00065612792969,
                    4.000986099243164,
                    -108.50006103515625
                ],
                "Up": [
                    5.960460498499742e-07,
                    1.0000009536743164,
                    -1.19208827698003e-07
                ],
                "At": [
                    -9.611237601347966e-07,
                    1.1920928955078125e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    48.00065612792969,
                    4.001047134399414,
                    -108.50006103515625
                ],
                "Up": [
                    6.397585252670979e-07,
                    1.0000009536743164,
                    -8.009353535953778e-08
                ],
                "At": [
                    1.0,
                    -6.397577863026527e-07,
                    1.0291722674082848e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    40.00067138671875,
                    4.000558853149414,
                    -108.4998779296875
                ],
                "Up": [
                    1.1165957403136417e-06,
                    1.0000009536743164,
                    2.9243585686344886e-07
                ],
                "At": [
                    1.0,
                    -1.1165949445057777e-06,
                    9.099625799535715e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    24.00067138671875,
                    4.000680923461914,
                    -108.49990844726562
                ],
                "Up": [
                    1.116595626626804e-06,
                    1.0000009536743164,
                    3.352767237174703e-07
                ],
                "At": [
                    1.0,
                    -1.1165949445057777e-06,
                    9.099625799535715e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    16.000717163085938,
                    4.000558853149414,
                    -108.49993896484375
                ],
                "Up": [
                    1.235805029864423e-06,
                    1.0000009536743164,
                    3.892937741056812e-07
                ],
                "At": [
                    1.0,
                    -1.235804234056559e-06,
                    1.0291716989740962e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    8.000732421875,
                    4.000619888305664,
                    -108.49993896484375
                ],
                "Up": [
                    1.3550143194152042e-06,
                    1.0000009536743164,
                    4.079202255979908e-07
                ],
                "At": [
                    1.0,
                    -1.3550135236073402e-06,
                    1.0291716989740962e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    0.0003509521484375,
                    4.000619888305664,
                    -108.50015258789062
                ],
                "Up": [
                    6.397586389539356e-07,
                    1.0000009536743164,
                    -1.5087374549693777e-07
                ],
                "At": [
                    1.0,
                    -6.397577863026527e-07,
                    1.5060094256114098e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -7.9996490478515625,
                    4.000741958618164,
                    -108.50015258789062
                ],
                "Up": [
                    6.397585821105167e-07,
                    1.0000009536743164,
                    -1.2107142310924246e-07
                ],
                "At": [
                    1.0,
                    -6.397577863026527e-07,
                    1.5060094256114098e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -15.999649047851562,
                    4.000802993774414,
                    -108.50015258789062
                ],
                "Up": [
                    6.397585821105167e-07,
                    1.0000009536743164,
                    -1.2107142310924246e-07
                ],
                "At": [
                    1.0,
                    -6.397577863026527e-07,
                    1.5060094256114098e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -23.999160766601562,
                    4.000619888305664,
                    -108.50009155273438
                ],
                "Up": [
                    1.3550142057283665e-06,
                    1.0000009536743164,
                    6.463387762778439e-07
                ],
                "At": [
                    1.0,
                    -1.3550135236073402e-06,
                    9.099620683628018e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -31.999191284179688,
                    4.000619888305664,
                    -108.5001220703125
                ],
                "Up": [
                    1.3550142057283665e-06,
                    1.0000009536743164,
                    6.835915655756253e-07
                ],
                "At": [
                    1.0,
                    -1.3550135236073402e-06,
                    9.099620115193829e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -39.99916076660156,
                    4.000558853149414,
                    -108.5001220703125
                ],
                "Up": [
                    1.4742234952791478e-06,
                    1.0000009536743164,
                    7.15256760486227e-07
                ],
                "At": [
                    1.0,
                    -1.4742228131581214e-06,
                    1.0291712442267453e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -47.99916076660156,
                    4.000558853149414,
                    -108.50015258789062
                ],
                "Up": [
                    1.4742236089659855e-06,
                    1.000001072883606,
                    7.357460276580241e-07
                ],
                "At": [
                    1.0,
                    -1.4742228131581214e-06,
                    1.0291711305399076e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -55.99916076660156,
                    4.000558853149414,
                    -108.5001220703125
                ],
                "Up": [
                    1.4742234952791478e-06,
                    1.0000009536743164,
                    7.487842594855465e-07
                ],
                "At": [
                    1.0,
                    -1.4742228131581214e-06,
                    9.099618409891264e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -55.99900817871094,
                    4.00056266784668,
                    -100.50021362304688
                ],
                "Up": [
                    2.1457681214087643e-06,
                    1.000001072883606,
                    9.85464794212021e-07
                ],
                "At": [
                    1.3430909575617989e-06,
                    9.854609288595384e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -47.99885559082031,
                    4.00031852722168,
                    -100.50018310546875
                ],
                "Up": [
                    2.2649733182333875e-06,
                    1.0000009536743164,
                    9.854653626462095e-07
                ],
                "At": [
                    1.581509650350199e-06,
                    9.854609288595384e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -39.999176025390625,
                    4.00056266784668,
                    -100.5001220703125
                ],
                "Up": [
                    1.5060101077324362e-06,
                    1.0000009536743164,
                    7.227073410831508e-07
                ],
                "At": [
                    -1.0,
                    1.5060094256114098e-06,
                    -9.97384631773457e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -39.99885559082031,
                    4.000322341918945,
                    -92.50018310546875
                ],
                "Up": [
                    2.2212659587239614e-06,
                    1.000001072883606,
                    9.983808695324115e-07
                ],
                "At": [
                    -1.0,
                    2.2212650492292596e-06,
                    -1.4742206531082047e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -39.99884033203125,
                    4.000326156616211,
                    -84.50015258789062
                ],
                "Up": [
                    2.340475020901067e-06,
                    1.0000009536743164,
                    1.017004024106427e-06
                ],
                "At": [
                    -1.0,
                    2.340474338780041e-06,
                    -1.5934298289721482e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -31.999221801757812,
                    4.00062370300293,
                    -100.5001220703125
                ],
                "Up": [
                    1.3868007044948172e-06,
                    1.0000009536743164,
                    6.947675501578487e-07
                ],
                "At": [
                    -1.0,
                    1.3868001360606286e-06,
                    -9.973847454602947e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -23.999465942382812,
                    4.000448226928711,
                    -84.5
                ],
                "Up": [
                    4.331263880885672e-07,
                    1.0000009536743164,
                    -2.440065429709648e-07
                ],
                "At": [
                    -1.0,
                    4.3312570596754085e-07,
                    -9.973857686418341e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -31.998825073242188,
                    4.000383377075195,
                    -92.50015258789062
                ],
                "Up": [
                    2.2212659587239614e-06,
                    1.000001072883606,
                    9.983808695324115e-07
                ],
                "At": [
                    -1.0,
                    2.2212650492292596e-06,
                    -1.4742206531082047e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -31.99884033203125,
                    4.000326156616211,
                    -84.50015258789062
                ],
                "Up": [
                    2.3404752482747426e-06,
                    1.000001072883606,
                    1.0076945500259171e-06
                ],
                "At": [
                    -1.0,
                    2.340474338780041e-06,
                    -1.5934298289721482e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -23.99920654296875,
                    4.00068473815918,
                    -100.50009155273438
                ],
                "Up": [
                    1.386800818181655e-06,
                    1.000001072883606,
                    7.13394115336996e-07
                ],
                "At": [
                    -1.0,
                    1.3868001360606286e-06,
                    -9.973847454602947e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -23.999465942382812,
                    4.000444412231445,
                    -92.5
                ],
                "Up": [
                    4.3312635966685775e-07,
                    1.0000009536743164,
                    -2.160669225759193e-07
                ],
                "At": [
                    -1.0,
                    4.331257343892503e-07,
                    -8.781764790910529e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -15.999649047851562,
                    4.00086784362793,
                    -100.50015258789062
                ],
                "Up": [
                    6.715450240335485e-07,
                    1.0000009536743164,
                    -8.009313745560576e-08
                ],
                "At": [
                    -1.0,
                    6.715442850691034e-07,
                    -1.5934322163957404e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -15.999679565429688,
                    4.000932693481445,
                    -92.50015258789062
                ],
                "Up": [
                    7.907543704277487e-07,
                    1.0000009536743164,
                    -5.5878331295389216e-08
                ],
                "At": [
                    -1.0,
                    7.907535746198846e-07,
                    -1.831850795497303e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -15.99969482421875,
                    4.000997543334961,
                    -84.50015258789062
                ],
                "Up": [
                    9.099637736653676e-07,
                    1.0000009536743164,
                    -4.470217618290917e-08
                ],
                "At": [
                    -1.0,
                    9.09962807327247e-07,
                    -1.951060085048084e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -7.9996490478515625,
                    4.00074577331543,
                    -100.50015258789062
                ],
                "Up": [
                    6.715450240335485e-07,
                    1.0000009536743164,
                    -8.009313745560576e-08
                ],
                "At": [
                    -1.0,
                    6.715442850691034e-07,
                    -1.5934322163957404e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -7.9996490478515625,
                    4.000932693481445,
                    -92.50015258789062
                ],
                "Up": [
                    7.907543704277487e-07,
                    1.0000009536743164,
                    -5.0290424269405776e-08
                ],
                "At": [
                    -1.0,
                    7.907535746198846e-07,
                    -1.8318506818104652e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -7.9996795654296875,
                    4.000936508178711,
                    -84.50015258789062
                ],
                "Up": [
                    9.099637736653676e-07,
                    1.0000009536743164,
                    -3.352635502551493e-08
                ],
                "At": [
                    -1.0,
                    9.09962807327247e-07,
                    -1.951060085048084e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    0.0003204345703125,
                    4.00062370300293,
                    -100.50018310546875
                ],
                "Up": [
                    6.715450808769674e-07,
                    1.0000009536743164,
                    -1.1175816183595089e-07
                ],
                "At": [
                    -1.0,
                    6.715442850691034e-07,
                    -1.5934322163957404e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    0.0003509521484375,
                    4.000932693481445,
                    -92.50015258789062
                ],
                "Up": [
                    9.099637736653676e-07,
                    1.0000009536743164,
                    -3.5389032149169e-08
                ],
                "At": [
                    -1.0,
                    9.099628641706659e-07,
                    -1.8318506818104652e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    0.0003204345703125,
                    4.000936508178711,
                    -84.5001220703125
                ],
                "Up": [
                    9.099637736653676e-07,
                    1.0000009536743164,
                    -3.166362461115568e-08
                ],
                "At": [
                    -1.0,
                    9.09962807327247e-07,
                    -1.951060085048084e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    8.000320434570312,
                    4.00062370300293,
                    -100.50018310546875
                ],
                "Up": [
                    7.907544272711675e-07,
                    1.0000009536743164,
                    -7.636763399432311e-08
                ],
                "At": [
                    -1.0,
                    7.907535746198846e-07,
                    -1.5934322163957404e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    8.000289916992188,
                    4.000688552856445,
                    -92.50018310546875
                ],
                "Up": [
                    7.907544841145864e-07,
                    1.0000009536743164,
                    -9.685665958159007e-08
                ],
                "At": [
                    -1.0,
                    7.907535746198846e-07,
                    -1.7126415059465216e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    8.000274658203125,
                    4.000753402709961,
                    -84.50018310546875
                ],
                "Up": [
                    7.907544272711675e-07,
                    1.0000009536743164,
                    -8.009272534081902e-08
                ],
                "At": [
                    -1.0,
                    7.907535177764657e-07,
                    -1.951060085048084e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    16.000717163085938,
                    4.00062370300293,
                    -100.49993896484375
                ],
                "Up": [
                    1.3868009318684926e-06,
                    1.0000009536743164,
                    3.855686827591853e-07
                ],
                "At": [
                    -1.0,
                    1.3868001360606286e-06,
                    -1.1165944897584268e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    16.000320434570312,
                    4.000749588012695,
                    -92.50015258789062
                ],
                "Up": [
                    9.099638873522053e-07,
                    1.0000009536743164,
                    -1.11757607612617e-07
                ],
                "At": [
                    -1.0,
                    9.099628641706659e-07,
                    -1.7126415059465216e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    16.000289916992188,
                    4.000814437866211,
                    -84.50018310546875
                ],
                "Up": [
                    9.099637736653676e-07,
                    1.0000009536743164,
                    -4.656482133214013e-08
                ],
                "At": [
                    -1.0,
                    9.09962807327247e-07,
                    -1.951060085048084e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    24.000686645507812,
                    4.00074577331543,
                    -100.49990844726562
                ],
                "Up": [
                    1.0291728358424734e-06,
                    1.0000009536743164,
                    3.445899494636251e-07
                ],
                "At": [
                    -1.0,
                    1.0291722674082848e-06,
                    -9.973853138944833e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    24.000320434570312,
                    4.000688552856445,
                    -92.5001220703125
                ],
                "Up": [
                    9.099638873522053e-07,
                    1.0000009536743164,
                    -1.11757607612617e-07
                ],
                "At": [
                    -1.0,
                    9.099628641706659e-07,
                    -1.7126415059465216e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    24.00030517578125,
                    4.000814437866211,
                    -84.50018310546875
                ],
                "Up": [
                    9.099637736653676e-07,
                    1.0000009536743164,
                    -3.352638344722436e-08
                ],
                "At": [
                    -1.0,
                    9.09962807327247e-07,
                    -1.951060085048084e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    32.00065612792969,
                    4.00068473815918,
                    -100.49990844726562
                ],
                "Up": [
                    1.1483822390800924e-06,
                    1.0000009536743164,
                    3.4272741800123185e-07
                ],
                "At": [
                    -1.0,
                    1.148381556959066e-06,
                    -9.973853138944833e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    32.00032043457031,
                    4.000688552856445,
                    -92.5001220703125
                ],
                "Up": [
                    9.099638873522053e-07,
                    1.0000009536743164,
                    -1.1175757919090756e-07
                ],
                "At": [
                    -1.0,
                    9.099628641706659e-07,
                    -1.7126415059465216e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    32.000335693359375,
                    4.000875473022461,
                    -84.50018310546875
                ],
                "Up": [
                    9.099637736653676e-07,
                    1.0000009536743164,
                    -3.166362461115568e-08
                ],
                "At": [
                    -1.0,
                    9.09962807327247e-07,
                    -1.951060085048084e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    40.00062561035156,
                    4.00050163269043,
                    -100.4998779296875
                ],
                "Up": [
                    1.1483823527669301e-06,
                    1.0000009536743164,
                    3.0174919629644137e-07
                ],
                "At": [
                    -1.0,
                    1.148381556959066e-06,
                    -9.973853138944833e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    40.000335693359375,
                    4.000688552856445,
                    -92.5001220703125
                ],
                "Up": [
                    9.099638873522053e-07,
                    1.0000009536743164,
                    -1.11757607612617e-07
                ],
                "At": [
                    -1.0,
                    9.099628641706659e-07,
                    -1.7126415059465216e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    40.00028991699219,
                    4.000753402709961,
                    -84.5001220703125
                ],
                "Up": [
                    1.0291732905898243e-06,
                    1.0000009536743164,
                    -8.940542528534934e-08
                ],
                "At": [
                    -1.0,
                    1.029172153721447e-06,
                    -1.951060085048084e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    48.00068664550781,
                    4.00092887878418,
                    -100.50003051757812
                ],
                "Up": [
                    5.523355639525107e-07,
                    1.0000009536743164,
                    -2.6076856229906298e-08
                ],
                "At": [
                    -1.0,
                    5.523349955183221e-07,
                    -1.1165949445057777e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    48.00065612792969,
                    4.000932693481445,
                    -92.50006103515625
                ],
                "Up": [
                    5.523355639525107e-07,
                    1.0000009536743164,
                    -5.774185041218516e-08
                ],
                "At": [
                    -1.0,
                    5.523349955183221e-07,
                    -1.1165950581926154e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    48.00030517578125,
                    4.000814437866211,
                    -84.5001220703125
                ],
                "Up": [
                    1.0291731769029866e-06,
                    1.0000009536743164,
                    -2.421287703668895e-08
                ],
                "At": [
                    -1.0,
                    1.029172153721447e-06,
                    -1.951060085048084e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    32.000274658203125,
                    19.999656677246094,
                    -76.49984741210938
                ],
                "Up": [
                    1.7881401959130017e-07,
                    1.0000009536743164,
                    -5.960469025012571e-07
                ],
                "At": [
                    -5.662434432451846e-07,
                    5.960464477539062e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    24.000274658203125,
                    19.999778747558594,
                    -76.49984741210938
                ],
                "Up": [
                    2.3841860752327193e-07,
                    1.0000009536743164,
                    -5.960469025012571e-07
                ],
                "At": [
                    -5.289905971039843e-07,
                    5.960464477539062e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_DOOR_A",
                "UserData": 51,
                "Position": [
                    64.00050354003906,
                    4.000576019287109,
                    -72.49969482421875
                ],
                "Up": [
                    3.278256031080673e-07,
                    1.0000009536743164,
                    -1.1920922560193503e-07
                ],
                "At": [
                    -5.36441234544327e-07,
                    1.1920928955078125e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_DOOR_A",
                "UserData": 51,
                "Position": [
                    64.00050354003906,
                    4.000436782836914,
                    -104.499755859375
                ],
                "Up": [
                    5.960460498499742e-07,
                    1.0000009536743164,
                    3.178691088123742e-08
                ],
                "At": [
                    6.278330033637758e-07,
                    3.1786509424591713e-08,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_DOOR_A",
                "UserData": 51,
                "Position": [
                    -63.99900817871094,
                    4.000497817993164,
                    -104.50021362304688
                ],
                "Up": [
                    2.1457656202983344e-06,
                    1.0000009536743164,
                    9.854646805251832e-07
                ],
                "At": [
                    1.3430909575617989e-06,
                    9.854609288595384e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_DOOR_A",
                "UserData": 51,
                "Position": [
                    -63.99876403808594,
                    4.000331878662109,
                    -72.500244140625
                ],
                "Up": [
                    2.4437904357910156e-06,
                    1.0000009536743164,
                    9.53679204940272e-07
                ],
                "At": [
                    -1.676379156378971e-06,
                    -9.536742027194123e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    16.000289916992188,
                    19.999839782714844,
                    -76.4998779296875
                ],
                "Up": [
                    2.98023280720372e-07,
                    1.0000009536743164,
                    -5.960469025012571e-07
                ],
                "At": [
                    -4.917378078062029e-07,
                    5.960464477539062e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    8.000274658203125,
                    19.999656677246094,
                    -76.5
                ],
                "Up": [
                    2.0861621408130304e-07,
                    1.0000009536743164,
                    -4.768374992636382e-07
                ],
                "At": [
                    -6.854526191091281e-07,
                    4.76837158203125e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    0.0002593994140625,
                    19.999717712402344,
                    -76.5
                ],
                "Up": [
                    1.6292109705773328e-07,
                    1.0000009536743164,
                    -4.228207899359404e-07
                ],
                "At": [
                    1.0,
                    -1.629206565212371e-07,
                    6.715443987559411e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -7.9997100830078125,
                    19.999839782714844,
                    -76.5
                ],
                "Up": [
                    1.6292105442516913e-07,
                    1.0000009536743164,
                    -3.7439201605593553e-07
                ],
                "At": [
                    1.0,
                    -1.629206565212371e-07,
                    6.715443987559411e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -15.999740600585938,
                    19.999656677246094,
                    -76.50006103515625
                ],
                "Up": [
                    2.821305713496258e-07,
                    1.0000009536743164,
                    -4.880132564721862e-07
                ],
                "At": [
                    1.0,
                    -2.8212994607201836e-07,
                    7.907537451501412e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -23.999679565429688,
                    20.00042724609375,
                    -116.5001220703125
                ],
                "Up": [
                    5.960459930065554e-07,
                    1.0000009536743164,
                    -2.0663145505750435e-07
                ],
                "At": [
                    1.3430885701382067e-06,
                    -2.0663208033511182e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -31.999649047851562,
                    20.00054931640625,
                    -116.50015258789062
                ],
                "Up": [
                    5.364414050745836e-07,
                    1.0000009536743164,
                    -2.0663154032263265e-07
                ],
                "At": [
                    1.3430885701382067e-06,
                    -2.0663208033511182e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -39.99961853027344,
                    20.00048828125,
                    -116.50018310546875
                ],
                "Up": [
                    5.960459930065554e-07,
                    1.0000009536743164,
                    -2.0663145505750435e-07
                ],
                "At": [
                    1.3430885701382067e-06,
                    -2.0663208033511182e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -47.99964904785156,
                    20.0003662109375,
                    -116.50018310546875
                ],
                "Up": [
                    5.066393100605637e-07,
                    1.0000009536743164,
                    -3.2584108566879877e-07
                ],
                "At": [
                    1.1046699910366442e-06,
                    -3.2584134146418364e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -63.99964904785156,
                    20.00030517578125,
                    -116.50018310546875
                ],
                "Up": [
                    5.066393669039826e-07,
                    1.0000009536743164,
                    -3.258411993556365e-07
                ],
                "At": [
                    8.662514119350817e-07,
                    -3.2584134146418364e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -55.99964904785156,
                    20.00030517578125,
                    -116.50018310546875
                ],
                "Up": [
                    4.172323713191872e-07,
                    1.0000009536743164,
                    -3.258412846207648e-07
                ],
                "At": [
                    8.662514119350817e-07,
                    -3.2584134146418364e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -23.999710083007812,
                    27.999671936035156,
                    -60.50001525878906
                ],
                "Up": [
                    1.6292115390115214e-07,
                    1.0000009536743164,
                    -6.314370466498076e-07
                ],
                "At": [
                    1.0,
                    -1.629206565212371e-07,
                    5.523351660485787e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -31.999679565429688,
                    27.999671936035156,
                    -60.50001525878906
                ],
                "Up": [
                    1.6292113969029742e-07,
                    1.0000009536743164,
                    -5.997720791128813e-07
                ],
                "At": [
                    1.0,
                    -1.629206565212371e-07,
                    5.523351660485787e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -39.99967956542969,
                    27.999732971191406,
                    -60.50001525878906
                ],
                "Up": [
                    1.6292113969029742e-07,
                    1.0000009536743164,
                    -5.979094339636504e-07
                ],
                "At": [
                    1.0,
                    -1.629206565212371e-07,
                    5.523351660485787e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -47.99964904785156,
                    27.999855041503906,
                    -60.50001525878906
                ],
                "Up": [
                    1.6292113969029742e-07,
                    1.0000009536743164,
                    -5.979094339636504e-07
                ],
                "At": [
                    1.0,
                    -1.629206565212371e-07,
                    5.523351660485787e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -55.99964904785156,
                    27.999916076660156,
                    -60.50001525878906
                ],
                "Up": [
                    1.6292113969029742e-07,
                    1.0000009536743164,
                    -5.979094339636504e-07
                ],
                "At": [
                    1.0,
                    -1.629206565212371e-07,
                    5.523351660485787e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -63.99964904785156,
                    27.999977111816406,
                    -60.50001525878906
                ],
                "Up": [
                    1.6292113969029742e-07,
                    1.0000009536743164,
                    -5.979094339636504e-07
                ],
                "At": [
                    1.0,
                    -1.629206565212371e-07,
                    5.523351660485787e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -63.9996337890625,
                    28.000083923339844,
                    -68.5
                ],
                "Up": [
                    2.3841863594498136e-07,
                    1.0000009536743164,
                    -5.960468456578383e-07
                ],
                "At": [
                    -7.450572638845188e-07,
                    5.960464477539062e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -63.99961853027344,
                    28.000144958496094,
                    -76.5
                ],
                "Up": [
                    2.6822095833267667e-07,
                    1.0000009536743164,
                    -5.960468456578383e-07
                ],
                "At": [
                    -7.450572070410999e-07,
                    5.960464477539062e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -63.99961853027344,
                    28.000205993652344,
                    -84.5
                ],
                "Up": [
                    2.98023280720372e-07,
                    1.0000009536743164,
                    -5.960467888144194e-07
                ],
                "At": [
                    -7.525078444814426e-07,
                    5.960464477539062e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -63.99961853027344,
                    28.000198364257812,
                    -92.5
                ],
                "Up": [
                    3.278256031080673e-07,
                    1.0000009536743164,
                    -5.960467888144194e-07
                ],
                "At": [
                    -7.525077876380237e-07,
                    5.960464477539062e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -63.99961853027344,
                    28.000259399414062,
                    -100.50003051757812
                ],
                "Up": [
                    3.874301341966202e-07,
                    1.0000009536743164,
                    -4.768373287333816e-07
                ],
                "At": [
                    -7.450572070410999e-07,
                    4.76837158203125e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -63.99961853027344,
                    28.000381469726562,
                    -108.50003051757812
                ],
                "Up": [
                    4.172324565843155e-07,
                    1.0000009536743164,
                    -4.768373287333816e-07
                ],
                "At": [
                    -7.450572070410999e-07,
                    4.76837158203125e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -63.999603271484375,
                    28.00042724609375,
                    -116.50003051757812
                ],
                "Up": [
                    4.4703469370688254e-07,
                    1.0000009536743164,
                    -3.576278970740532e-07
                ],
                "At": [
                    -7.376068538178515e-07,
                    3.5762786865234375e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -55.99961853027344,
                    28.00048828125,
                    -116.50003051757812
                ],
                "Up": [
                    4.331265017754049e-07,
                    1.0000009536743164,
                    -3.892929214543983e-07
                ],
                "At": [
                    -1.0,
                    4.331257343892503e-07,
                    -8.781765927778906e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -47.99961853027344,
                    28.00054931640625,
                    -116.50003051757812
                ],
                "Up": [
                    4.331265017754049e-07,
                    1.0000009536743164,
                    -3.8743027630516735e-07
                ],
                "At": [
                    -1.0,
                    4.331257343892503e-07,
                    -8.781765927778906e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -39.99961853027344,
                    28.0006103515625,
                    -116.50003051757812
                ],
                "Up": [
                    4.331265017754049e-07,
                    1.0000009536743164,
                    -3.8743027630516735e-07
                ],
                "At": [
                    -1.0,
                    4.331257343892503e-07,
                    -8.781765927778906e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -31.999649047851562,
                    28.00054931640625,
                    -116.50003051757812
                ],
                "Up": [
                    4.331265017754049e-07,
                    1.0000009536743164,
                    -3.8743027630516735e-07
                ],
                "At": [
                    -1.0,
                    4.331257343892503e-07,
                    -8.781765927778906e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -23.999649047851562,
                    28.00054931640625,
                    -116.50003051757812
                ],
                "Up": [
                    4.331265017754049e-07,
                    1.0000009536743164,
                    -3.8743027630516735e-07
                ],
                "At": [
                    -1.0,
                    4.331257343892503e-07,
                    -8.781765927778906e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -15.999649047851562,
                    28.00054931640625,
                    -116.50003051757812
                ],
                "Up": [
                    4.331265017754049e-07,
                    1.0000009536743164,
                    -3.8743027630516735e-07
                ],
                "At": [
                    -1.0,
                    4.331257343892503e-07,
                    -8.781765927778906e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -7.999664306640625,
                    28.00054931640625,
                    -116.50003051757812
                ],
                "Up": [
                    4.331265017754049e-07,
                    1.0000009536743164,
                    -3.8743027630516735e-07
                ],
                "At": [
                    -1.0,
                    4.331257343892503e-07,
                    -8.781765927778906e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    0.0003509521484375,
                    28.00054931640625,
                    -116.50003051757812
                ],
                "Up": [
                    4.331265017754049e-07,
                    1.0000009536743164,
                    -3.8743027630516735e-07
                ],
                "At": [
                    -1.0,
                    4.331257343892503e-07,
                    -8.781765927778906e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    8.000335693359375,
                    28.00054931640625,
                    -116.50003051757812
                ],
                "Up": [
                    4.331265017754049e-07,
                    1.0000009536743164,
                    -3.8743027630516735e-07
                ],
                "At": [
                    -1.0,
                    4.331257343892503e-07,
                    -8.781765927778906e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    16.000320434570312,
                    28.00054931640625,
                    -116.50003051757812
                ],
                "Up": [
                    4.331265017754049e-07,
                    1.0000009536743164,
                    -3.8743027630516735e-07
                ],
                "At": [
                    -1.0,
                    4.331257343892503e-07,
                    -8.781765927778906e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    24.000320434570312,
                    28.00054931640625,
                    -116.50003051757812
                ],
                "Up": [
                    4.331265017754049e-07,
                    1.0000009536743164,
                    -3.8743027630516735e-07
                ],
                "At": [
                    -1.0,
                    4.331257343892503e-07,
                    -8.781765927778906e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    32.00035095214844,
                    28.0006103515625,
                    -116.50003051757812
                ],
                "Up": [
                    4.331265017754049e-07,
                    1.0000009536743164,
                    -3.8743027630516735e-07
                ],
                "At": [
                    -1.0,
                    4.331257343892503e-07,
                    -8.781765927778906e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    40.00038146972656,
                    28.0006103515625,
                    -116.50003051757812
                ],
                "Up": [
                    4.331265017754049e-07,
                    1.0000009536743164,
                    -3.8743027630516735e-07
                ],
                "At": [
                    -1.0,
                    4.331257343892503e-07,
                    -8.781765927778906e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    48.00038146972656,
                    28.0006103515625,
                    -116.50003051757812
                ],
                "Up": [
                    4.331265017754049e-07,
                    1.0000009536743164,
                    -3.8743027630516735e-07
                ],
                "At": [
                    -1.0,
                    4.331257343892503e-07,
                    -8.781765927778906e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    56.00038146972656,
                    28.0006103515625,
                    -116.50003051757812
                ],
                "Up": [
                    4.331265017754049e-07,
                    1.0000009536743164,
                    -3.8743027630516735e-07
                ],
                "At": [
                    -1.0,
                    4.331257343892503e-07,
                    -8.781765927778906e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    64.00041198730469,
                    28.00067138671875,
                    -116.50003051757812
                ],
                "Up": [
                    4.331265017754049e-07,
                    1.0000009536743164,
                    -3.8743027630516735e-07
                ],
                "At": [
                    -1.0,
                    4.331257343892503e-07,
                    -8.781765927778906e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    64.00038146972656,
                    28.000686645507812,
                    -108.50003051757812
                ],
                "Up": [
                    5.662439548359544e-07,
                    1.0000009536743164,
                    -3.258410288253799e-07
                ],
                "At": [
                    1.1046699910366442e-06,
                    -3.2584134146418364e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    64.00038146972656,
                    28.000686645507812,
                    -100.50003051757812
                ],
                "Up": [
                    6.25848599611345e-07,
                    1.0000009536743164,
                    -3.258409435602516e-07
                ],
                "At": [
                    1.1046699910366442e-06,
                    -3.2584134146418364e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    64.00038146972656,
                    28.000686645507812,
                    -92.5
                ],
                "Up": [
                    6.556509788424592e-07,
                    1.0000009536743164,
                    -3.258409151385422e-07
                ],
                "At": [
                    1.1046698773498065e-06,
                    -3.2584134146418364e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    64.00038146972656,
                    28.000694274902344,
                    -84.5
                ],
                "Up": [
                    6.854532443867356e-07,
                    1.0000009536743164,
                    -3.2584088671683276e-07
                ],
                "At": [
                    1.1046698773498065e-06,
                    -3.2584134146418364e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    64.00038146972656,
                    28.000694274902344,
                    -76.5
                ],
                "Up": [
                    7.152556236178498e-07,
                    1.0000009536743164,
                    -3.258408582951233e-07
                ],
                "At": [
                    1.1046698773498065e-06,
                    -3.2584134146418364e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    64.00035095214844,
                    28.000755310058594,
                    -68.5
                ],
                "Up": [
                    7.450577754752885e-07,
                    1.0000009536743164,
                    -2.0663145505750435e-07
                ],
                "At": [
                    1.1046699910366442e-06,
                    -2.0663208033511182e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    64.00035095214844,
                    28.000831604003906,
                    -60.50001525878906
                ],
                "Up": [
                    7.748600978629838e-07,
                    1.0000009536743164,
                    -2.066313982140855e-07
                ],
                "At": [
                    1.1046699910366442e-06,
                    -2.0663208033511182e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    56.00035095214844,
                    28.000892639160156,
                    -60.50001525878906
                ],
                "Up": [
                    8.781774454291735e-07,
                    1.0000009536743164,
                    -2.1234100699984992e-07
                ],
                "At": [
                    1.0,
                    -8.781763654042152e-07,
                    1.1483816706459038e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    48.0003662109375,
                    28.000953674316406,
                    -60.50001525878906
                ],
                "Up": [
                    8.781775022725924e-07,
                    1.0000009536743164,
                    -2.291047849212191e-07
                ],
                "At": [
                    1.0,
                    -8.781763654042152e-07,
                    1.1483816706459038e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    40.000213623046875,
                    27.999732971191406,
                    -60.49989318847656
                ],
                "Up": [
                    4.371167960925959e-08,
                    1.0000009536743164,
                    -6.165359991427977e-07
                ],
                "At": [
                    1.0,
                    -4.3711370523169535e-08,
                    4.3312579123266914e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    40.00022888183594,
                    27.999839782714844,
                    -68.4998779296875
                ],
                "Up": [
                    8.940698847936801e-08,
                    1.0000009536743164,
                    -5.96046959344676e-07
                ],
                "At": [
                    -5.28990710790822e-07,
                    5.960464477539062e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    40.00025939941406,
                    27.999900817871094,
                    -76.4998779296875
                ],
                "Up": [
                    5.960470161880949e-08,
                    1.0000009536743164,
                    -5.960470161880949e-07
                ],
                "At": [
                    -5.289906539474032e-07,
                    5.960464477539062e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    48.00035095214844,
                    28.000999450683594,
                    -68.5
                ],
                "Up": [
                    9.238714824277849e-07,
                    1.0000009536743164,
                    -2.3841761276344187e-07
                ],
                "At": [
                    -1.303850353906455e-06,
                    2.384185791015625e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    56.00035095214844,
                    28.000816345214844,
                    -68.50003051757812
                ],
                "Up": [
                    7.90754654644843e-07,
                    1.0000009536743164,
                    -2.5518187385387137e-07
                ],
                "At": [
                    -1.0,
                    7.907535746198846e-07,
                    -1.2358044614302344e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    56.00038146972656,
                    28.000755310058594,
                    -76.5
                ],
                "Up": [
                    7.450577754752885e-07,
                    1.0000009536743164,
                    -2.3841798224566446e-07
                ],
                "At": [
                    -1.1175857252965216e-06,
                    2.384185791015625e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    48.00025939941406,
                    27.999961853027344,
                    -76.4998779296875
                ],
                "Up": [
                    1.1920936060505483e-07,
                    1.0000009536743164,
                    -5.96046959344676e-07
                ],
                "At": [
                    -7.376067969744327e-07,
                    5.960464477539062e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    56.00038146972656,
                    28.000694274902344,
                    -84.50003051757812
                ],
                "Up": [
                    7.748602115498215e-07,
                    1.0000009536743164,
                    -3.57627357061574e-07
                ],
                "At": [
                    -1.1101355994469486e-06,
                    3.5762786865234375e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    48.000274658203125,
                    28.000022888183594,
                    -84.4998779296875
                ],
                "Up": [
                    1.4901168299275014e-07,
                    1.0000009536743164,
                    -5.960469025012571e-07
                ],
                "At": [
                    -7.450573207279376e-07,
                    5.960464477539062e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    48.00030517578125,
                    28.000076293945312,
                    -92.4998779296875
                ],
                "Up": [
                    1.4901168299275014e-07,
                    1.0000009536743164,
                    -5.960469025012571e-07
                ],
                "At": [
                    -7.450573207279376e-07,
                    5.960464477539062e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    40.00025939941406,
                    27.999961853027344,
                    -84.4998779296875
                ],
                "Up": [
                    5.960469451338213e-08,
                    1.0000009536743164,
                    -5.960470161880949e-07
                ],
                "At": [
                    -5.215400733504794e-07,
                    5.960464477539062e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    40.00028991699219,
                    28.000137329101562,
                    -92.4998779296875
                ],
                "Up": [
                    1.4901159772762185e-07,
                    1.0000009536743164,
                    -4.768374992636382e-07
                ],
                "At": [
                    -7.152549983402423e-07,
                    4.76837158203125e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    40.00030517578125,
                    28.000198364257812,
                    -100.49990844726562
                ],
                "Up": [
                    1.4901159772762185e-07,
                    1.0000009536743164,
                    -4.768374992636382e-07
                ],
                "At": [
                    -7.227055789371661e-07,
                    4.76837158203125e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    48.00032043457031,
                    28.000137329101562,
                    -100.49990844726562
                ],
                "Up": [
                    1.4901168299275014e-07,
                    1.0000009536743164,
                    -5.960469025012571e-07
                ],
                "At": [
                    -7.525078444814426e-07,
                    5.960464477539062e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    56.00032043457031,
                    28.000076293945312,
                    -92.49990844726562
                ],
                "Up": [
                    1.947078374087141e-07,
                    1.0000009536743164,
                    -5.662444095833052e-07
                ],
                "At": [
                    -1.0,
                    1.9470714107683307e-07,
                    -8.781765359344718e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    56.00038146972656,
                    28.000808715820312,
                    -100.50003051757812
                ],
                "Up": [
                    6.55651035685878e-07,
                    1.0000009536743164,
                    -3.576274707484117e-07
                ],
                "At": [
                    -1.1175856116096838e-06,
                    3.5762786865234375e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    56.00038146972656,
                    28.000686645507812,
                    -108.50003051757812
                ],
                "Up": [
                    5.662439548359544e-07,
                    1.0000009536743164,
                    -3.5762758443524945e-07
                ],
                "At": [
                    -1.1101352583864355e-06,
                    3.5762786865234375e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    40.00035095214844,
                    28.000625610351562,
                    -108.50003051757812
                ],
                "Up": [
                    5.662439548359544e-07,
                    1.0000009536743164,
                    -3.5762758443524945e-07
                ],
                "At": [
                    -1.1101352583864355e-06,
                    3.5762786865234375e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    48.00035095214844,
                    28.000198364257812,
                    -108.49990844726562
                ],
                "Up": [
                    1.7881390590446244e-07,
                    1.0000009536743164,
                    -4.768374992636382e-07
                ],
                "At": [
                    -7.599584250783664e-07,
                    4.76837158203125e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    32.0003662109375,
                    28.000686645507812,
                    -108.50003051757812
                ],
                "Up": [
                    5.205493494031543e-07,
                    1.0000009536743164,
                    -3.8184222717063676e-07
                ],
                "At": [
                    1.0,
                    -5.205484967518714e-07,
                    9.099630915443413e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    24.00030517578125,
                    28.000625610351562,
                    -108.50003051757812
                ],
                "Up": [
                    5.205493494031543e-07,
                    1.0000009536743164,
                    -3.8184222717063676e-07
                ],
                "At": [
                    1.0,
                    -5.205484967518714e-07,
                    9.099630915443413e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    16.000320434570312,
                    28.000564575195312,
                    -108.50003051757812
                ],
                "Up": [
                    5.205493494031543e-07,
                    1.0000009536743164,
                    -3.8184222717063676e-07
                ],
                "At": [
                    1.0,
                    -5.205484967518714e-07,
                    9.099630915443413e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    8.000350952148438,
                    28.000625610351562,
                    -108.50003051757812
                ],
                "Up": [
                    5.205493494031543e-07,
                    1.0000009536743164,
                    -3.8184222717063676e-07
                ],
                "At": [
                    1.0,
                    -5.205484967518714e-07,
                    9.099630915443413e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    8.000335693359375,
                    28.000625610351562,
                    -100.50003051757812
                ],
                "Up": [
                    5.205493494031543e-07,
                    1.0000009536743164,
                    -3.6880371112602006e-07
                ],
                "At": [
                    1.0,
                    -5.205484967518714e-07,
                    9.099630915443413e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    16.000350952148438,
                    28.000625610351562,
                    -100.5
                ],
                "Up": [
                    5.205493494031543e-07,
                    1.0000009536743164,
                    -3.6880371112602006e-07
                ],
                "At": [
                    1.0,
                    -5.205484967518714e-07,
                    9.099630915443413e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    8.000350952148438,
                    28.000686645507812,
                    -92.5
                ],
                "Up": [
                    5.662439548359544e-07,
                    1.0000009536743164,
                    -3.2584117093392706e-07
                ],
                "At": [
                    8.662513550916628e-07,
                    -3.2584134146418364e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    16.000350952148438,
                    28.000686645507812,
                    -92.5
                ],
                "Up": [
                    5.662439548359544e-07,
                    1.0000009536743164,
                    -3.2584117093392706e-07
                ],
                "At": [
                    8.662513550916628e-07,
                    -3.2584134146418364e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    24.00030517578125,
                    28.000686645507812,
                    -100.50003051757812
                ],
                "Up": [
                    5.523359050130239e-07,
                    1.0000009536743164,
                    -3.7066629943183216e-07
                ],
                "At": [
                    -1.0,
                    5.523349955183221e-07,
                    -9.973858823286719e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    24.00030517578125,
                    28.000747680664062,
                    -92.5
                ],
                "Up": [
                    5.523359618564427e-07,
                    1.0000009536743164,
                    -3.8184202821867075e-07
                ],
                "At": [
                    -1.0,
                    5.523349955183221e-07,
                    -1.2358044614302344e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    32.00030517578125,
                    28.000259399414062,
                    -100.49990844726562
                ],
                "Up": [
                    1.9470778056529525e-07,
                    1.0000009536743164,
                    -5.029144745094527e-07
                ],
                "At": [
                    -1.0,
                    1.9470714107683307e-07,
                    -8.781764790910529e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    32.00028991699219,
                    28.000808715820312,
                    -92.50003051757812
                ],
                "Up": [
                    5.523359618564427e-07,
                    1.0000009536743164,
                    -3.8184202821867075e-07
                ],
                "At": [
                    -1.0,
                    5.523349955183221e-07,
                    -1.2358044614302344e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    32.000274658203125,
                    28.000816345214844,
                    -84.50003051757812
                ],
                "Up": [
                    5.523360755432805e-07,
                    1.0000009536743164,
                    -3.781166242333711e-07
                ],
                "At": [
                    -1.0,
                    5.523349955183221e-07,
                    -1.4742230405317969e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    24.000274658203125,
                    28.000755310058594,
                    -84.5
                ],
                "Up": [
                    5.960461635368119e-07,
                    1.0000009536743164,
                    -3.258408582951233e-07
                ],
                "At": [
                    1.3430885701382067e-06,
                    -3.2584134146418364e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    32.00025939941406,
                    28.000816345214844,
                    -76.5
                ],
                "Up": [
                    6.715454787808994e-07,
                    1.0000009536743164,
                    -3.7252840456858394e-07
                ],
                "At": [
                    -1.0,
                    6.715442850691034e-07,
                    -1.5934323300825781e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    24.000259399414062,
                    28.000877380371094,
                    -76.5
                ],
                "Up": [
                    6.556508083122026e-07,
                    1.0000009536743164,
                    -3.258404603911913e-07
                ],
                "At": [
                    1.819925614654494e-06,
                    -3.2584134146418364e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^CEILINGLIGHT",
                "UserData": 0,
                "Position": [
                    -46.1744384765625,
                    27.020828247070312,
                    -92.44819641113281
                ],
                "Up": [
                    0.0005085064913146198,
                    -5.000004768371582,
                    -0.0009885337203741074
                ],
                "At": [
                    0.9983217120170593,
                    9.008104098029435e-05,
                    0.057911466807127
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^CEILINGLIGHT",
                "UserData": 0,
                "Position": [
                    -16.1744384765625,
                    27.020828247070312,
                    -92.44819641113281
                ],
                "Up": [
                    0.0005085064913146198,
                    -5.000004768371582,
                    -0.0009885337203741074
                ],
                "At": [
                    0.9983217120170593,
                    9.008104098029435e-05,
                    0.057911466807127
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^CEILINGLIGHT",
                "UserData": 0,
                "Position": [
                    13.8255615234375,
                    27.020828247070312,
                    -92.44819641113281
                ],
                "Up": [
                    0.0005085064913146198,
                    -5.000004768371582,
                    -0.0009885337203741074
                ],
                "At": [
                    0.9983217120170593,
                    9.008104098029435e-05,
                    0.057911466807127
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^CEILINGLIGHT",
                "UserData": 0,
                "Position": [
                    43.8255615234375,
                    27.020828247070312,
                    -92.44819641113281
                ],
                "Up": [
                    0.0005085064913146198,
                    -5.000004768371582,
                    -0.0009885337203741074
                ],
                "At": [
                    0.9983217120170593,
                    9.008104098029435e-05,
                    0.057911466807127
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    24.000198364257812,
                    27.999778747558594,
                    -68.49996948242188
                ],
                "Up": [
                    1.5099628569714696e-07,
                    1.0000009536743164,
                    -5.960469025012571e-07
                ],
                "At": [
                    6.278328896769381e-07,
                    -5.960464477539062e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    32.00025939941406,
                    28.000816345214844,
                    -68.5
                ],
                "Up": [
                    6.715455924677372e-07,
                    1.0000009536743164,
                    -3.799788430569606e-07
                ],
                "At": [
                    -1.0,
                    6.715442850691034e-07,
                    -1.8318509091841406e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    16.000198364257812,
                    27.999778747558594,
                    -68.5
                ],
                "Up": [
                    4.3711665398404875e-08,
                    1.0000009536743164,
                    -5.792830961581785e-07
                ],
                "At": [
                    1.0,
                    -4.3711370523169535e-08,
                    4.3312579123266914e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    16.000274658203125,
                    28.000755310058594,
                    -84.50003051757812
                ],
                "Up": [
                    6.39758866327611e-07,
                    1.0000009536743164,
                    -3.2596238952464773e-07
                ],
                "At": [
                    1.0,
                    -6.397577863026527e-07,
                    1.5060095392982475e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    16.000228881835938,
                    27.999900817871094,
                    -76.5
                ],
                "Up": [
                    1.629211254794427e-07,
                    1.0000009536743164,
                    -5.69969756725186e-07
                ],
                "At": [
                    1.0,
                    -1.629206565212371e-07,
                    5.523351660485787e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    8.000213623046875,
                    27.999778747558594,
                    -68.49993896484375
                ],
                "Up": [
                    1.6292101179260499e-07,
                    1.0000009536743164,
                    -6.109479500082671e-07
                ],
                "At": [
                    1.0,
                    -1.6292067073209182e-07,
                    3.1391655852530675e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    0.0001983642578125,
                    27.999778747558594,
                    -68.49993896484375
                ],
                "Up": [
                    4.371161210769969e-08,
                    1.0000009536743164,
                    -6.109480068516859e-07
                ],
                "At": [
                    1.0,
                    -4.3711374075883214e-08,
                    3.139165016818879e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -7.9997406005859375,
                    27.999778747558594,
                    -68.5
                ],
                "Up": [
                    1.6292115390115214e-07,
                    1.0000009536743164,
                    -6.183985306051909e-07
                ],
                "At": [
                    1.0,
                    -1.629206565212371e-07,
                    5.523351660485787e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    8.000228881835938,
                    27.999900817871094,
                    -76.5
                ],
                "Up": [
                    1.62921111268588e-07,
                    1.0000009536743164,
                    -5.513432483894576e-07
                ],
                "At": [
                    1.0,
                    -1.629206565212371e-07,
                    5.523351660485787e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    8.000335693359375,
                    28.000694274902344,
                    -84.5
                ],
                "Up": [
                    6.258487132981827e-07,
                    1.0000009536743164,
                    -3.5762758443524945e-07
                ],
                "At": [
                    -1.0207282912233495e-06,
                    3.5762786865234375e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    0.000213623046875,
                    27.999839782714844,
                    -76.49993896484375
                ],
                "Up": [
                    1.6292113969029742e-07,
                    1.0000009536743164,
                    -5.867335630682646e-07
                ],
                "At": [
                    1.0,
                    -1.629206565212371e-07,
                    5.523351660485787e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    0.0002288818359375,
                    27.999900817871094,
                    -84.49993896484375
                ],
                "Up": [
                    2.0861631355728605e-07,
                    1.0000009536743164,
                    -5.960469025012571e-07
                ],
                "At": [
                    -7.003537803029758e-07,
                    5.960464477539062e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    0.0003509521484375,
                    28.000747680664062,
                    -92.5
                ],
                "Up": [
                    6.258486564547638e-07,
                    1.0000009536743164,
                    -3.5762758443524945e-07
                ],
                "At": [
                    -1.0281788718202733e-06,
                    3.5762786865234375e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -7.9997406005859375,
                    27.999778747558594,
                    -76.50003051757812
                ],
                "Up": [
                    1.6292128179884457e-07,
                    1.0000009536743164,
                    -6.109478931648482e-07
                ],
                "At": [
                    1.0,
                    -1.629206565212371e-07,
                    7.907537451501412e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -7.9997100830078125,
                    27.999839782714844,
                    -84.50003051757812
                ],
                "Up": [
                    2.8213079872330127e-07,
                    1.0000009536743164,
                    -6.128104246272414e-07
                ],
                "At": [
                    1.0,
                    -2.821299176503089e-07,
                    1.0291723810951225e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -7.9996490478515625,
                    28.000869750976562,
                    -92.5
                ],
                "Up": [
                    6.85453073856479e-07,
                    1.0000009536743164,
                    -2.3841812435421161e-07
                ],
                "At": [
                    -9.909261962093296e-07,
                    2.384185791015625e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -15.999710083007812,
                    27.999717712402344,
                    -68.5
                ],
                "Up": [
                    1.62921310220554e-07,
                    1.0000009536743164,
                    -6.463382078436553e-07
                ],
                "At": [
                    1.0,
                    -1.629206565212371e-07,
                    7.907537451501412e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -23.999710083007812,
                    27.999717712402344,
                    -68.5
                ],
                "Up": [
                    2.82130713458173e-07,
                    1.0000009536743164,
                    -6.500633844552794e-07
                ],
                "At": [
                    1.0,
                    -2.8212994607201836e-07,
                    7.9075380199356e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -31.999649047851562,
                    27.999717712402344,
                    -68.5
                ],
                "Up": [
                    1.6292126758798986e-07,
                    1.0000009536743164,
                    -5.923214985159575e-07
                ],
                "At": [
                    1.0,
                    -1.629206565212371e-07,
                    7.907537451501412e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -15.999710083007812,
                    27.999717712402344,
                    -76.50003051757812
                ],
                "Up": [
                    1.6292143811824644e-07,
                    1.0000009536743164,
                    -6.25848997515277e-07
                ],
                "At": [
                    1.0,
                    -1.629206423103824e-07,
                    1.0291722674082848e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -23.999679565429688,
                    27.999778747558594,
                    -76.5
                ],
                "Up": [
                    2.821308271450107e-07,
                    1.0000009536743164,
                    -6.31436876119551e-07
                ],
                "At": [
                    1.0,
                    -2.821299176503089e-07,
                    1.0291723810951225e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -31.9996337890625,
                    27.999778747558594,
                    -76.5
                ],
                "Up": [
                    1.6292138127482758e-07,
                    1.0000009536743164,
                    -5.736949333368102e-07
                ],
                "At": [
                    1.0,
                    -1.629206423103824e-07,
                    1.0291722674082848e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -31.9996337890625,
                    27.999839782714844,
                    -84.50003051757812
                ],
                "Up": [
                    2.8213085556672013e-07,
                    1.0000009536743164,
                    -5.904586259930511e-07
                ],
                "At": [
                    1.0,
                    -2.821299176503089e-07,
                    1.1483816706459038e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -23.9996337890625,
                    27.999900817871094,
                    -84.50003051757812
                ],
                "Up": [
                    2.821309976752673e-07,
                    1.0000009536743164,
                    -6.109476089477539e-07
                ],
                "At": [
                    1.0,
                    -2.821299176503089e-07,
                    1.3868002497474663e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -15.999679565429688,
                    27.999900817871094,
                    -84.50006103515625
                ],
                "Up": [
                    2.6822101517609553e-07,
                    1.0000009536743164,
                    -5.960467888144194e-07
                ],
                "At": [
                    -9.313216082773579e-07,
                    5.960464477539062e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -15.9996337890625,
                    28.000930786132812,
                    -92.50003051757812
                ],
                "Up": [
                    7.152553962441743e-07,
                    1.0000009536743164,
                    -2.3841812435421161e-07
                ],
                "At": [
                    -9.536732932247105e-07,
                    2.384185791015625e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -23.999603271484375,
                    27.999954223632812,
                    -92.50003051757812
                ],
                "Up": [
                    2.8213105451868614e-07,
                    1.0000009536743164,
                    -5.923212142988632e-07
                ],
                "At": [
                    1.0,
                    -2.821299176503089e-07,
                    1.5060095392982475e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -31.999588012695312,
                    28.000076293945312,
                    -92.50003051757812
                ],
                "Up": [
                    2.821310260969767e-07,
                    1.0000009536743164,
                    -5.755574079557846e-07
                ],
                "At": [
                    1.0,
                    -2.821299176503089e-07,
                    1.5060095392982475e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    0.000335693359375,
                    28.000686645507812,
                    -108.50003051757812
                ],
                "Up": [
                    5.662439548359544e-07,
                    1.0000009536743164,
                    -3.5762758443524945e-07
                ],
                "At": [
                    -1.1101352583864355e-06,
                    3.5762786865234375e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    0.000396728515625,
                    28.000808715820312,
                    -100.5
                ],
                "Up": [
                    6.71545251407224e-07,
                    1.0000009536743164,
                    -3.1292415769712534e-07
                ],
                "At": [
                    -1.0,
                    6.715442850691034e-07,
                    -9.973858823286719e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -7.9996337890625,
                    28.000930786132812,
                    -100.5
                ],
                "Up": [
                    6.715451945638051e-07,
                    1.0000009536743164,
                    -2.905724727497727e-07
                ],
                "At": [
                    -1.0,
                    6.715442850691034e-07,
                    -8.781766496213095e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -7.999603271484375,
                    28.000991821289062,
                    -108.5
                ],
                "Up": [
                    7.450577186318696e-07,
                    1.0000009536743164,
                    -2.3841812435421161e-07
                ],
                "At": [
                    -9.313216651207767e-07,
                    2.384185791015625e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -15.999649047851562,
                    28.000564575195312,
                    -108.50003051757812
                ],
                "Up": [
                    5.662439548359544e-07,
                    1.0000009536743164,
                    -3.5762758443524945e-07
                ],
                "At": [
                    -1.1101352583864355e-06,
                    3.5762786865234375e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -15.999679565429688,
                    28.000625610351562,
                    -100.5
                ],
                "Up": [
                    5.960461635368119e-07,
                    1.0000009536743164,
                    -3.576274423267023e-07
                ],
                "At": [
                    -1.2740478041450842e-06,
                    3.5762786865234375e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -23.999588012695312,
                    28.000015258789062,
                    -100.50003051757812
                ],
                "Up": [
                    2.821311966272333e-07,
                    1.0000009536743164,
                    -5.979090360597183e-07
                ],
                "At": [
                    1.0,
                    -2.821298892285995e-07,
                    1.74442811839981e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -23.999649047851562,
                    28.000564575195312,
                    -108.50003051757812
                ],
                "Up": [
                    5.662439548359544e-07,
                    1.0000009536743164,
                    -3.5762758443524945e-07
                ],
                "At": [
                    -1.1101352583864355e-06,
                    3.5762786865234375e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -31.999526977539062,
                    28.000137329101562,
                    -100.50003051757812
                ],
                "Up": [
                    2.8213116820552386e-07,
                    1.0000009536743164,
                    -5.811451728732209e-07
                ],
                "At": [
                    1.0,
                    -2.821298892285995e-07,
                    1.74442811839981e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -31.999526977539062,
                    28.000198364257812,
                    -108.50003051757812
                ],
                "Up": [
                    4.0134071355169e-07,
                    1.0000009536743164,
                    -5.848702357980073e-07
                ],
                "At": [
                    1.0,
                    -4.0133917877938075e-07,
                    1.9828466975013725e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -39.99961853027344,
                    28.000625610351562,
                    -108.50003051757812
                ],
                "Up": [
                    5.205493494031543e-07,
                    1.0000009536743164,
                    -3.8184222717063676e-07
                ],
                "At": [
                    1.0,
                    -5.205484967518714e-07,
                    9.099630915443413e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -39.9996337890625,
                    28.000686645507812,
                    -100.50003051757812
                ],
                "Up": [
                    5.205493494031543e-07,
                    1.0000009536743164,
                    -3.6880371112602006e-07
                ],
                "At": [
                    1.0,
                    -5.205484967518714e-07,
                    9.099630915443413e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -39.99964904785156,
                    27.999900817871094,
                    -84.50003051757812
                ],
                "Up": [
                    2.980233091420814e-07,
                    1.0000009536743164,
                    -5.642601195177122e-07
                ],
                "At": [
                    1.3430885701382067e-06,
                    -5.642600058308744e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -39.99957275390625,
                    28.000137329101562,
                    -92.50003051757812
                ],
                "Up": [
                    2.980233944072097e-07,
                    1.0000009536743164,
                    -5.642600626742933e-07
                ],
                "At": [
                    1.5815071492397692e-06,
                    -5.642600058308744e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -39.9996337890625,
                    27.999778747558594,
                    -76.5
                ],
                "Up": [
                    2.3841860752327193e-07,
                    1.0000009536743164,
                    -5.642602332045499e-07
                ],
                "At": [
                    1.1046699910366442e-06,
                    -5.642600058308744e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -39.99964904785156,
                    27.999839782714844,
                    -68.5
                ],
                "Up": [
                    2.0861631355728605e-07,
                    1.0000009536743164,
                    -5.642602900479687e-07
                ],
                "At": [
                    1.1046699910366442e-06,
                    -5.642600058308744e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -47.99964904785156,
                    27.999839782714844,
                    -68.50003051757812
                ],
                "Up": [
                    2.8213068503646355e-07,
                    1.0000009536743164,
                    -6.183984169183532e-07
                ],
                "At": [
                    1.0,
                    -2.8212994607201836e-07,
                    7.9075380199356e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -47.99961853027344,
                    27.999900817871094,
                    -76.50003051757812
                ],
                "Up": [
                    2.8213079872330127e-07,
                    1.0000009536743164,
                    -5.997719085826247e-07
                ],
                "At": [
                    1.0,
                    -2.821299176503089e-07,
                    1.0291723810951225e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -47.99958801269531,
                    27.999961853027344,
                    -84.5
                ],
                "Up": [
                    2.821308271450107e-07,
                    1.0000009536743164,
                    -5.774201099484344e-07
                ],
                "At": [
                    1.0,
                    -2.821299176503089e-07,
                    1.1483816706459038e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -47.99958801269531,
                    28.000015258789062,
                    -92.5
                ],
                "Up": [
                    4.013403724911768e-07,
                    1.0000009536743164,
                    -5.867331083209137e-07
                ],
                "At": [
                    1.0,
                    -4.013392072010902e-07,
                    1.3868002497474663e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -47.99955749511719,
                    28.000076293945312,
                    -100.5
                ],
                "Up": [
                    4.0134048617801454e-07,
                    1.0000009536743164,
                    -5.662439548359544e-07
                ],
                "At": [
                    1.0,
                    -4.013392072010902e-07,
                    1.6252188288490288e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -47.999542236328125,
                    28.000198364257812,
                    -108.5
                ],
                "Up": [
                    5.205499746807618e-07,
                    1.0000009536743164,
                    -5.68106315768091e-07
                ],
                "At": [
                    1.0,
                    -5.205484967518714e-07,
                    1.7444282320866478e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -55.99952697753906,
                    28.000259399414062,
                    -108.50003051757812
                ],
                "Up": [
                    5.205499746807618e-07,
                    1.0000009536743164,
                    -5.69968960917322e-07
                ],
                "At": [
                    1.0,
                    -5.205484967518714e-07,
                    1.7444282320866478e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -55.99958801269531,
                    28.000259399414062,
                    -100.50003051757812
                ],
                "Up": [
                    4.0134003143066366e-07,
                    1.0000009536743164,
                    -4.768372718899627e-07
                ],
                "At": [
                    1.0,
                    -4.013392356227996e-07,
                    9.099630915443413e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -55.99964904785156,
                    28.000198364257812,
                    -92.5
                ],
                "Up": [
                    4.013400882740825e-07,
                    1.0000009536743164,
                    -5.457551424115081e-07
                ],
                "At": [
                    1.0,
                    -4.013392356227996e-07,
                    9.099631483877602e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -55.99964904785156,
                    28.000205993652344,
                    -84.5
                ],
                "Up": [
                    4.470348642371391e-07,
                    1.0000009536743164,
                    -5.642600058308744e-07
                ],
                "At": [
                    1.1046698773498065e-06,
                    -5.642600058308744e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_EXT_PLATFOR",
                "UserData": 51,
                "Position": [
                    -55.99961853027344,
                    28.000205993652344,
                    -76.50003051757812
                ],
                "Up": [
                    2.980233091420814e-07,
                    1.0000009536743164,
                    -5.642602332045499e-07
                ],
                "At": [
                    8.662513550916628e-07,
                    -5.642600058308744e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^CUBEROOM_SPACE",
                "UserData": 0,
                "Position": [
                    8.000152587890625,
                    19.99993896484375,
                    -4.499933242797852
                ],
                "Up": [
                    4.3711580133276584e-08,
                    1.0000009536743164,
                    -5.14090515935095e-07
                ],
                "At": [
                    1.0,
                    -4.3711374075883214e-08,
                    3.139165016818879e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_DOOR_A",
                "UserData": 51,
                "Position": [
                    8.000473022460938,
                    4.000213623046875,
                    -64.49993896484375
                ],
                "Up": [
                    2.3841846541472478e-07,
                    1.0000009536743164,
                    -3.5762803918260033e-07
                ],
                "At": [
                    -7.45057150197681e-07,
                    3.5762786865234375e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_WINDOW",
                "UserData": 51,
                "Position": [
                    8.000152587890625,
                    19.99993896484375,
                    -0.49993324279785156
                ],
                "Up": [
                    -2.9802286860558524e-08,
                    1.0000009536743164,
                    -5.642605174216442e-07
                ],
                "At": [
                    3.8941439584050386e-07,
                    -5.642600058308744e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_WINDOW",
                "UserData": 51,
                "Position": [
                    16.000213623046875,
                    19.99993896484375,
                    -0.49993324279785156
                ],
                "Up": [
                    1.5099602990176209e-07,
                    1.0000009536743164,
                    -5.960470161880949e-07
                ],
                "At": [
                    1.509957598955225e-07,
                    -5.960464477539062e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    24.00018310546875,
                    20.00006103515625,
                    -4.499994277954102
                ],
                "Up": [
                    -4.371128881075492e-08,
                    1.0000009536743164,
                    -5.58793999516638e-07
                ],
                "At": [
                    -1.0,
                    -4.3711398944878965e-08,
                    -2.8212994607201836e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_DOOR_A",
                "UserData": 51,
                "Position": [
                    -7.99969482421875,
                    19.99968719482422,
                    -16.499961853027344
                ],
                "Up": [
                    2.9802372125686816e-08,
                    1.0000009536743164,
                    -5.960470161880949e-07
                ],
                "At": [
                    -4.3213321987423114e-07,
                    5.960464477539062e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_DOOR_A",
                "UserData": 51,
                "Position": [
                    28.000244140625,
                    19.999526977539062,
                    -28.499916076660156
                ],
                "Up": [
                    4.3711928299217107e-08,
                    1.0000009536743164,
                    -6.705526516270766e-07
                ],
                "At": [
                    1.0,
                    -4.371135275960114e-08,
                    7.907536883067223e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^CUBEROOM_SPACE",
                "UserData": 0,
                "Position": [
                    -7.99969482421875,
                    19.99969482421875,
                    -4.499979019165039
                ],
                "Up": [
                    1.3775546187696358e-13,
                    1.0000009536743164,
                    -6.834699206592632e-07
                ],
                "At": [
                    6.278329465203569e-07,
                    -6.834692953816557e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^CUBEROOM_SPACE",
                "UserData": 0,
                "Position": [
                    0.000152587890625,
                    19.99993896484375,
                    -4.499933242797852
                ],
                "Up": [
                    2.9802347256691064e-08,
                    1.0000009536743164,
                    -5.642605174216442e-07
                ],
                "At": [
                    3.8941436741879443e-07,
                    -5.642600058308744e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_WALL",
                "UserData": 51,
                "Position": [
                    4.00018310546875,
                    19.99993896484375,
                    -4.499917984008789
                ],
                "Up": [
                    7.549822100827441e-08,
                    1.0000009536743164,
                    -5.215409828451811e-07
                ],
                "At": [
                    -1.0,
                    7.549787994776125e-08,
                    -5.205486104387091e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_WALL",
                "UserData": 51,
                "Position": [
                    4.00018310546875,
                    20.0,
                    -12.499996185302734
                ],
                "Up": [
                    -4.371130302160964e-08,
                    1.0000009536743164,
                    -4.991893547412474e-07
                ],
                "At": [
                    -1.0,
                    -4.3711398944878965e-08,
                    -2.8212994607201836e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_WINDOW",
                "UserData": 51,
                "Position": [
                    0.000152587890625,
                    19.99993896484375,
                    -0.49991798400878906
                ],
                "Up": [
                    2.9802347256691064e-08,
                    1.0000009536743164,
                    -5.642605174216442e-07
                ],
                "At": [
                    3.8941436741879443e-07,
                    -5.642600058308744e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_WINDOW",
                "UserData": 51,
                "Position": [
                    -7.99969482421875,
                    19.99969482421875,
                    -0.49994850158691406
                ],
                "Up": [
                    7.161538885785274e-14,
                    1.0000009536743164,
                    -6.834699206592632e-07
                ],
                "At": [
                    3.8941436741879443e-07,
                    -6.834692953816557e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -15.999755859375,
                    19.999755859375,
                    -4.499994277954102
                ],
                "Up": [
                    2.9802347256691064e-08,
                    1.0000009536743164,
                    -5.642605174216442e-07
                ],
                "At": [
                    3.8941436741879443e-07,
                    -5.642600058308744e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^CUBEROOM_SPACE",
                "UserData": 0,
                "Position": [
                    -23.999755859375,
                    19.999862670898438,
                    -28.499977111816406
                ],
                "Up": [
                    4.3711729347251094e-08,
                    1.0000009536743164,
                    -5.811456844639906e-07
                ],
                "At": [
                    1.0,
                    -4.371136341774218e-08,
                    5.523351092051598e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^CUBEROOM_SPACE",
                "UserData": 0,
                "Position": [
                    40.000335693359375,
                    19.999496459960938,
                    -28.499916076660156
                ],
                "Up": [
                    7.549837732767628e-08,
                    1.0000009536743164,
                    -6.780032322240004e-07
                ],
                "At": [
                    -1.0,
                    7.549787284233389e-08,
                    -6.397578999894904e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^CUBEROOM_SPACE",
                "UserData": 0,
                "Position": [
                    40.000244140625,
                    19.99999237060547,
                    -20.499855041503906
                ],
                "Up": [
                    7.549819258656498e-08,
                    1.0000009536743164,
                    -6.03497483098181e-07
                ],
                "At": [
                    -1.0,
                    7.54978870531886e-08,
                    -4.0133929246621847e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_WALL",
                "UserData": 51,
                "Position": [
                    28.000152587890625,
                    20.0,
                    -12.499980926513672
                ],
                "Up": [
                    -4.3711285258041244e-08,
                    1.0000009536743164,
                    -5.662445801135618e-07
                ],
                "At": [
                    -1.0,
                    -4.3711398944878965e-08,
                    -2.8212994607201836e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    40.000152587890625,
                    19.99993896484375,
                    -12.499935150146484
                ],
                "Up": [
                    4.371158723870394e-08,
                    1.0000009536743164,
                    -5.364422577258665e-07
                ],
                "At": [
                    1.0,
                    -4.3711374075883214e-08,
                    3.139165016818879e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_WINDOW",
                "UserData": 51,
                "Position": [
                    44.000274658203125,
                    19.99993133544922,
                    -20.499855041503906
                ],
                "Up": [
                    7.549812863771876e-08,
                    1.0000009536743164,
                    -6.03497483098181e-07
                ],
                "At": [
                    -1.0,
                    7.54978870531886e-08,
                    -2.821300029154372e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_WINDOW",
                "UserData": 51,
                "Position": [
                    44.00042724609375,
                    19.999435424804688,
                    -28.499900817871094
                ],
                "Up": [
                    1.9470775214358582e-07,
                    1.0000009536743164,
                    -6.258491680455336e-07
                ],
                "At": [
                    -1.0,
                    1.9470715528768778e-07,
                    -6.397579568329093e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_WALL",
                "UserData": 51,
                "Position": [
                    40.000244140625,
                    19.99993133544922,
                    -16.499855041503906
                ],
                "Up": [
                    1.5099615779945452e-07,
                    1.0000009536743164,
                    -5.96046959344676e-07
                ],
                "At": [
                    3.8941428215366614e-07,
                    -5.960464477539062e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_WALL",
                "UserData": 51,
                "Position": [
                    20.000244140625,
                    19.999908447265625,
                    -4.499933242797852
                ],
                "Up": [
                    -4.371134920688746e-08,
                    1.0000009536743164,
                    -5.513433620762953e-07
                ],
                "At": [
                    -1.0,
                    -4.3711395392165286e-08,
                    -1.629206565212371e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_WALL",
                "UserData": 51,
                "Position": [
                    -11.99969482421875,
                    19.99969482421875,
                    -4.499979019165039
                ],
                "Up": [
                    -7.549758151981223e-08,
                    1.0000009536743164,
                    -6.183987011354475e-07
                ],
                "At": [
                    1.0,
                    7.549792968575275e-08,
                    6.715442850691034e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^CUBEROOM_SPACE",
                "UserData": 0,
                "Position": [
                    40.00030517578125,
                    19.999549865722656,
                    -44.499847412109375
                ],
                "Up": [
                    1.9470780898700468e-07,
                    1.0000009536743164,
                    -6.258491680455336e-07
                ],
                "At": [
                    -1.0,
                    1.9470715528768778e-07,
                    -7.589672463836905e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^CUBEROOM_SPACE",
                "UserData": 0,
                "Position": [
                    40.000274658203125,
                    19.999557495117188,
                    -36.49983215332031
                ],
                "Up": [
                    1.9470795109555183e-07,
                    1.0000009536743164,
                    -6.183985874486098e-07
                ],
                "At": [
                    -1.0,
                    1.9470714107683307e-07,
                    -9.973857686418341e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_WALL",
                "UserData": 51,
                "Position": [
                    40.00030517578125,
                    19.999496459960938,
                    -32.49983215332031
                ],
                "Up": [
                    1.7881399116959074e-07,
                    1.0000009536743164,
                    -6.834696932855877e-07
                ],
                "At": [
                    1.1046699910366442e-06,
                    -6.834692953816557e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_WALL",
                "UserData": 51,
                "Position": [
                    32.000274658203125,
                    19.999588012695312,
                    -32.49992370605469
                ],
                "Up": [
                    8.94071234824878e-08,
                    1.0000009536743164,
                    -6.834698638158443e-07
                ],
                "At": [
                    8.662514687785006e-07,
                    -6.834692953816557e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_WALL",
                "UserData": 51,
                "Position": [
                    32.000274658203125,
                    19.99958038330078,
                    -56.4998779296875
                ],
                "Up": [
                    8.940713058791516e-08,
                    1.0000009536743164,
                    -7.15256362582295e-07
                ],
                "At": [
                    -6.705516284455371e-07,
                    7.152557373046875e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_WALL",
                "UserData": 51,
                "Position": [
                    28.00018310546875,
                    19.999610900878906,
                    -52.49989318847656
                ],
                "Up": [
                    1.6292122495542571e-07,
                    1.0000009536743164,
                    -6.332997486424574e-07
                ],
                "At": [
                    1.0,
                    -1.629206565212371e-07,
                    6.715444555993599e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_WINDOW",
                "UserData": 51,
                "Position": [
                    44.00030517578125,
                    19.999496459960938,
                    -36.49981689453125
                ],
                "Up": [
                    1.9470786583042354e-07,
                    1.0000009536743164,
                    -6.109478363214293e-07
                ],
                "At": [
                    -1.0,
                    1.9470714107683307e-07,
                    -8.781765359344718e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_WINDOW",
                "UserData": 51,
                "Position": [
                    44.000335693359375,
                    19.99951934814453,
                    -44.49983215332031
                ],
                "Up": [
                    1.9470780898700468e-07,
                    1.0000009536743164,
                    -6.183985874486098e-07
                ],
                "At": [
                    -1.0,
                    1.9470715528768778e-07,
                    -7.589672463836905e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^CUBEROOM_SPACE",
                "UserData": 0,
                "Position": [
                    -23.9998779296875,
                    19.99993133544922,
                    -20.49999237060547
                ],
                "Up": [
                    1.629209265274767e-07,
                    1.0000009536743164,
                    -4.842881935473997e-07
                ],
                "At": [
                    1.0,
                    -1.6292067073209182e-07,
                    1.947072689745255e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_CORR_A_GLAS",
                "UserData": 51,
                "Position": [
                    -23.999755859375,
                    19.999755859375,
                    -12.500011444091797
                ],
                "Up": [
                    4.371161921312705e-08,
                    1.000001072883606,
                    -6.258492248889524e-07
                ],
                "At": [
                    1.0,
                    -4.3711374075883214e-08,
                    3.139165016818879e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_WALL",
                "UserData": 51,
                "Position": [
                    -15.99981689453125,
                    19.99993133544922,
                    -16.499977111816406
                ],
                "Up": [
                    1.5099602990176209e-07,
                    1.0000009536743164,
                    -5.960470161880949e-07
                ],
                "At": [
                    1.509957741063772e-07,
                    -5.960464477539062e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_WALL",
                "UserData": 51,
                "Position": [
                    -19.99969482421875,
                    19.99969482421875,
                    -12.499980926513672
                ],
                "Up": [
                    -4.371119999291295e-08,
                    1.0000009536743164,
                    -6.258492248889524e-07
                ],
                "At": [
                    -1.0,
                    -4.371140605030632e-08,
                    -4.013392356227996e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_WINDOW",
                "UserData": 51,
                "Position": [
                    -27.9998779296875,
                    19.99993133544922,
                    -20.499977111816406
                ],
                "Up": [
                    1.629209265274767e-07,
                    1.0000009536743164,
                    -4.768376129504759e-07
                ],
                "At": [
                    1.0,
                    -1.6292067073209182e-07,
                    1.947072689745255e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_WINDOW",
                "UserData": 51,
                "Position": [
                    -27.999755859375,
                    19.999862670898438,
                    -28.499961853027344
                ],
                "Up": [
                    4.371167960925959e-08,
                    1.0000009536743164,
                    -6.109480068516859e-07
                ],
                "At": [
                    1.0,
                    -4.3711370523169535e-08,
                    4.3312579123266914e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_DOOR_A",
                "UserData": 51,
                "Position": [
                    -11.99981689453125,
                    19.999671936035156,
                    -44.49989318847656
                ],
                "Up": [
                    1.9470762424589338e-07,
                    1.0000009536743164,
                    -5.140904590916762e-07
                ],
                "At": [
                    -1.0,
                    1.9470715528768778e-07,
                    -5.20548667282128e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^CUBEROOM_SPACE",
                "UserData": 0,
                "Position": [
                    -23.99981689453125,
                    19.999671936035156,
                    -44.499908447265625
                ],
                "Up": [
                    1.6292096916004084e-07,
                    1.0000009536743164,
                    -4.768376129504759e-07
                ],
                "At": [
                    1.0,
                    -1.6292067073209182e-07,
                    3.1391655852530675e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^CUBEROOM_SPACE",
                "UserData": 0,
                "Position": [
                    -23.999755859375,
                    19.999832153320312,
                    -36.49995422363281
                ],
                "Up": [
                    4.371183237594778e-08,
                    1.0000009536743164,
                    -5.513433620762953e-07
                ],
                "At": [
                    1.0,
                    -4.371135275960114e-08,
                    7.907536314633035e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_WALL",
                "UserData": 51,
                "Position": [
                    -23.999755859375,
                    19.999862670898438,
                    -32.499969482421875
                ],
                "Up": [
                    2.980239699468257e-08,
                    1.0000009536743164,
                    -5.960470161880949e-07
                ],
                "At": [
                    -6.705515147586993e-07,
                    5.960464477539062e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_WALL",
                "UserData": 51,
                "Position": [
                    -15.999755859375,
                    19.999862670898438,
                    -32.49998474121094
                ],
                "Up": [
                    5.96046660916727e-08,
                    1.0000009536743164,
                    -5.960470161880949e-07
                ],
                "At": [
                    -4.917378646496218e-07,
                    5.960464477539062e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_WINDOW",
                "UserData": 51,
                "Position": [
                    -27.99981689453125,
                    19.999801635742188,
                    -36.499969482421875
                ],
                "Up": [
                    4.371186790308457e-08,
                    1.0000009536743164,
                    -5.215409828451811e-07
                ],
                "At": [
                    1.0,
                    -4.371134920688746e-08,
                    9.099629210140847e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_WINDOW",
                "UserData": 51,
                "Position": [
                    -27.9998779296875,
                    19.999671936035156,
                    -44.499908447265625
                ],
                "Up": [
                    1.6292095494918613e-07,
                    1.0000009536743164,
                    -4.3958470996585675e-07
                ],
                "At": [
                    1.0,
                    -1.6292067073209182e-07,
                    3.139165301035973e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_WALL",
                "UserData": 51,
                "Position": [
                    -15.999755859375,
                    19.999549865722656,
                    -56.49998474121094
                ],
                "Up": [
                    1.1920928244535389e-07,
                    1.0000009536743164,
                    -4.76837556107057e-07
                ],
                "At": [
                    -4.768365897689364e-07,
                    4.76837158203125e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_WALL",
                "UserData": 51,
                "Position": [
                    -11.99969482421875,
                    19.999488830566406,
                    -52.5
                ],
                "Up": [
                    1.9470762424589338e-07,
                    1.0000009536743164,
                    -5.28991563442105e-07
                ],
                "At": [
                    -1.0,
                    1.9470715528768778e-07,
                    -5.20548667282128e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^WALLLIGHTGREEN",
                "UserData": 0,
                "Position": [
                    63.925384521484375,
                    17.999752044677734,
                    -100.64047241210938
                ],
                "Up": [
                    5.604896796285175e-05,
                    -1.0000004768371582,
                    0.0005929726175963879
                ],
                "At": [
                    0.999716579914093,
                    4.191691186861135e-05,
                    -0.023805733770132065
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^WALLLIGHTGREEN",
                "UserData": 0,
                "Position": [
                    63.96466064453125,
                    17.999879837036133,
                    -76.3070068359375
                ],
                "Up": [
                    -0.009242457337677479,
                    -0.9998830556869507,
                    -0.009560671634972095
                ],
                "At": [
                    -0.9996203780174255,
                    0.008991003967821598,
                    0.026043759658932686
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^WALLLIGHTGREEN",
                "UserData": 0,
                "Position": [
                    -64.01925659179688,
                    18.000246047973633,
                    -76.3519287109375
                ],
                "Up": [
                    -0.008731698617339134,
                    -0.9999006986618042,
                    -0.00861343089491129
                ],
                "At": [
                    -0.9997835159301758,
                    0.008567332290112972,
                    0.018961889669299126
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^WALLLIGHTGREEN",
                "UserData": 0,
                "Position": [
                    -64.00399780273438,
                    18.000362396240234,
                    -100.71106719970703
                ],
                "Up": [
                    -0.001015090150758624,
                    -0.9998531937599182,
                    -0.014863484539091587
                ],
                "At": [
                    0.9976779222488403,
                    -4.042718160235381e-07,
                    -0.0681084468960762
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^WALLLIGHTGREEN",
                "UserData": 0,
                "Position": [
                    64.24517822265625,
                    10.160344123840332,
                    -75.33308410644531
                ],
                "Up": [
                    0.0032800883054733276,
                    -0.9999353885650635,
                    -0.009363432414829731
                ],
                "At": [
                    0.9993758201599121,
                    0.002948582638055086,
                    0.035206008702516556
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^WALLLIGHTGREEN",
                "UserData": 0,
                "Position": [
                    64.07504272460938,
                    10.160149574279785,
                    -101.65812683105469
                ],
                "Up": [
                    0.0014308721292763948,
                    -0.9999827146530151,
                    -0.0050455681048333645
                ],
                "At": [
                    0.9996791481971741,
                    0.0015580004546791315,
                    -0.02528170682489872
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_WINDOW",
                "UserData": 51,
                "Position": [
                    28.000396728515625,
                    4.000249862670898,
                    -52.499847412109375
                ],
                "Up": [
                    1.6292143811824644e-07,
                    1.0000009536743164,
                    -5.736949901802291e-07
                ],
                "At": [
                    1.0,
                    -1.6292062809952768e-07,
                    1.148381556959066e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1721851818,
                "ObjectID": "^S_LANDINGZONE",
                "UserData": 0,
                "Position": [
                    -0.9255599975585938,
                    4.000688076019287,
                    -92.37480926513672
                ],
                "Up": [
                    -7.907530630291149e-07,
                    1.0000009536743164,
                    -7.58968667469162e-07
                ],
                "At": [
                    1.0,
                    7.907536883067223e-07,
                    1.863636725829565e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1721851818,
                "ObjectID": "^S_LANDINGZONE",
                "UserData": 0,
                "Position": [
                    -38.425559997558594,
                    4.000688076019287,
                    -92.37480926513672
                ],
                "Up": [
                    -7.907530630291149e-07,
                    1.0000009536743164,
                    -7.58968667469162e-07
                ],
                "At": [
                    1.0,
                    7.907536883067223e-07,
                    1.863636725829565e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1721851818,
                "ObjectID": "^S_LANDINGZONE",
                "UserData": 0,
                "Position": [
                    -38.425559997558594,
                    4.000688076019287,
                    -92.37480926513672
                ],
                "Up": [
                    -7.907530630291149e-07,
                    1.0000009536743164,
                    -7.58968667469162e-07
                ],
                "At": [
                    1.0,
                    7.907536883067223e-07,
                    1.863636725829565e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^WALLLIGHTGREEN",
                "UserData": 0,
                "Position": [
                    -42.121910095214844,
                    14.089548110961914,
                    -113.74557495117188
                ],
                "Up": [
                    -1.0728836059570312e-06,
                    1.9470742529392737e-07,
                    1.0000011920928955
                ],
                "At": [
                    1.86276971625432e-09,
                    -1.0,
                    1.9470719792025193e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1721851818,
                "ObjectID": "^S_LANDINGZONE",
                "UserData": 0,
                "Position": [
                    36.574440002441406,
                    4.000688076019287,
                    -92.37480926513672
                ],
                "Up": [
                    -7.907530630291149e-07,
                    1.0000009536743164,
                    -7.58968667469162e-07
                ],
                "At": [
                    1.0,
                    7.907536883067223e-07,
                    1.863636725829565e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1721852548,
                "ObjectID": "^BASE_BEAMSTONE",
                "UserData": 0,
                "Position": [
                    -38.425559997558594,
                    1.5006873607635498,
                    -92.37480926513672
                ],
                "Up": [
                    7.907543704277487e-07,
                    1.0000009536743164,
                    -4.371073814013471e-08
                ],
                "At": [
                    -1.0,
                    7.907535746198846e-07,
                    -1.712641392259684e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1721852548,
                "ObjectID": "^BASE_BEAMSTONE",
                "UserData": 0,
                "Position": [
                    -38.425559997558594,
                    1.5006873607635498,
                    -92.37480926513672
                ],
                "Up": [
                    7.907543704277487e-07,
                    1.0000009536743164,
                    -4.371073814013471e-08
                ],
                "At": [
                    -1.0,
                    7.907535746198846e-07,
                    -1.712641392259684e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1721852548,
                "ObjectID": "^BASE_BEAMSTONE",
                "UserData": 0,
                "Position": [
                    -48.08550262451172,
                    1.5006988048553467,
                    -22.900991439819336
                ],
                "Up": [
                    7.907543704277487e-07,
                    1.0000009536743164,
                    -4.371073814013471e-08
                ],
                "At": [
                    -1.0,
                    7.907535746198846e-07,
                    -1.712641392259684e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1721852548,
                "ObjectID": "^BASE_BEAMSTONE",
                "UserData": 0,
                "Position": [
                    36.574440002441406,
                    1.5006873607635498,
                    -92.37480926513672
                ],
                "Up": [
                    7.907543704277487e-07,
                    1.0000009536743164,
                    -4.371073814013471e-08
                ],
                "At": [
                    -1.0,
                    7.907535746198846e-07,
                    -1.712641392259684e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1721852548,
                "ObjectID": "^BASE_BEAMSTONE",
                "UserData": 0,
                "Position": [
                    -0.9255599975585938,
                    1.5006873607635498,
                    -92.37480926513672
                ],
                "Up": [
                    7.907543704277487e-07,
                    1.0000009536743164,
                    -4.371073814013471e-08
                ],
                "At": [
                    -1.0,
                    7.907535746198846e-07,
                    -1.712641392259684e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1721934877,
                "ObjectID": "^PANEL_GLASS",
                "UserData": 0,
                "Position": [
                    34.39076232910156,
                    28.626035690307617,
                    -116.50021362304688
                ],
                "Up": [
                    -7.907536314633035e-07,
                    1.0000009536743164,
                    -5.801542783956393e-07
                ],
                "At": [
                    1.0,
                    7.907536883067223e-07,
                    1.3867996813132777e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^U_PARAGON",
                "UserData": 4294967296000000,
                "Position": [
                    0.0,
                    0.0,
                    0.0
                ],
                "Up": [
                    -2.9802322387695312e-08,
                    1.0,
                    -3.5762786865234375e-07
                ],
                "At": [
                    8.881782608814476e-16,
                    3.5762786865234375e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^WALLLIGHTGREEN",
                "UserData": 0,
                "Position": [
                    -64.03475952148438,
                    10.159539222717285,
                    -101.66636657714844
                ],
                "Up": [
                    0.0007143429829739034,
                    -0.9999918341636658,
                    -0.003647568402811885
                ],
                "At": [
                    0.994133710861206,
                    0.0011046568397432566,
                    -0.10815300792455673
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^WALLLIGHTGREEN",
                "UserData": 0,
                "Position": [
                    -64.04995727539062,
                    10.159855842590332,
                    -75.39889526367188
                ],
                "Up": [
                    0.00013074981688987464,
                    -1.0000001192092896,
                    -0.0012110070092603564
                ],
                "At": [
                    0.9999675154685974,
                    0.000140503587317653,
                    -0.008057770319283009
                ],
                "Message": ""
            },
            {
                "Timestamp": 1721936156,
                "ObjectID": "^PANEL_GLASS",
                "UserData": 0,
                "Position": [
                    -36.06072235107422,
                    9.74958610534668,
                    -116.50019073486328
                ],
                "Up": [
                    -4.396429176267702e-07,
                    2.835585832595825,
                    -1.926760705828201e-05
                ],
                "At": [
                    9.740283246628678e-09,
                    -6.794929959141882e-06,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1721936156,
                "ObjectID": "^PANEL_GLASS",
                "UserData": 0,
                "Position": [
                    -24.036212921142578,
                    9.749622344970703,
                    -116.50019073486328
                ],
                "Up": [
                    -4.396429176267702e-07,
                    2.835585832595825,
                    -1.926760705828201e-05
                ],
                "At": [
                    9.740283246628678e-09,
                    -6.794929959141882e-06,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1721936156,
                "ObjectID": "^PANEL_GLASS",
                "UserData": 0,
                "Position": [
                    -12.011730194091797,
                    9.749653816223145,
                    -116.50019073486328
                ],
                "Up": [
                    -4.396429176267702e-07,
                    2.835585832595825,
                    -1.926760705828201e-05
                ],
                "At": [
                    9.740283246628678e-09,
                    -6.794929959141882e-06,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1721936156,
                "ObjectID": "^PANEL_GLASS",
                "UserData": 0,
                "Position": [
                    0.012765597552061081,
                    9.749686241149902,
                    -116.50020599365234
                ],
                "Up": [
                    -4.396429176267702e-07,
                    2.835585832595825,
                    -1.926760705828201e-05
                ],
                "At": [
                    9.740283246628678e-09,
                    -6.794929959141882e-06,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1721936156,
                "ObjectID": "^PANEL_GLASS",
                "UserData": 0,
                "Position": [
                    12.037261962890625,
                    9.749719619750977,
                    -116.50020599365234
                ],
                "Up": [
                    -4.396429176267702e-07,
                    2.835585832595825,
                    -1.926760705828201e-05
                ],
                "At": [
                    9.740283246628678e-09,
                    -6.794929959141882e-06,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1721936156,
                "ObjectID": "^PANEL_GLASS",
                "UserData": 0,
                "Position": [
                    24.061758041381836,
                    9.749752044677734,
                    -116.50020599365234
                ],
                "Up": [
                    -4.396429176267702e-07,
                    2.835585832595825,
                    -1.926760705828201e-05
                ],
                "At": [
                    9.740283246628678e-09,
                    -6.794929959141882e-06,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1721936156,
                "ObjectID": "^PANEL_GLASS",
                "UserData": 0,
                "Position": [
                    36.08623504638672,
                    9.749786376953125,
                    -116.50020599365234
                ],
                "Up": [
                    -4.396429176267702e-07,
                    2.835585832595825,
                    -1.926760705828201e-05
                ],
                "At": [
                    9.740283246628678e-09,
                    -6.794929959141882e-06,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^WALLLIGHTGREEN",
                "UserData": 0,
                "Position": [
                    -40.05766296386719,
                    18.000396728515625,
                    -114.96707153320312
                ],
                "Up": [
                    -5.396088340603455e-07,
                    -1.0000011920928955,
                    1.598637453525953e-07
                ],
                "At": [
                    0.9919448494911194,
                    -5.150116066943156e-07,
                    0.1266704797744751
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^WALLLIGHTGREEN",
                "UserData": 0,
                "Position": [
                    -40.98486328125,
                    14.23855972290039,
                    -115.00338745117188
                ],
                "Up": [
                    1.0000011920928955,
                    -6.278336286413833e-07,
                    9.099641147258808e-07
                ],
                "At": [
                    -6.278331170506135e-07,
                    -1.0,
                    2.309680127154934e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^WALLLIGHTGREEN",
                "UserData": 0,
                "Position": [
                    -40.29682922363281,
                    10.25693130493164,
                    -115.08197021484375
                ],
                "Up": [
                    1.0000011920928955,
                    -6.278336286413833e-07,
                    9.099641147258808e-07
                ],
                "At": [
                    -6.278331170506135e-07,
                    -1.0,
                    2.309680127154934e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^WALLLIGHTGREEN",
                "UserData": 0,
                "Position": [
                    39.959716796875,
                    18.000579833984375,
                    -115.51123046875
                ],
                "Up": [
                    -1.12752150016604e-06,
                    -0.9999728202819824,
                    -2.6856085355575487e-08
                ],
                "At": [
                    0.9769112467765808,
                    -1.1072562529079732e-06,
                    0.21364541351795197
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^WALLLIGHTGREEN",
                "UserData": 0,
                "Position": [
                    40.97541809082031,
                    14.16006851196289,
                    -115.02676391601562
                ],
                "Up": [
                    -0.0008366405963897705,
                    6.6320162659394555e-06,
                    1.0000008344650269
                ],
                "At": [
                    9.266271083774313e-11,
                    -1.0,
                    6.632011263718596e-06
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^WALLLIGHTGREEN",
                "UserData": 0,
                "Position": [
                    40.18601989746094,
                    9.95029067993164,
                    -115.05606079101562
                ],
                "Up": [
                    1.0678861599444645e-06,
                    1.000001072883606,
                    3.179325176461134e-07
                ],
                "At": [
                    0.8936119079589844,
                    -1.0969755521728075e-06,
                    0.4488404393196106
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^WALLLIGHTGREEN",
                "UserData": 0,
                "Position": [
                    42.13890075683594,
                    14.122171401977539,
                    -113.74588012695312
                ],
                "Up": [
                    -1.4603135696233949e-06,
                    1.3113429986333358e-07,
                    1.0000009536743164
                ],
                "At": [
                    1.1175840697319472e-08,
                    -1.0,
                    1.3113418617649586e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^U_MINIPORTAL",
                "UserData": 0,
                "Position": [
                    3.4987945556640625,
                    3.9960172176361084,
                    -66.92608642578125
                ],
                "Up": [
                    7.182661221349917e-08,
                    1.0000009536743164,
                    -1.36402860562157e-07
                ],
                "At": [
                    -0.9991902112960815,
                    7.725667217073351e-08,
                    0.040235936641693115
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^U_MINIPORTAL",
                "UserData": 0,
                "Position": [
                    2.5841827392578125,
                    3.458491563796997,
                    25.01458740234375
                ],
                "Up": [
                    -1.1289216672594193e-08,
                    1.0000008344650269,
                    -1.9057084443829808e-07
                ],
                "At": [
                    -0.9748868346214294,
                    -5.344594811163006e-08,
                    -0.22270084917545319
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^U_PORTALLINE",
                "UserData": 0,
                "Position": [
                    4.3872528076171875,
                    5.5897746086120605,
                    -66.96185302734375
                ],
                "Up": [
                    -5.922262425883673e-05,
                    0.9999840259552002,
                    0.005830673035234213
                ],
                "At": [
                    -0.9463717341423035,
                    -0.5433334708213806,
                    93.17428588867188
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_FLEET",
                "UserData": 51,
                "Position": [
                    -24.0,
                    4.000002384185791,
                    19.5
                ],
                "Up": [
                    4.470344094897882e-08,
                    1.0000009536743164,
                    -5.960470161880949e-07
                ],
                "At": [
                    8.195630840646118e-08,
                    5.960464477539062e-07,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_ROOM_TECH",
                "UserData": 51,
                "Position": [
                    -7.99993896484375,
                    3.999760150909424,
                    35.49989318847656
                ],
                "Up": [
                    -1.0430801467009587e-07,
                    1.000001072883606,
                    -4.4505114260573464e-07
                ],
                "At": [
                    3.894144242622133e-07,
                    -4.450506310149649e-07,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^U_PARAGON",
                "UserData": 4294967296000000,
                "Position": [
                    0.0,
                    0.0,
                    0.0
                ],
                "Up": [
                    4.440891304407238e-16,
                    1.0,
                    -7.450580152834618e-09
                ],
                "At": [
                    -5.960463766996327e-08,
                    7.450580152834618e-09,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^U_PARAGON",
                "UserData": 4294967296000000,
                "Position": [
                    0.0,
                    0.0,
                    0.0
                ],
                "Up": [
                    4.440891304407238e-16,
                    1.0,
                    -7.450580152834618e-09
                ],
                "At": [
                    -5.960463766996327e-08,
                    7.450580152834618e-09,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^U_PARAGON",
                "UserData": 4294967296000000,
                "Position": [
                    0.0,
                    0.0,
                    0.0
                ],
                "Up": [
                    4.440891304407238e-16,
                    1.0,
                    -7.450580152834618e-09
                ],
                "At": [
                    -5.960463766996327e-08,
                    7.450580152834618e-09,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^U_PARAGON",
                "UserData": 4294967296000000,
                "Position": [
                    0.0,
                    0.0,
                    0.0
                ],
                "Up": [
                    4.440891304407238e-16,
                    1.0,
                    -7.450580152834618e-09
                ],
                "At": [
                    -5.960463766996327e-08,
                    7.450580152834618e-09,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^U_PARAGON",
                "UserData": 4294967296000000,
                "Position": [
                    0.0,
                    0.0,
                    0.0
                ],
                "Up": [
                    4.440891304407238e-16,
                    1.0,
                    -7.450580152834618e-09
                ],
                "At": [
                    -5.960463766996327e-08,
                    7.450580152834618e-09,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^U_PARAGON",
                "UserData": 4294967296000000,
                "Position": [
                    0.0,
                    0.0,
                    0.0
                ],
                "Up": [
                    4.440891304407238e-16,
                    1.0,
                    -7.450580152834618e-09
                ],
                "At": [
                    -5.960463766996327e-08,
                    7.450580152834618e-09,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^U_PARAGON",
                "UserData": 4294967296000000,
                "Position": [
                    0.0,
                    0.0,
                    0.0
                ],
                "Up": [
                    4.440891304407238e-16,
                    1.0,
                    -7.450580152834618e-09
                ],
                "At": [
                    -5.960463766996327e-08,
                    7.450580152834618e-09,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^U_PARAGON",
                "UserData": 4294967296000000,
                "Position": [
                    0.0,
                    0.0,
                    0.0
                ],
                "Up": [
                    -2.9802322387695312e-08,
                    1.0,
                    1.1175870007207322e-08
                ],
                "At": [
                    -2.60770320892334e-08,
                    -1.1175870895385742e-08,
                    1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_DOOR_A",
                "UserData": 51,
                "Position": [
                    -11.999755859375,
                    19.99951171875,
                    -60.50006103515625
                ],
                "Up": [
                    1.49011640360186e-07,
                    1.0000011920928955,
                    -5.513429073289444e-07
                ],
                "At": [
                    -1.0,
                    1.490111856128351e-07,
                    -5.215400733504794e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_DOOR_A",
                "UserData": 51,
                "Position": [
                    28.000244140625,
                    19.999542236328125,
                    -60.49981689453125
                ],
                "Up": [
                    8.940699558479537e-08,
                    1.0000011920928955,
                    -6.854533580735733e-07
                ],
                "At": [
                    1.0,
                    -8.94064697831709e-08,
                    6.109469268267276e-07
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^FRE_FACE_DOOR_A",
                "UserData": 51,
                "Position": [
                    0.00042724609375,
                    20.0006103515625,
                    -112.50019836425781
                ],
                "Up": [
                    8.940697853176971e-07,
                    1.0000011920928955,
                    -8.94069742685133e-08
                ],
                "At": [
                    1.3262017546367133e-06,
                    -8.940805429347165e-08,
                    -1.0
                ],
                "Message": ""
            },
            {
                "Timestamp": 1728534512,
                "ObjectID": "^U_MINIPORTAL",
                "UserData": 0,
                "Position": [
                    2.0981597900390625,
                    4.11676025390625,
                    43.67999267578125
                ],
                "Up": [
                    -2.945091281958412e-08,
                    1.000001072883606,
                    -2.6677874132019497e-08
                ],
                "At": [
                    -0.99373459815979,
                    -2.6284698861900324e-08,
                    0.11176547408103943
                ],
                "Message": ""
            }
        ],
        "RID": "",
        "Owner": {
            "LID": "76561199060525572",
            "UID": "76561199060525572",
            "USN": "BigBuffaloBill",
            "PTK": "ST",
            "TS": 1653475528
        },
        "Name": "",
        "BaseType": {
            "PersistentBaseTypes": "FreighterBase"
        },
        "LastEditedById": "",
        "LastEditedByUsername": "",
        "ScreenshotAt": [
            0.0,
            0.0,
            0.0
        ],
        "ScreenshotPos": [
            0.0,
            0.0,
            0.0
        ],
        "GameMode": {
            "PresetGameMode": "Normal"
        },
        "Difficulty": {
            "DifficultyPreset": {
                "DifficultyPresetType": "Custom"
            },
            "PersistentBaseDifficultyFlags": 0
        },
        "PlatformToken": "",
        "IsReported": false,
        "IsFeatured": false,
        "AutoPowerSetting": {
            "BaseAutoPowerSetting": "UseDefault"
        }
    }
]"""  

   