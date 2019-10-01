"""
/***************************************************************************
RasterStats for QGIS
 
    Name:        QGIS plgin iniitalizer
                              -------------------
        begin                : 2014-03-19
        edited               : 2019-10-01
        copyright            : Pedro Camargo
        Original Author: Pedro Camargo pedro@xl-optim.com
        Contributors: 
        Licence: See LICENSE.TXT
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""
import sys
sys.dont_write_bytecode = True

def classFactory(iface):
    from .rasterstats_menu import rasterstats_menu
    return rasterstats_menu(iface)
