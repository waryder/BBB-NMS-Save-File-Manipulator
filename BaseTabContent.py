from imports import *

class BaseTabContent(QWidget):
    def __init__(self, model):
        super().__init__()
        self.model = model
        
    def update_text_widget_from_model(self):
        pass

    def text_changed_signal(self):
        pass
        
    def blockSignals(self):
        pass
        
    def unblockSignals(self):
        pass        