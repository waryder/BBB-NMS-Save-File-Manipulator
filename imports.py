import sys, os, pdb, logging, json, traceback, configparser, copy 
import pyautogui, yappi, psutil, threading, traceback, concurrent.futures
from PyQt5.QtCore import pyqtSignal, QObject, Qt, QMimeData, QTimer, QEvent
from PyQt5.QtWidgets import (QApplication, QMainWindow, QSplitter, QTabWidget,
                             QVBoxLayout, QHBoxLayout, QWidget, QLabel, QAction,
                             QTreeWidget, QTreeWidgetItem, QPushButton, QFileDialog, QMessageBox,
                             QAbstractItemView, QDialog, QLineEdit, QInputDialog, QMenu, QHeaderView,
                             QPlainTextEdit, QTextBrowser)
from PyQt5.QtGui import (QClipboard, QDragEnterEvent, QDropEvent, QDragMoveEvent, QDrag, QTextCursor,
                        QColor, QPalette, QKeySequence, QFont)
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

global GALAXIES

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
logging.basicConfig(level=app_log_level, format='%(filename)s # line %(lineno)d # %(asctime)s # %(levelname)s # %(message)s')

# Get a logger instance
logger = logging.getLogger(__name__)

def get_new_QTreeWidgetItem():
    widget = QTreeWidgetItem()
    widget.setFlags(widget.flags() | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled)  # Make item drag and droppable Qt.ItemIsEditable
    return widget
    
def get_num_app_child_threads():
    logger.verbose("get_num_app_child_threads() ENTER")
    # Get the current process (your application)
    current_process = psutil.Process(os.getpid())
    num_threads = len(current_process.threads())
    logger.verbose("get_num_app_child_threads() EXIT, num threads: {num_threads}")
    return num_threads


#some values are preceeded by '0x' and some are not:    
def get_galaxy_system_planet_from_full_addr(galactic_addr_in):
    if isinstance(galactic_addr_in, int):
        galactic_address = f"0x{galactic_addr_in:X}" 
    elif "0x" not in galactic_addr_in:    
        galactic_address = f"0x{int(galactic_addr_in):X}"
    else:
        galactic_address = galactic_addr_in    
        
    gal_idx_slice = slice(6, 8)
    system_idx_slice = slice(3, 6)
    planet_idx = 2
    
    return [galactic_address[gal_idx_slice], galactic_address[system_idx_slice], galactic_address[2]]  


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
                
