"""
/***************************************************************************
 rasterstats for QGIS

    Name:        QGIS plgin iniitalizer
                              -------------------
        begin                : 2018-02-11
        copyright            : Pedro Camargo
        Original Author: Pedro Camargo pedro@xl-optim.com
        Contributors:
        Licence: See LICENSE.TXT
 ***************************************************************************/
"""

from qgis.core import *
import qgis
from PyQt4 import QtCore
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from worker_thread import WorkerThread
from osgeo import gdal
import numpy as np

Qt = QtCore.Qt


class RunMyRasterStatistics(WorkerThread):
    def __init__(self, parentThread, polygon_layer, polygon_id, raster_layer, output_file, decimals, histogram):
        WorkerThread.__init__(self, parentThread)
        self.polygon_layer = polygon_layer
        self.polygon_id = polygon_id
        self.raster_layer = raster_layer
        self.output_file = output_file
        self.decimals = decimals
        self.histogram = histogram
        self.errors = []
        # Creates transform if necessary
        self.transform = None
        if self.raster_layer.crs() != self.polygon_layer.dataProvider().crs():
            self.transform = QgsCoordinateTransform(self.polygon_layer.dataProvider().crs(), self.raster_layer.crs())

    def doWork(self):
        # We colect info on the vector file
        idx = self.polygon_layer.fieldNameIndex(self.polygon_id)
        statDict = {}

        # Information on the raster layer
        raster_width = self.raster_layer.width()
        raster_height = self.raster_layer.height()
        raster = gdal.Open(self.raster_layer.source())
        raster_info = raster.GetGeoTransform()
        xOrigin = raster_info[0]
        yOrigin = raster_info[3]
        pixelWidth = raster_info[1]
        pixelHeight = raster_info[5]


        xOrigin = self.raster_layer.extent().xMinimum()
        yOrigin = self.raster_layer.extent().yMaximum()
        pixelWidth = self.raster_layer.rasterUnitsPerPixelX()
        pixelHeight = self.raster_layer.rasterUnitsPerPixelY()

        tot_feat = self.polygon_layer.featureCount()
        for i, feat in enumerate(self.polygon_layer.getFeatures()):
            self.emit(SIGNAL("ProgressValue( PyQt_PyObject )"), int(100 * (float(i) / tot_feat)))
            feat_id = feat.attributes()[idx]
            statDict[feat_id] = None

            # Reproject vector geometry to same projection as raster
            geom = feat.geometry()
            if self.transform is not None:
                geom.transform(self.transform)

            # Get extent of feat
            bb = geom.boundingBox()

            if bb is not None:
                xmin, xmax, ymin, ymax = bb.xMinimum(), bb.xMaximum(), bb.yMinimum(), bb.yMaximum()
                # Specify offset and rows and columns to read
                xoff = int(abs(xmin - xOrigin) / pixelWidth)
                yoff = int(abs(yOrigin - ymax) / pixelHeight)
                xcount = int((xmax - xmin) / pixelWidth) + 1
                ycount = int((ymax - ymin) / pixelHeight) + 1

                banddataraster = raster.GetRasterBand(1)
                dataraster = banddataraster.ReadAsArray(xoff, yoff, xcount, ycount)

                if dataraster is not None:
                    dataraster.astype(np.float)

                    # Calculate statistics of zonal raster`
                    if self.histogram:
                        if self.decimals > 0:
                            dataraster = dataraster * pow(10, self.decimals)
                        statDict[feat_id] = np.bincount((dataraster.astype(np.int)).flat, weights=None, minlength=None)
                    else:
                        statDict[feat_id] = [np.average(dataraster), np.mean(dataraster), np.median(dataraster),
                                             np.std(dataraster), np.var(dataraster), np.min(dataraster),
                                             np.max(dataraster)]
                else:
                    self.errors.append('Statistics for polygon with ID ' + str(feat_id) + ' was empty')

        columns = 0
        for feat_id, dictionary in statDict.iteritems():
                if dictionary is not None:
                    if self.histogram:
                        if columns < dictionary.shape[0]:
                            columns = dictionary.shape[0]

        self.emit(SIGNAL("ProgressValue( PyQt_PyObject )"), 100)
        O = open(self.output_file, 'w')
        if self.histogram:
            txt = 'Zone ID'
            if self.decimals > 0:
                divide = pow(10, self.decimals)
                for i in range(columns):
                    txt = txt + ',' + str(round(float(i) / divide, self.decimals))
            else:
                for i in range(columns):
                    txt = txt + ',' + str(i)
            print >> O, txt
        else:
            print >> O, 'Zone ID,Average,Mean,Median,Standard deviation,Variance,Minimum,Maximum'
        tot_feat = len(statDict.keys())
        for i, ids in enumerate(statDict.keys()):
            self.emit(SIGNAL("ProgressValue( PyQt_PyObject )"), int(100 * (float(i) / tot_feat)))
            txt = str(ids)
            if statDict[ids] is None:
                self.errors.append(txt + ', No data or error in computation')
            else:
                for i in statDict[ids]:
                    txt = txt + ',' + str(i)
                for i in range(columns - len(statDict[ids])):
                    txt = txt + ',0'
                print >> O, txt
        O.flush()
        O.close()

        if len(self.errors) > 0:
            O = open(self.output_file + '.errors', 'w')
            for txt in self.errors:
                print >> O, txt
            O.flush()
            O.close()
        self.emit(SIGNAL("FinishedThreadedProcedure( PyQt_PyObject )"), 0)
