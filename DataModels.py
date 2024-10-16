from imports import *

global INIT_BASE_TEXT
global INIT_STARSHIP_TEXT    

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
    def __init__(self, ini_file_manager, INIT_TEXT = None):
        logger.debug("JsonArrayModel(DataModel).__init__ ENTER")
        self.INIT_TEXT=INIT_TEXT
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
        
class IniFileManager:
    def __init__(self, ini_file=None):
        """
        Initializes the IniFileManager class.
        :param ini_file: The path to the .ini file.
        """
        # Set the ini file path to be in the same directory as the script
        self.ini_file = os.path.join(os.path.dirname(__file__), ini_file)
        self.config = configparser.ConfigParser()
        
        #config = configparser.ConfigParser(allow_no_value=True)

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

    def get_reference_sentinel(self):
        return self.config.get('Preferences', 'reference_sentinel', fallback='')
        
    def get_reference_hauler(self):
        return self.config.get('Preferences', 'reference_hauler', fallback='')

    def get_reference_living(self):
        return self.config.get('Preferences', 'reference_living', fallback='')

    def get_reference_explorer(self):
        return self.config.get('Preferences', 'reference_explorer', fallback='')

    def get_reference_shuttle(self):
        return self.config.get('Preferences', 'reference_shuttle', fallback='')
       
    def get_reference_fighter(self):
        return self.config.get('Preferences', 'reference_fighter', fallback='')

    def get_reference_solar(self):
        return self.config.get('Preferences', 'reference_solar', fallback='')        

    def get_reference_royal(self):
        return self.config.get('Preferences', 'reference_royal', fallback='')        

      