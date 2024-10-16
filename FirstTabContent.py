#from imports import *
from BaseTabContent import *
from CustomTreeWidget import *
from CustomTextEdit import *
from DataModels import *
from TextSearchDialog import *

class FirstTabContent(BaseTabContent):
    def __init__(self, parent=None):
        self.main_window = parent        
        
        self.ini_file_manager = IniFileManager('app_preferences.ini')
        self.model = JsonArrayModel(self.ini_file_manager, self.init_text())
        
        super().__init__(self.model)        
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
        self.search_dialog = TextSearchDialog(self)
        self.search_dialog.show()
        logger.debug("search_text() EXIT")
        
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
        
        logger.debug("populate_tree_from_json() EXIT") 
        
    def init_text(self):
        return """[
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
]"""  

   