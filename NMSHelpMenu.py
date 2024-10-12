#NMSHelpMenu.py

from imports import *

class NMSHelpMenu:
    def __init__(self, parent):
        # Parent is the main window instance
        self.parent = parent

    def create_help_menu(self, menubar):
        # Add the "Help" menu
        help_menu = menubar.addMenu('Help')

        # Create "Help" action
        help_action = QAction('Help', self.parent)
        help_action.triggered.connect(self.show_help_dialog)
        help_menu.addAction(help_action)

        # Create "Documentation" action
        doc_action = QAction('Documentation', self.parent)
        doc_action.triggered.connect(self.show_help_dialog)
        help_menu.addAction(doc_action)

    def show_help_dialog(self):
        # Open the help dialog (using QTextBrowser with navigation)
        dialog = NMSHelpDialog(self.parent)  # This is now NMSHelpDialog
        dialog.exec_()


class NMSHelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Help")

        # Create the QTextBrowser for displaying help content
        self.text_browser = QTextBrowser()

        # Load the main help page content
        self.load_main_page()

        # Connect link clicks to handle navigation using anchorClicked
        self.text_browser.anchorClicked.connect(self.handle_link)

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.text_browser)
        self.setLayout(layout)

    def load_main_page(self):
        self.text_browser.setHtml('''
            <h1>Main Help Page</h1>
            <p>Welcome to the main help section.</p>
            <p><a href="section1">Go to Section 1</a></p>
            <p><a href="section2">Go to Section 2</a></p>
        ''')

    def load_section1(self):
        self.text_browser.setHtml('''
            <h2>Section 1</h2>
            <p>This is the content of Section 1.</p>
            <p><a href="main">Back to Main Help</a></p>
        ''')

    def load_section2(self):
        self.text_browser.setHtml('''
            <h2>Section 2</h2>
            <p>This is the content of Section 2.</p>
            <p><a href="main">Back to Main Help</a></p>
        ''')

    def handle_link(self, url):
        link = url.toString()
        if link == "main":
            self.load_main_page()
        elif link == "section1":
            self.load_section1()
        elif link == "section2":
            self.load_section2()
