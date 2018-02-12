"""
/***************************************************************************
 rasterstats and np matrix vizualiser for QGIS
 
    Name:        QGIS plgin iniitalizer
                              -------------------
        Begin                : 2014-03-19
        Edit                : 2018-02-11
        Copyright            : Pedro Camargo
        Original Author: Pedro Camargo pedro@xl-optim.com
        Contributors: 
        Licence: See LICENSE.TXT
 ***************************************************************************/
"""

import sys, os
from qgis.core import *
import qgis
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from run_raster_statistics import RunMyRasterStatistics
from qgis.gui import QgsMapLayerProxyModel

Qt = QtCore.Qt

sys.modules['qgsfieldcombobox'] = qgis.gui
sys.modules['qgsmaplayercombobox'] = qgis.gui
FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ui_rasterstats_visualizer.ui'))


class open_rasterstats_class(QtGui.QDialog, FORM_CLASS):
    def __init__(self, iface):
        QtGui.QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)
        self.decimals = 0

        self.cob_raster.setFilters(QgsMapLayerProxyModel.RasterLayer)
        self.cob_polygon.setFilters(QgsMapLayerProxyModel.PolygonLayer)
        self.cob_id.setLayer(self.cob_polygon.currentLayer())
        self.but_output.clicked.connect(self.browse_outputfile)

        self.histogram.toggled.connect(self.sets_histogram)
        self.general.toggled.connect(self.sets_histogram)
        self.slider_decimals.valueChanged.connect(self.update_decimals)

        self.but_run.clicked.connect(self.run_stats)
        self.but_close.clicked.connect(self.closewidget)

    def browse_outputfile(self):
        newname = QFileDialog.getSaveFileName(None, 'Output file', self.output_file.text(),
                                              "Comma-separated file(*.csv)")
        if newname is None:
            self.output_file.setText('')
        else:
            self.output_file.setText(newname)

    def closewidget(self):
        self.close()

    def update_decimals(self):
        self.label_decimals.setText('Histogram decimal places: ' + str(self.slider_decimals.value()))
        self.decimals = self.slider_decimals.value()

    def sets_histogram(self):
        status = False
        if self.histogram.isChecked():
            status = True

        self.label_decimals.setVisible(status)
        self.slider_decimals.setVisible(status)

    def ProgressValueFromThread(self, val):
        self.progressbar.setValue(val)

    def runThread(self):
        QObject.connect(self.workerThread, SIGNAL("ProgressValue( PyQt_PyObject )"), self.ProgressValueFromThread)
        QObject.connect(self.workerThread, SIGNAL("FinishedThreadedProcedure( PyQt_PyObject )"), self.closewidget)

        self.workerThread.start()
        self.exec_()

    def run_stats(self):
        histogram = False
        if self.histogram.isChecked():
            histogram = True

        self.workerThread = RunMyRasterStatistics(qgis.utils.iface.mainWindow(), self.cob_polygon.currentLayer(),
                                                  self.cob_id.currentText(), self.cob_raster.currentLayer(),
                                                  self.output_file.text(), self.decimals, histogram)
        self.runThread()
