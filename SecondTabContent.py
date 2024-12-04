#from imports import *
from BaseTabContent import *
from CustomTreeWidget import *
from CustomTextEdit import *
from WhichStarshipsToUpgradeDialog import *
from TextSearchDialog import *
from IniFileManager import *
#from DataModels import *
from DataViews import *

class SecondTabContent(BaseTabContent):
    def __init__(self, parent=None):
        self.main_window = parent
        self.text_edit = None
        super().__init__(parent, 'tab2', self.text_edit)
        self.ini_file_manager = ini_file_manager
        self.init_ui()

    def init_ui(self):
        self.search_dialog = None

        # Set static width for buttons
        #button_width = 140
                          
#left pane:
        self.sync_tree_from_text_window_button = QPushButton("Sync from Text Window")
        self.sync_tree_from_text_window_button.setFixedWidth(self.button_width)
###
        # Create the text label and indicator widget for Tree sync status
        #self.tree_synced_label = QLabel("Tree Synced:", self)  # Create a text label for "Status"
        #self.tree_synced_label.setFixedWidth(self.button_width - 75)
        
        #self.tree_synced = True
        #self.tree_synced_indicator = QWidget(self)  # Create a widget to represent the LED
        #self.tree_synced_indicator.setFixedSize(10, 10)  # Set size to small (like an LED)
        #self.tree_synced_indicator.setToolTip("Is tree synced from Text Window? Green=Yes. Red=No.")

        # Initially set the indicator to red (off) and make it circular
        #self.tree_synced_indicator.setStyleSheet(f"background-color: {GREEN_LED_COLOR}; border-radius: 4px;")
###
        self.upgrade_starships_button = QPushButton("Upgrade Starships")
        self.upgrade_starships_button.setFixedWidth(self.button_width)

        # Create tree widget and text edit
        #self.tree_widget = QTreeWidget()
        self.tree_widget = CustomTreeWidget(self)
        self.tree_widget.setHeaderHidden(True)
        
        self.bottom_left_label = QLabel("", self)
###        
        tree_synced_indicator_layout = QHBoxLayout()
        tree_synced_indicator_layout.addWidget(self.tree_synced_label)
        tree_synced_indicator_layout.addWidget(self.tree_synced_indicator)
###        
        # Create layout for the buttons to be horizontal
        left_buttons_lo = QHBoxLayout()
        left_buttons_lo.addWidget(self.sync_tree_from_text_window_button)
        left_buttons_lo.addLayout(tree_synced_indicator_layout)
        left_buttons_lo.addWidget(self.upgrade_starships_button)
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
        self.right_button.setFixedWidth(self.button_width)
###        
        self.export_button = QPushButton("Export to Clipboard")
        self.export_button.setFixedWidth(self.button_width)
###
        self.import_button = QPushButton("Import from Clipboard")
        self.import_button.setFixedWidth(self.button_width)