def init_galaxies():
    GALAXIES = {}
    GALAXIES[0] = 'Euclid'
    GALAXIES[1] = 'Hilbert Dimension'
    GALAXIES[2] = 'Calypso'
    GALAXIES[3] = 'Hesperius Dimension'
    GALAXIES[4] = 'Hyades'
    GALAXIES[5] = 'Ickjamatew'
    GALAXIES[6] = 'Budullangr'
    GALAXIES[7] = 'Kikolgallr'
    GALAXIES[8] = 'Eltiensleen'
    GALAXIES[9] = 'Eissentam'
    GALAXIES[10] = 'Elkupalos'
    GALAXIES[11] = 'Aptarkaba'
    GALAXIES[12] = 'Ontiniangp'
    GALAXIES[13] = 'Odiwagiri'
    GALAXIES[14] = 'Ogtialabi'
    GALAXIES[15] = 'Muhacksonto'
    GALAXIES[16] = 'Hitonskyer'
    GALAXIES[17] = 'Rerasmutul'
    GALAXIES[18] = 'Isdoraijung'
    GALAXIES[19] = 'Doctinawyra'
    GALAXIES[20] = 'Loychazinq'
    GALAXIES[21] = 'Zukasizawa'
    GALAXIES[22] = 'Ekwathore'
    GALAXIES[23] = 'Yeberhahne'
    GALAXIES[24] = 'Twerbetek'
    GALAXIES[25] = 'Sivarates'
    GALAXIES[26] = 'Eajerandal'
    GALAXIES[27] = 'Aldukesci'
    GALAXIES[28] = 'Wotyarogii'
    GALAXIES[29] = 'Sudzerbal'
    GALAXIES[30] = 'Maupenzhay'
    GALAXIES[31] = 'Sugueziume'
    GALAXIES[32] = 'Brogoweldian'
    GALAXIES[33] = 'Ehbogdenbu'
    GALAXIES[34] = 'Ijsenufryos'
    GALAXIES[35] = 'Nipikulha'
    GALAXIES[36] = 'Autsurabin'
    GALAXIES[37] = 'Lusontrygiamh'
    GALAXIES[38] = 'Rewmanawa'
    GALAXIES[39] = 'Ethiophodhe'
    GALAXIES[40] = 'Urastrykle'
    GALAXIES[41] = 'Xobeurindj'
    GALAXIES[42] = 'Oniijialdu'
    GALAXIES[43] = 'Wucetosucc'
    GALAXIES[44] = 'Ebyeloof'
    GALAXIES[45] = 'Odyavanta'
    GALAXIES[46] = 'Milekistri'
    GALAXIES[47] = 'Waferganh'
    GALAXIES[48] = 'Agnusopwit'
    GALAXIES[49] = 'Teyaypilny'
    GALAXIES[50] = 'Zalienkosm'
    GALAXIES[51] = 'Ladgudiraf'
    GALAXIES[52] = 'Mushonponte'
    GALAXIES[53] = 'Amsentisz'
    GALAXIES[54] = 'Fladiselm'
    GALAXIES[55] = 'Laanawemb'
    GALAXIES[56] = 'Ilkerloor'
    GALAXIES[57] = 'Davanossi'
    GALAXIES[58] = 'Ploehrliou'
    GALAXIES[59] = 'Corpinyaya'
    GALAXIES[60] = 'Leckandmeram'
    GALAXIES[61] = 'Quulngais'
    GALAXIES[62] = 'Nokokipsechl'
    GALAXIES[63] = 'Rinblodesa'
    GALAXIES[64] = 'Loydporpen'
    GALAXIES[65] = 'Ibtrevskip'
    GALAXIES[66] = 'Elkowaldb'
    GALAXIES[67] = 'Heholhofsko'
    GALAXIES[68] = 'Yebrilowisod'
    GALAXIES[69] = 'Husalvangewi'
    GALAXIES[70] = 'Ovnauesed'
    GALAXIES[71] = 'Bahibusey'
    GALAXIES[72] = 'Nuybeliaure'
    GALAXIES[73] = 'Doshawchuc'
    GALAXIES[74] = 'Ruckinarkh'
    GALAXIES[75] = 'Thorettac'
    GALAXIES[76] = 'Nuponoparau'
    GALAXIES[77] = 'Moglaschil'
    GALAXIES[78] = 'Uiweupose'
    GALAXIES[79] = 'Nasmilete'
    GALAXIES[80] = 'Ekdaluskin'
    GALAXIES[81] = 'Hakapanasy'
    GALAXIES[82] = 'Dimonimba'
    GALAXIES[83] = 'Cajaccari'
    GALAXIES[84] = 'Olonerovo'
    GALAXIES[85] = 'Umlanswick'
    GALAXIES[86] = 'Henayliszm'
    GALAXIES[87] = 'Utzenmate'
    GALAXIES[88] = 'Umirpaiya'
    GALAXIES[89] = 'Paholiang'
    GALAXIES[90] = 'Iaereznika'
    GALAXIES[91] = 'Yudukagath'
    GALAXIES[92] = 'Boealalosnj'
    GALAXIES[93] = 'Yaevarcko'
    GALAXIES[94] = 'Coellosipp'
    GALAXIES[95] = 'Wayndohalou'
    GALAXIES[96] = 'Smoduraykl'
    GALAXIES[97] = 'Apmaneessu'
    GALAXIES[98] = 'Hicanpaav'
    GALAXIES[99] = 'Akvasanta'
    GALAXIES[100] = 'Tuychelisaor'
    GALAXIES[101] = 'Rivskimbe'
    GALAXIES[102] = 'Daksanquix'
    GALAXIES[103] = 'Kissonlin'
    GALAXIES[104] = 'Aediabiel'
    GALAXIES[105] = 'Ulosaginyik'
    GALAXIES[106] = 'Roclaytonycar'
    GALAXIES[107] = 'Kichiaroa'
    GALAXIES[108] = 'Irceauffey'
    GALAXIES[109] = 'Nudquathsenfe'
    GALAXIES[110] = 'Getaizakaal'
    GALAXIES[111] = 'Hansolmien'
    GALAXIES[112] = 'Bloytisagra'
    GALAXIES[113] = 'Ladsenlay'
    GALAXIES[114] = 'Luyugoslasr'
    GALAXIES[115] = 'Ubredhatk'
    GALAXIES[116] = 'Cidoniana'
    GALAXIES[117] = 'Jasinessa'
    GALAXIES[118] = 'Torweierf'
    GALAXIES[119] = 'Saffneckm'
    GALAXIES[120] = 'Thnistner'
    GALAXIES[121] = 'Dotusingg'
    GALAXIES[122] = 'Luleukous'
    GALAXIES[123] = 'Jelmandan'
    GALAXIES[124] = 'Otimanaso'
    GALAXIES[125] = 'Enjaxusanto'
    GALAXIES[126] = 'Sezviktorew'
    GALAXIES[127] = 'Zikehpm'
    GALAXIES[128] = 'Bephembah'
    GALAXIES[129] = 'Broomerrai'
    GALAXIES[130] = 'Meximicka'
    GALAXIES[131] = 'Venessika'
    GALAXIES[132] = 'Gaiteseling'
    GALAXIES[133] = 'Zosakasiro'
    GALAXIES[134] = 'Drajayanes'
    GALAXIES[135] = 'Ooibekuar'
    GALAXIES[136] = 'Urckiansi'
    GALAXIES[137] = 'Dozivadido'
    GALAXIES[138] = 'Emiekereks'
    GALAXIES[139] = 'Meykinunukur'
    GALAXIES[140] = 'Kimycuristh'
    GALAXIES[141] = 'Roansfien'
    GALAXIES[142] = 'Isgarmeso'
    GALAXIES[143] = 'Daitibeli'
    GALAXIES[144] = 'Gucuttarik'
    GALAXIES[145] = 'Enlaythie'
    GALAXIES[146] = 'Drewweste'
    GALAXIES[147] = 'Akbulkabi'
    GALAXIES[148] = 'Homskiw'
    GALAXIES[149] = 'Zavainlani'
    GALAXIES[150] = 'Jewijkmas'
    GALAXIES[151] = 'Itlhotagra'
    GALAXIES[152] = 'Podalicess'
    GALAXIES[153] = 'Hiviusauer'
    GALAXIES[154] = 'Halsebenk'
    GALAXIES[155] = 'Puikitoac'
    GALAXIES[156] = 'Gaybakuaria'
    GALAXIES[157] = 'Grbodubhe'
    GALAXIES[158] = 'Rycempler'
    GALAXIES[159] = 'Indjalala'
    GALAXIES[160] = 'Fontenikk'
    GALAXIES[161] = 'Pasycihelwhee'
    GALAXIES[162] = 'Ikbaksmit'
    GALAXIES[163] = 'Telicianses'
    GALAXIES[164] = 'Oyleyzhan'
    GALAXIES[165] = 'Uagerosat'
    GALAXIES[166] = 'Impoxectin'
    GALAXIES[167] = 'Twoodmand'
    GALAXIES[168] = 'Hilfsesorbs'
    GALAXIES[169] = 'Ezdaranit'
    GALAXIES[170] = 'Wiensanshe'
    GALAXIES[171] = 'Ewheelonc'
    GALAXIES[172] = 'Litzmantufa'
    GALAXIES[173] = 'Emarmatosi'
    GALAXIES[174] = 'Mufimbomacvi'
    GALAXIES[175] = 'Wongquarum'
    GALAXIES[176] = 'Hapirajua'
    GALAXIES[177] = 'Igbinduina'
    GALAXIES[178] = 'Wepaitvas'
    GALAXIES[179] = 'Sthatigudi'
    GALAXIES[180] = 'Yekathsebehn'
    GALAXIES[181] = 'Ebedeagurst'
    GALAXIES[182] = 'Nolisonia'
    GALAXIES[183] = 'Ulexovitab'
    GALAXIES[184] = 'Iodhinxois'
    GALAXIES[185] = 'Irroswitzs'
    GALAXIES[186] = 'Bifredait'
    GALAXIES[187] = 'Beiraghedwe'
    GALAXIES[188] = 'Yeonatlak'
    GALAXIES[189] = 'Cugnatachh'
    GALAXIES[190] = 'Nozoryenki'
    GALAXIES[191] = 'Ebralduri'
    GALAXIES[192] = 'Evcickcandj'
    GALAXIES[193] = 'Ziybosswin'
    GALAXIES[194] = 'Heperclait'
    GALAXIES[195] = 'Sugiuniam'
    GALAXIES[196] = 'Aaseertush'
    GALAXIES[197] = 'Uglyestemaa'
    GALAXIES[198] = 'Horeroedsh'
    GALAXIES[199] = 'Drundemiso'
    GALAXIES[200] = 'Ityanianat'
    GALAXIES[201] = 'Purneyrine'
    GALAXIES[202] = 'Dokiessmat'
    GALAXIES[203] = 'Nupiacheh'
    GALAXIES[204] = 'Dihewsonj'
    GALAXIES[205] = 'Rudrailhik'
    GALAXIES[206] = 'Tweretnort'
    GALAXIES[207] = 'Snatreetze'
    GALAXIES[208] = 'Iwundaracos'
    GALAXIES[209] = 'Digarlewena'
    GALAXIES[210] = 'Erquagsta'
    GALAXIES[211] = 'Logovoloin'
    GALAXIES[212] = 'Boyaghosganh'
    GALAXIES[213] = 'Kuolungau'
    GALAXIES[214] = 'Pehneldept'
    GALAXIES[215] = 'Yevettiiqidcon'
    GALAXIES[216] = 'Sahliacabru'
    GALAXIES[217] = 'Noggalterpor'
    GALAXIES[218] = 'Chmageaki'
    GALAXIES[219] = 'Veticueca'
    GALAXIES[220] = 'Vittesbursul'
    GALAXIES[221] = 'Nootanore'
    GALAXIES[222] = 'Innebdjerah'
    GALAXIES[223] = 'Kisvarcini'
    GALAXIES[224] = 'Cuzcogipper'
    GALAXIES[225] = 'Pamanhermonsu'
    GALAXIES[226] = 'Brotoghek'
    GALAXIES[227] = 'Mibittara'
    GALAXIES[228] = 'Huruahili'
    GALAXIES[229] = 'Raldwicarn'
    GALAXIES[230] = 'Ezdartlic'
    GALAXIES[231] = 'Badesclema'
    GALAXIES[232] = 'Isenkeyan'
    GALAXIES[233] = 'Iadoitesu'
    GALAXIES[234] = 'Yagrovoisi'
    GALAXIES[235] = 'Ewcomechio'
    GALAXIES[236] = 'Inunnunnoda'
    GALAXIES[237] = 'Dischiutun'
    GALAXIES[238] = 'Yuwarugha'
    GALAXIES[239] = 'Ialmendra'
    GALAXIES[240] = 'Reponudrle'
    GALAXIES[241] = 'Rinjanagrbo'
    GALAXIES[242] = 'Zeziceloh'
    GALAXIES[243] = 'Oeileutasc'
    GALAXIES[244] = 'Zicniijinis'
    GALAXIES[245] = 'Dugnowarilda'
    GALAXIES[246] = 'Neuxoisan'
    GALAXIES[247] = 'Ilmenhorn'
    GALAXIES[248] = 'Rukwatsuku'
    GALAXIES[249] = 'Nepitzaspru'
    GALAXIES[250] = 'Chcehoemig'
    GALAXIES[251] = 'Haffneyrin'
    GALAXIES[252] = 'Uliciawai'
    GALAXIES[253] = 'Tuhgrespod'
    GALAXIES[254] = 'Iousongola'
    GALAXIES[255] = 'Odyalutai'   

    return GALAXIES 

GALAXIES = init_galaxies()    


# MIT License
#
# Copyright (c) [Year] [Your Name or Your Company] <youremail@example.com>
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
#    [Your Name or Your Company] <youremail@example.com>, available under the MIT License.
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


    
