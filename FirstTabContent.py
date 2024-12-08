from BaseTabContent import *
from CustomTreeWidget import *
from CustomTextEdit import *
from TextSearchDialog import *
from IniFileManager import *
from DataModels import *

class FirstTabContent(BaseTabContent):
    def __init__(self, parent=None):
        self.main_window = parent
        self.text_edit = None
        super().__init__(parent, 'tab1', self.text_edit)
        self.ini_file_manager = ini_file_manager 
        self.init_ui()

    def init_ui(self):
        self.search_dialog = None

        left_container = self.initLeftPane()
        right_container = self.initRightPane()

#Set up the main window:
        self.splitter = QSplitter(Qt.Horizontal)  # Set the orientation to horizontal

        # Add both containers to the splitter
        self.splitter.addWidget(left_container)
        self.splitter.addWidget(right_container)

        # Set initial splitter size ratios (optional)
        self.splitter.setStretchFactor(0, 5)
        self.splitter.setStretchFactor(1, 7)

        # Set the splitter as the main layout for the widget
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.splitter)

        # Set the layout to the widget
        self.setLayout(main_layout)

        # Connect buttons to methods
        self.sync_tree_from_text_window_button.clicked.connect(self.sync_tree_from_text_window)
        self.sort_bases_by_gal_sys_name_button.clicked.connect(self.sort_bases_by_gal_sys_name)
        self.import_button.clicked.connect(lambda: self.paste_to_text_window(self))
        self.export_button.clicked.connect(lambda: self.copy_to_clipboard(self))
        self.pretty_print_button.clicked.connect(lambda: self.pretty_print_text_widget(self.model, self))
        
        # Update tree from model
        self.update_tree_from_model()
        self.tree_widget.expand_tree_to_level(1)

        #this is to update the model on each character input.
        self.text_edit.textChanged.connect(self.text_changed_signal)

        #if anything in here causes a model change this will update the tree and text windows
        self.model.modelChanged.connect(self.model_changed)

    def initLeftPane(self):
        # left pane:
        self.sync_tree_from_text_window_button = QPushButton("Sync from Text Window")
        self.sync_tree_from_text_window_button.setFixedWidth(self.button_width)

        # Sort button
        self.sort_bases_by_gal_sys_name_button = QPushButton("Sort By Gal, Sys, Name")
        self.sort_bases_by_gal_sys_name_button.setFixedWidth(self.button_width)

        # Checkbox for "Move Freighter to Top"
        self.move_freighter_to_top_checkbox = QCheckBox("Move Freighter to Top on Sort")
        self.move_freighter_to_top_checkbox.stateChanged.connect(self.handle_move_freighter_to_top_checkbox)

        # Create tree widget and text edit
        self.tree_widget = CustomTreeWidget(self)
        self.tree_widget.setHeaderHidden(True)

        self.bottom_left_label = QLabel("", self)

        # Indicator layout
        tree_synced_indicator_layout = QHBoxLayout()
        tree_synced_indicator_layout.addWidget(self.tree_synced_label)
        tree_synced_indicator_layout.addWidget(self.tree_synced_indicator)

        # Create layout for the buttons to be horizontal
        left_buttons_lo = QHBoxLayout()
        left_buttons_lo.addWidget(self.sync_tree_from_text_window_button)
        left_buttons_lo.addLayout(tree_synced_indicator_layout)
        left_buttons_lo.addWidget(self.sort_bases_by_gal_sys_name_button)
        left_buttons_lo.addWidget(self.move_freighter_to_top_checkbox)

        # Set alignment
        left_buttons_lo.setAlignment(Qt.AlignLeft)

        # Create a vertical layout for the left side and add buttons layout
        left_pane_layout = QVBoxLayout()
        left_pane_layout.addLayout(left_buttons_lo)
        left_pane_layout.addWidget(self.tree_widget)
        left_pane_layout.addWidget(self.bottom_left_label)

        # Create left container
        left_container = QWidget()
        left_container.setLayout(left_pane_layout)

        self.move_freighter_to_top_checkbox.setChecked(True)

        return left_container

    # Stub function to handle checkbox state change
    def handle_move_freighter_to_top_checkbox(self, state):
        if state == Qt.Checked:
            self.move_freighter_to_top = True
        else:
            self.move_freighter_to_top = False

    def initRightPane(self):
        # right pane:
        self.right_button = QPushButton("Synch from Tree Window")
        self.right_button.setFixedWidth(self.button_width)
        ###
        self.export_button = QPushButton("Export to Clipboard")
        self.export_button.setFixedWidth(self.button_width)
        ###
        self.import_button = QPushButton("Import from Clipboard")
        self.import_button.setFixedWidth(self.button_width)
        ###
        self.pretty_print_button = QPushButton("Pretty Print")  # New button for copying text
        self.pretty_print_button.setFixedWidth(self.button_width)
        ###
        self.text_edit = CustomTextEdit(self)

        # Customize the palette to keep the selection highlighted when the window loses focus.
        # This also solved that on search, the found text was not highlighting. I didn't track down
        # the root cause of that since changing the default behavior of not highlighting on loss of focus
        # is what I want anyhow and solves that original issue.
        palette = self.text_edit.palette()
        palette.setColor(QPalette.Inactive, QPalette.Highlight, palette.color(QPalette.Active, QPalette.Highlight))
        palette.setColor(QPalette.Inactive, QPalette.HighlightedText,
                         palette.color(QPalette.Active, QPalette.HighlightedText))
        self.text_edit.setPalette(palette)

        # Enable custom context menu
        self.text_edit.setContextMenuPolicy(Qt.CustomContextMenu)
        self.text_edit.customContextMenuRequested.connect(self.show_context_menu)

        self.text_edit.setPlainText(self.view.get_text())

        # added just to keep spacing consistent with left panel:
        self.bottom_right_label = QLabel("", self)

        right_pane_layout = QVBoxLayout()
        right_button_layout = QHBoxLayout()
        right_button_layout.setAlignment(Qt.AlignLeft)
        # right_button_layout.setSpacing(2)

        # right_button_layout.addWidget(self.import_button)
        # right_button_layout.addWidget(self.export_button)
        right_button_layout.addWidget(self.pretty_print_button)

        right_pane_layout.addLayout(right_button_layout)
        right_pane_layout.addWidget(self.text_edit)
        right_pane_layout.addWidget(self.bottom_right_label)

        right_container = QWidget()
        right_container.setLayout(right_pane_layout)

        return right_container
                       
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

    def repaint_tree(self):
        logger.debug(f"repainting tree...")
        self.tree_widget.repaint()
        
    def sort_bases_by_gal_sys_name(self):
        logger.debug("1st tab Sort Bases clicked")
        self.main_window.background_processing_signal.emit(4, "tab1")
        self.update_tree_synced_indicator(False)

        model_json = self.view.get_json()

        model_json.sort(key=lambda el: (
            int(get_galaxy_system_planet_from_full_addr(el['GalacticAddress'])[GALAXY_FROM_GALACTIC_ADDR_IDX], 16) if el.get('GalacticAddress') else 0,  # default galaxy value
            int(get_galaxy_system_planet_from_full_addr(el['GalacticAddress'])[SYSTEM_FROM_GALACTIC_ADDR_IDX], 16) if el.get('GalacticAddress') else 0,  # default system value
            el['Name'] if el.get('Name') else ""  # default to empty string if 'Name' is missing
        ))    

        # Now loop through model_json and simulate the key generation for debug output
        #for el in model_json:
        #    galaxy_value = int(get_galaxy_system_planet_from_full_addr(el['GalacticAddress'])[GALAXY_FROM_GALACTIC_ADDR_IDX], 16) if el.get('GalacticAddress') else 0
        #    system_value = int(get_galaxy_system_planet_from_full_addr(el['GalacticAddress'])[SYSTEM_FROM_GALACTIC_ADDR_IDX], 16) if el.get('GalacticAddress') else 0
        #    name_value = el['Name'] if el.get('Name') else ""

        # Move the unnamed freighter base to the top if the checkbox is enabled
        if self.move_freighter_to_top:
            for i, el in enumerate(model_json):
                if not el.get('Name'): #if the base is unnamed it's a freighter base:
                    unnamed_freighter_base = model_json.pop(i)  # Remove it from the current position
                    model_json.insert(0, unnamed_freighter_base)  # Insert it at the top
                    break  # Stop after finding the first match
                    
        self.model.modelChanged.emit()

        QMessageBox.information(self, "Bases Sorted", "Base data has been sorted successfully!")

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
                    if(galaxy):
                        galaxy_name = GALAXIES[int(galaxy, 16)]
                    else:
                        galaxy_name = ""

                    system = get_galaxy_system_planet_from_full_addr(galactic_addr)[SYSTEM_FROM_GALACTIC_ADDR_IDX]
                    
                    item.setText(0, f"[{base_count - 1}] Dict ({size}) Gal name: {galaxy_name}, Sys: {system}, Base: {base_name}")
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
                #if( key == "Message" ):
                #    line_count += val.count('/w')
               
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