###
        self.pretty_print_button = QPushButton("Pretty Print")
        self.pretty_print_button.setFixedWidth(self.button_width)
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
                
        self.text_edit.setPlainText(self.view.get_text())

        #added just to keep spacing consistent with left panel:
        self.bottom_right_label = QLabel("", self)
        
        right_pane_layout = QVBoxLayout()
        right_button_layout = QHBoxLayout()
        right_button_layout.setAlignment(Qt.AlignLeft)
        #right_button_layout.setSpacing(2)
        
        #right_button_layout.addWidget(self.import_button)
        #right_button_layout.addWidget(self.export_button)
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
        self.splitter.setStretchFactor(1, 7)  # Right pane takes less space

        # Set the splitter as the main layout for the widget
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.splitter)

        # Set the layout to the widget
        self.setLayout(main_layout)

        # Connect buttons to methods
        self.sync_tree_from_text_window_button.clicked.connect(self.sync_tree_from_text_window)
        self.upgrade_starships_button.clicked.connect(self.upgrade_starships)
        self.import_button.clicked.connect(lambda: self.paste_to_text_window(self))
        self.export_button.clicked.connect(lambda: self.copy_to_clipboard(self))
        self.pretty_print_button.clicked.connect(lambda: self.pretty_print_text_widget(self.model, self))
        
        # Update tree from model
        self.update_tree_from_model()
        self.tree_widget.expand_tree_to_level(1)
        
        #this is to update the model on each charater input.
        self.text_edit.textChanged.connect(self.text_changed_signal)

        #if anything in here causes a model change this will update the tree and text windows
        self.model.modelChanged.connect(self.model_changed)
    
    def show_context_menu(self, position):
        logger.debug("2nd tab show_context_menu() ENTER")
        # Create the default context menu
        context_menu = self.text_edit.createStandardContextMenu()

        # Add a search option
        search_action = context_menu.addAction("Search Text")

        # Connect the search option to a function that performs the search
        search_action.triggered.connect(self.search_text)

        # Show the context menu
        context_menu.exec_(self.text_edit.mapToGlobal(position))
        logger.debug("2nd tab show_context_menu() ENTER")
        
    def search_text(self):       
        logger.debug("2nd tab search_text() ENTER")
        self.search_dialog = TextSearchDialog(self)
        self.search_dialog.show()
        logger.debug("2nd tab search_text() EXIT")

    def repaint_tree(self):
        logger.debug(f"repainting tree...")
        self.tree_widget.repaint()
        
    def return_json_from_file(self, filename):
        self.parent.ini_file_manager.ensure_persistent_file(filename)
        file_path = os.path.join(self.parent.ini_file_manager.get_persistent_dir(), filename)
        with open(file_path, 'r') as file:
            return json.loads(file.read())
        
    def upgrade_starships(self):
        logger.debug("2nd tab upgrade_starships() ENTER")

        model_json = copy.deepcopy(self.view.get_json())
        
        starship_names = []
        for starship_el in model_json:
            starship_names.append(starship_el['Name'])
       
        selected_checkboxes = []
        dialog = WhichStarshipsToUpgradeDialog(starship_names)
        if dialog.exec_() == QDialog.Accepted:
            selected_checkboxes = dialog.get_selected_items()
            self.main_window.background_processing_signal.emit(4, "tab2")
            self.update_tree_synced_indicator(False)
        else:
            return

        upgraded_starship_names = ""

        #for starship_el in model_json:
        if selected_checkboxes:                
            for checkbox in selected_checkboxes:
                starship_el = model_json[checkbox.property('starshipListIdx')]            
                
                name = copy.deepcopy(starship_el['Name'])
                upgraded_starship_names += f"\u2713 {name}\n"

                #need the second element of ['Seed'] here:
                seed = copy.deepcopy(starship_el['Resource']['Seed'][1])
                resource_filename = starship_el['Resource']['Filename']
                
                logger.debug(f"***name before: {name}") 
                logger.debug(f"   seed before: {seed}") 
                            
                reference = ""
                
                if "SENTINEL" in resource_filename:
                    reference = self.return_json_from_file('reference_sentinel.json')
                    logger.verbose(f"   ship_type: SENTINEL")
                
                elif "DROPSHIP" in resource_filename:
                    reference = self.return_json_from_file('reference_hauler.json')
                    logger.verbose(f"   ship_type: DROPSHIP")
                
                elif "BIOSHIP" in resource_filename: 
                    reference = self.return_json_from_file('reference_living.json')
                    logger.verbose(f"   ship_type: LIVING")

                elif "SCIENTIFIC" in resource_filename:
                    reference = self.return_json_from_file('reference_explorer.json')
                    logger.verbose(f"   ship_type: EXPLORER")                    

                elif "SHUTTLE" in resource_filename:                          
                    reference = self.return_json_from_file('reference_shuttle.json')
                    logger.verbose(f"   ship_type: SHUTTLE")
                    
                elif "FIGHTER" in resource_filename:
                    reference = self.return_json_from_file('reference_fighter.json')
                    logger.verbose(f"   ship_type: FIGHTER")
                
                elif "SAILSHIP" in resource_filename:
                    reference = self.return_json_from_file('reference_solar.json')
                    logger.verbose(f"   ship_type: SOLAR")

                elif "S-CLASS" in resource_filename:
                    reference = self.return_json_from_file('reference_royal.json')
                    logger.verbose(f"   ship_type: ROYAL")
                    
                else:
                    print ('ERROR')
                    
                #assuming we found a valid data for each starship. Shouldn't need to deep copy, really anywhere in here but something was screwing up, so it can't hurt anything either:
                starship_el = copy.deepcopy(reference)
                logger.verbose(f"   >>>name (reference ship's) after overwrite: {starship_el['Name']}")
                logger.verbose(f"   >>>seed (reference ship's) after overwrite: {starship_el['Resource']['Seed']}")
                
                starship_el['Name'] = name
                starship_el['Resource']['Seed'][1] = seed
                
                model_json[checkbox.property('starshipListIdx')] = starship_el
                
                #logger.verbose(json.dumps(starship_el,indent = 4) + ',')            
                
                logger.debug(f"   final name: {starship_el['Name']}")
                logger.debug(f"   final seed: {starship_el['Resource']['Seed']}")
            
            self.view.set_json(model_json)

            QMessageBox.information(None, "Starships Upgraded", "Your selected starships have been Upgraded:\n\n" + upgraded_starship_names)

        logger.debug("2nd tab upgrade_starships() EXIT")        
        
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
            json_text = self.view.get_text()

            if json_text:
                json_data = json.loads(json_text)
                return json_data
            else:
                return ""

        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON: {e}")
            return None        
            
    def clear_tree_view(self):
        logger.debug("2nd tab clear_tree_view() Called.")
        self.tree_widget.clear()        

    def populate_tree_from_json(self, json_data, parent_tree_node=None):
        #return
        logger.debug("2nd tab populate_tree_from_json() ENTER")

        starship_count = 0
        line_count = 0
        
        def parse_item(json_data, parent_tree_node, level):
            nonlocal starship_count
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

                #if he has children:    
                if json_data: 
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
                
                #if we are the top level node, assuming this is NMS starship data, add the base name data
                #to the top level node label text:
                
                if(level == 1 ):
                    # do this before we storage_container_count storage_container_name so we send it as a zero based idx:
                    #first arg needs to be the proper index into self.view.inventory_source_list for starships:
                    starship_name = self.view.get_storage_label_name_deep_copy(starship_count + 15, json_data)
                    starship_count += 1

                    item.setText(0, f"[{starship_count - 1}] Dict ({size})\t{starship_name}")
                else:
                    item.setText(0, f"Dict ({size})")                


                item.setData(0, QT_DATA_SAVE_NODES_DATA_STRUCT, {}) #add dict as parent json_data at this level
                line_count += 1
                item.setData(0, QT_DATA_LINE_COUNT, line_count) #store off the expected line number upon generation of the text from this this tree 
                               
                parent_tree_node.addChild(item)
                                
                #if he has children:    
                if json_data:               
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
        self.bottom_left_label.setText(f"Number of Starships: {starship_count}")
        
        logger.debug("2nd tab populate_tree_from_json() EXIT") 
  

    def init_text(self):
        return INIT_TEXT

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