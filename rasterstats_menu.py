# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RasterStats vizualiser for QGIS
 
    Name:        QGIS plgin iniitalizer
                              -------------------
        begin                : 2014-03-19
        copyright            : Pedro Camargo
        Original Author: Pedro Camargo pedro@xl-optim.com
        Contributors: 
        Licence: See LICENSE.TXT
 ***************************************************************************/


"""
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

# Import the code for the dialog
from rasterstats_dialogs import *
import sys
sys.dont_write_bytecode = True
import os.path
import numpy as np

class rasterstats_menu:

    def __init__(self, iface):
        self.iface = iface
        self.RasterStats_menu = None
        
    def TOOLS_add_submenu(self, submenu):
        if self.RasterStats_menu != None:
            self.RasterStats_menu.addMenu(submenu)
        else:
            self.iface.addPluginToMenu("&RasterStats", submenu.menuAction())
			

    def initGui(self):

        # CREATING MASTER MENU HEAD
	self.rasterstats_menu = QMenu(QCoreApplication.translate("RasterStats", "RasterStats"))
	self.iface.mainWindow().menuBar().insertMenu(self.iface.firstRightStandardMenu().menuAction(), self.rasterstats_menu)
	



#########################################################################
##################        GIS TOOLS SUB-MENU    #########################
		
        #Node to area aggregation
	icon = QIcon(os.path.dirname(__file__) + "/icons/icon_node_to_area.png")
        self.open_rasterstats_action = QAction(icon,u"Compute raster statistics", self.iface.mainWindow())
        QObject.connect(self.open_rasterstats_action, SIGNAL("triggered()"), self.open_rasterstats)
        self.rasterstats_menu.addAction(self.open_rasterstats_action)

#########################################################################


        
    def unload(self):
        if self.rasterstats_menu != None:
            self.iface.mainWindow().menuBar().removeAction(self.rasterstats_menu.menuAction())
        else:
            self.iface.removePluginMenu("&RasterStats", self.gis_rasterstats_menu.menuAction())
            

    def open_rasterstats(self):  
        dlg2 = open_rasterstats_class(self.iface)
        dlg2.exec_()
