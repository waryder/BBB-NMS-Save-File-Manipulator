from imports import *
from NMSHelpMenu import NMSHelpMenu  
from FirstTabContent import FirstTabContent
from SecondTabContent import SecondTabContent
    


class MainWindow(QMainWindow):
    
    background_processing_signal = pyqtSignal(int, str)
    
    def __init__(self):
        logger.debug("MainWindow(QMainWindow).__init__ ENTER")
        super().__init__()
        
        self.tabs = QTabWidget()

        self.tab1 = FirstTabContent(self)
        self.tab2 = SecondTabContent(self)
        self.background_processing_signal.connect(self.tab1.set_led_based_on_app_thread_load)
        self.background_processing_signal.connect(self.tab2.set_led_based_on_app_thread_load)        

        self.tabs.addTab(self.tab1, 'Base Processing')
        self.tabs.addTab(self.tab2, 'Starship Processing')

        self.tabs.tabBarClicked.connect(self.before_tab_change)
        self.tabs.currentChanged.connect(self.after_tab_change)

        self.setCentralWidget(self.tabs)
        self.setWindowTitle('BBB NMS Save File Manipulator')
        self.setGeometry(400, 250, 1500, 800)

        self.create_menu_bar()
        
        self.background_processing_signal.emit(5, "Main Window")
        logger.debug("MainWindow(QMainWindow).__init__ EXIT")        

    def create_menu_bar(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu('File')

        open_action = QAction('Open', self)
        save_action = QAction('Save', self)
        save_as_action = QAction('Save As', self)
        
        open_action.triggered.connect(self.open_file)
        save_action.triggered.connect(self.save_file)
        save_as_action.triggered.connect(self.save_file_as)
        
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(save_as_action)
                
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

    def before_tab_change(self, index):
        logger.debug(f"before_tab_changed() enter, index: {index}")
        self.tab1.blockSignals() 
        self.tab2.blockSignals()
        logger.debug("before_tab_changed() exit")

    def after_tab_change(self, index):
        logger.debug(f"after_tab_changed() enter, index: {index}")
        self.tab1.unblockSignals() 
        self.tab2.unblockSignals()
        logger.debug("after_tab_changed() exit")        
        
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
    

if __name__ == '__main__':
    #yappi.start() 
    
    exit_code = main()
    sys.exit(exit_code)  # Ensure the program terminates correctly
    
   
    
    
    
