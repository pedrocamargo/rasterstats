"""
/***************************************************************************
 rasterstats and np matrix vizualiser for QGIS
 
    Name:        QGIS plgin iniitalizer
                              -------------------
        Begin                : 2014-03-19
        Edit                 : 2019-10-01
        Copyright            : Pedro Camargo
        Original Author: Pedro Camargo pedro@xl-optim.com
        Contributors: 
        Licence: See LICENSE.TXT
 ***************************************************************************/
"""

import sys, os
import qgis
from qgis.core import *
from qgis.PyQt import QtWidgets, QtCore, QtGui, uic
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import QFileDialog

from .run_raster_statistics import RunMyRasterStatistics

# from qgis.gui import QgsMapLayerProxyModel

Qt = QtCore.Qt

sys.modules["qgsfieldcombobox"] = qgis.gui
sys.modules["qgsmaplayercombobox"] = qgis.gui
FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "ui_rasterstats_visualizer.ui")
)


class rasterstatsDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, iface):
        QtWidgets.QDialog.__init__(self)
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
        newname = QFileDialog.getSaveFileName(
            self, "Output file", self.output_file.text(), "Comma-separated file(*.csv)"
        )
        if newname is None:
            self.output_file.setText("")
        else:
            self.output_file.setText(newname[0])

    def closewidget(self):
        self.close()

    def update_decimals(self):
        self.label_decimals.setText(
            "Histogram decimal places: " + str(self.slider_decimals.value())
        )
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
        self.workerThread.ProgressValue.connect(self.ProgressValueFromThread)
        self.workerThread.finished_threaded_procedure.connect(self.closewidget)

        self.workerThread.start()
        self.exec_()

    def run_stats(self):
        histogram = False
        if self.histogram.isChecked():
            histogram = True

        self.workerThread = RunMyRasterStatistics(
            qgis.utils.iface.mainWindow(),
            self.cob_polygon.currentLayer(),
            self.cob_id.currentText(),
            self.cob_raster.currentLayer(),
            self.output_file.text(),
            self.decimals,
            histogram,
        )
        self.runThread()
