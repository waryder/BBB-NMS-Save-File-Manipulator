from imports import *
from PyQt5.QtWidgets import QCheckBox

class WhichStarshipsToUpgradeDialog(QDialog):
    def __init__(self, starship_names = None):
        self.starship_names = starship_names
        super().__init__()
        
        # Disable the question mark button
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        # Manually set the size of the dialog
        self.resize(400, 300)

        self.setWindowTitle('Which Starships Would You Like To Upgrade?')
        self.selected_items = []

        # Create layout for checkboxes
        layout = QVBoxLayout()

        label = QLabel("Please do not select any custom built or expedition Starships!!\nThis upgrade method will kill them!\n")
        # Make the label text bold
        font = QFont()
        font.setBold(True)
        label.setFont(font)
        label.setStyleSheet("padding-left: 10px;")
        layout.addWidget(label)

        # Create 12 checkboxes and add to layout
        self.checkboxes = []
        for index, starship_name in enumerate(self.starship_names):
            checkbox = QCheckBox(f"{starship_name}")
            checkbox.setProperty('starshipListIdx', index)
            checkbox.setStyleSheet("padding-left: 20px;")
            self.checkboxes.append(checkbox)
            layout.addWidget(checkbox)

        lineSpaceLabel = QLabel("")
        layout.addWidget(lineSpaceLabel)

        # Create OK and Cancel buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")

        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        # Connect buttons to actions
        ok_button.clicked.connect(self.on_ok)
        cancel_button.clicked.connect(self.reject)  # Reject closes the dialog without taking action

        # Add layouts to the main layout
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def on_ok(self):
        # Collect the labels of checked checkboxes
        #self.selected_items = [cb.text() for cb in self.checkboxes if cb.isChecked()]
        self.accept()  # Close the dialog and return with success

    def get_selected_items(self):
        return [checkbox for checkbox in self.checkboxes if checkbox.isChecked()]
        
        #return self.selected_items