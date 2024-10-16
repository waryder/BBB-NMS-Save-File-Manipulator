from imports import *

class BaseTabContent(QWidget):
    
    
    def __init__(self, model, text_edit):
        super().__init__()
        self.model = model
        self.text_edit = text_edit
                        
    def update_text_widget_from_model(self):
        pass

    def text_changed_signal(self):
        logger.debug("1st Tab text_changed_signal() enter")        
        self.update_tree_synced_indicator(False)
        logger.debug("1st Tab text_changed_signal() exit") 
        
    def blockSignals(self):
        pass
        
    def unblockSignals(self):
        pass  

    def copy_to_clipboard(self, parentWindow = None):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.text_edit.toPlainText())
        QMessageBox.information(parentWindow, "Copied", "Text copied to clipboard!")  

    # Function to update the indicator color (red or green)
    def update_status_indicator_to_green(self, green_if_true, context):
        logger.debug(f"update_status_indicator_to_green() ENTER, green?: {green_if_true}, context: {context}")
        palette = self.status_indicator.palette()
        
        if green_if_true:
            logger.verbose("green")
            self.status_indicator.setStyleSheet(f"background-color: {GREEN_LED_COLOR}; border-radius: 4px;")
        else:
            logger.verbose("yellow")
            self.status_indicator.setStyleSheet(f"background-color: {YELLOW_LED_COLOR}; border-radius: 4px;")
            
        self.status_indicator.setPalette(palette)
        self.status_indicator.update()
        logger.verbose("update_status_indicator_to_green() EXIT")  

    def set_led_based_on_app_thread_load(self, max_threads = 3, context="none"):
        logger.debug(f"set_led_based_on_app_thread_load() ENTER, max_threads: {max_threads}, context: {context}")
        
        def run():
            nonlocal max_threads
            logger.verbose("1st tab set_led_based_on_app_thread_load() ENTER")
            
            #4 comes from testing the idle state of the app informally:
            num_threads = get_num_app_child_threads()
            logger.verbose(f"max_threads: {max_threads}, num_threads: {num_threads}")
                
            if num_threads > max_threads:
                #set the led yellow:
                self.update_status_indicator_to_green(False, context)
                
                QTimer.singleShot(2000, run)
                logger.verbose("1st tab set_led_based_on_app_thread_load() EXIT, yellow\n")
            else:    
                #set the led green:        
                self.update_status_indicator_to_green(True,context)
                logger.verbose("1st tab set_led_based_on_app_thread_load() EXIT, green\n")            
        
        #wait 2 seconds on the first run:
        QTimer.singleShot(2000, run)
        logger.verbose("set_led_based_on_app_thread_load() EXIT") 

        