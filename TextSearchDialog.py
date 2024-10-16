from imports import *
from PyQt5.QtGui import QTextDocument 

class TextSearchDialog(QDialog):  # Change QWidget to QDialog
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.parentTab = parent        
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("Search Dialog")

        # Create a line edit for search input
        self.line_edit = QLineEdit(self)
        self.line_edit.setPlaceholderText("Enter search term")

        # Create buttons for search and cancel
        self.searchUp_button = QPushButton("Next Up", self)
        self.searchDown_button = QPushButton("Next Down", self)
        self.cancel_button = QPushButton("Close", self)

        # Layout to hold widgets
        layout = QVBoxLayout()
        layout.addWidget(self.line_edit)
        layout.addWidget(self.searchUp_button)
        layout.addWidget(self.searchDown_button)
        layout.addWidget(self.cancel_button)
        self.setLayout(layout)

        # Connect buttons to respective methods
        self.searchUp_button.clicked.connect(self.perform_upSearch)
        self.searchDown_button.clicked.connect(self.perform_downSearch)
        self.cancel_button.clicked.connect(self.reject)  # Use reject() for canceling
        
        self.current_search_string = ""
        self.last_cursor_position = None

    def perform_upSearch(self):
        search_string = self.line_edit.text()
        if search_string:
            self.current_search_string = search_string
            self.last_cursor_position = self.parentTab.text_edit.textCursor()
            self.find_next_occurrence("backward") 
        
    def perform_downSearch(self):
        search_string = self.line_edit.text()
        if search_string:
            self.current_search_string = search_string
            self.last_cursor_position = self.parentTab.text_edit.textCursor()
            self.find_next_occurrence("forward") 
        
    def find_next_occurrence(self, direction="forward"):
        logger.debug("find_occurrence() ENTER")
        """
        Searches for the next occurrence of the current search string in the given direction.
        Automatically wraps based on config.
        
        :param direction: "forward" to search down, "backward" to search up
        """
        if not self.current_search_string:
            return  # If no search string is set, return
        
        # Get the QTextDocument object
        document = self.parentTab.text_edit.document()
        
        # Determine search direction
        cursor = self.parentTab.text_edit.textCursor()
        
        if direction == "backward":
            cursor = document.find(self.current_search_string, cursor, QTextDocument.FindBackward)
        else:  # Default is forward
            cursor = document.find(self.current_search_string, cursor)
        
        # If occurrence not found and wrapping is enabled
        if cursor.isNull():
            self.parentTab.text_edit.setTextCursor(self.last_cursor_position)
            self.show_no_more_matches_dialog()
            return
    
        # Highlight the found occurrence and update the last cursor position
        self.parentTab.text_edit.setTextCursor(cursor)
        self.parentTab.text_edit.ensureCursorVisible()  # Scroll to make the found text visible
        self.last_cursor_position = self.parentTab.text_edit.textCursor()  # Update last position
        
        logger.debug("find_occurrence() EXIT")    


    # New method to show a dialog when no more matches are found
    def show_no_more_matches_dialog(self):
        """
        Shows a message box when no more occurrences of the search string are found.
        """
        QMessageBox.information(self, "End of Search", "No more occurrences found.")             