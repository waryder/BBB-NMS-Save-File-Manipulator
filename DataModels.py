from imports import *
from IniFileManager import *

global INIT_BASE_TEXT
global INIT_STARSHIP_TEXT    

# Parent Class: DataModel
class DataModel(QObject):
    # Define the signal to be emitted when text changes (can be inherited)
    # (Dude I don't know. Python wants this out here even though it is treated like an instance variable
    # when declared this way. ChatGPT couldn't explain it to me. Just know: this thing is treated like
    # an instance variable for the life of the app:
    modelChanged = pyqtSignal()
    
    
    def __init__(self, last_working_file_path):
        logger.debug("DataModel(QObject).__init__ ENTER")
        super().__init__()
        self.model_data = None
        
        #self.last_file_path = ini_file_manager.get_last_working_file_path()
        self.last_file_path = last_working_file_path
        
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
    def __init__(self, last_working_file_path, INIT_TEXT = None):
        logger.debug("JsonArrayModel(DataModel).__init__ ENTER")
        self.INIT_TEXT=INIT_TEXT
        super().__init__(last_working_file_path)
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
                new_model_data = json.loads(self.INIT_TEXT)
        else:
            # Fall back to INIT_TEXT if no file path is found or the file doesn't exist
            new_model_data = json.loads(self.INIT_TEXT)            
            
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
        
