import sys, os, pdb, logging, json, traceback, configparser 
import pyautogui, yappi, psutil, threading, traceback, concurrent.futures
from PyQt5.QtCore import pyqtSignal, QObject, Qt, QMimeData, QTimer, QEvent
from PyQt5.QtWidgets import (QApplication, QMainWindow, QSplitter, QTabWidget,
                             QVBoxLayout, QHBoxLayout, QWidget, QLabel, QAction,
                             QTreeWidget, QTreeWidgetItem, QPushButton, QFileDialog, QMessageBox,
                             QAbstractItemView, QDialog, QLineEdit, QInputDialog, QMenu, QHeaderView,
                             QPlainTextEdit, QTextBrowser)
from PyQt5.QtGui import (QClipboard, QDragEnterEvent, QDropEvent, QDragMoveEvent, QDrag, QTextCursor,
                        QColor, QPalette, QKeySequence)
from PyQt5.QtCore import Qt, QThread # Import the Qt namespace
from PyQt5 import QtCore, QtGui, QtWidgets

#Qt indexs into Tree Node Custom Data:
QT_DATA_SAVE_NODES_DATA_STRUCT = Qt.UserRole
QT_DATA_LINE_COUNT = Qt.UserRole + 1
QT_DATA_IS_BASE = Qt.UserRole + 2

GALAXY_FROM_GALACTIC_ADDR_IDX = 0
SYSTEM_FROM_GALACTIC_ADDR_IDX = 1
PLANET_FROM_GALACTIC_ADDR_IDX = 2

GREEN_LED_COLOR = '#2eb82e'
YELLOW_LED_COLOR = '#f9f906'

#************
# CURRENT LOGGER LEVEL:
app_log_level = logging.ERROR   
    
#************

# Define a new logging level called VERBOSE with a numeric value lower than DEBUG (5)
VERBOSE = 5
logging.addLevelName(VERBOSE, "VERBOSE")
# Add VERBOSE as a reference to the logging module
logging.VERBOSE = VERBOSE

def verbose(self, message, *args, **kwargs):
    if self.isEnabledFor(VERBOSE):
        self._log(VERBOSE, message, args, **kwargs)

logging.Logger.verbose = verbose

# Set up logging to include VERBOSE level messages
logging.basicConfig(level=app_log_level, format='line %(lineno)d - %(asctime)s - %(levelname)s - %(message)s')

# Get a logger instance
logger = logging.getLogger(__name__)

def global_exception_handler(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        # Let KeyboardInterrupt exceptions pass through without logging
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
        
    
    # Print the error and traceback
    print(f"Unhandled exception: {exc_value}")
    traceback.print_exception(exc_type, exc_value, exc_traceback)
    
INIT_TEXT = """[
    {
        "BaseVersion":8,
        "OriginalBaseVersion":8,
        "GalacticAddress":5068787278259680,
        "Position":[
            4566.828125,
            -28771.09375,
            -94145.3125
        ],
        "Forward":[
            0.07187037914991379,
            -0.9528860449790955,
            0.29469117522239687
        ]
    }
]
"""

def safe_remove_qtreewidget_node(item):
    # Recursively delete all children of the item first
    while item.childCount() > 0:
        child = item.takeChild(0)  # Take the first child
        safe_remove_qtreewidget_node(child)  # Recursively call to delete its children

    # After all children are deleted, remove the item from its parent
    parent = item.parent()
    if parent is not None:
        parent.removeChild(item)  # Remove from the parent's child list
    else:
        # If the item is a top-level item (no parent), remove it from the QTreeWidget
        tree_widget = item.treeWidget()
        
        if tree_widget is not None: 
            index = tree_widget.indexOfTopLevelItem(item)
        
            if index != -1:
                tree_widget.takeTopLevelItem(index)

    
