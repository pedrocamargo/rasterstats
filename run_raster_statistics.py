"""
/***************************************************************************
 rasterstats for QGIS

    Name:        QGIS plgin iniitalizer
                              -------------------
        begin           : 2018-02-11
        Last Edit       : 2018-04-20
        copyright       : Pedro Camargo
        Original Author : Pedro Camargo pedro@xl-optim.com
        Contributors    :
        Licence         : See LICENSE.TXT
 ***************************************************************************/
"""

from qgis.core import *
from qgis.PyQt import QtCore, QtGui, QtWidgets, uic
from osgeo import gdal
import numpy as np



from .worker_thread import WorkerThread

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

        EPSG1 = QgsCoordinateReferenceSystem(int(self.polygon_layer.crs().authid().split(":")[1]))
        EPSG2 = QgsCoordinateReferenceSystem(int(self.raster_layer.crs().authid().split(":")[1]))
        if EPSG1 != EPSG2:
            self.transform = QgsCoordinateTransform(EPSG1, EPSG2, QgsProject.instance())

    def doWork(self):
        # We colect info on the vector file
        idx = self.polygon_layer.dataProvider().fieldNameIndex(self.polygon_id)
        statDict = {}

        # Information on the raster layer
        raster = gdal.Open(self.raster_layer.source())

        xOrigin = self.raster_layer.extent().xMinimum()
        yOrigin = self.raster_layer.extent().yMaximum()
        pixelWidth = self.raster_layer.rasterUnitsPerPixelX()
        pixelHeight = self.raster_layer.rasterUnitsPerPixelY()

        tot_feat = self.polygon_layer.featureCount()
        xEnd = self.raster_layer.extent().xMaximum()
        # yEnd = self.raster_layer.extent().yMinimum()
        for i, feat in enumerate(self.polygon_layer.getFeatures()):
            self.ProgressValue.emit(int(100 * (float(i) / tot_feat)))

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
                xmax = min(xmax, xEnd)

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
                                             np.max(dataraster), self.mad(dataraster), np.size(dataraster)]
                else:
                    self.errors.append('Statistics for polygon with ID ' + str(feat_id) + ' was empty')

        columns = 0
        for feat_id, dictionary in statDict.items():
            if dictionary is not None:
                if self.histogram:
                    if columns < dictionary.shape[0]:
                        columns = dictionary.shape[0]

        self.ProgressValue.emit(100)
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
                    O.write(txt + '\n')
        else:
            txt = 'Zone ID,Average,Mean,Median,Standard deviation,Variance,Minimum,' \
                  'Maximum,Median absolute deviation,pixel count\n'
            O.write(txt)

        tot_feat = len(statDict.keys())
        for i, ids in enumerate(statDict.keys()):
            self.ProgressValue.emit(int(100 * (float(i) / tot_feat)))
            txt = str(ids)
            if statDict[ids] is None:
                self.errors.append(txt + ', No data or error in computation')
            else:
                for i in statDict[ids]:
                    txt = txt + ',' + str(i)
                for i in range(columns - len(statDict[ids])):
                    txt = txt + ',0'
                O.write(txt + '\n')

        O.flush()
        O.close()

        if len(self.errors) > 0:
            O = open(self.output_file + '.errors', 'w')
            for txt in self.errors:
                O.write(txt + '\n')
            O.flush()
            O.close()
        self.finished_threaded_procedure.emit(0)

    # From https://stackoverflow.com/questions/8930370/where-can-i-find-mad-mean-absolute-deviation-in-scipy
    @staticmethod
    def mad(arr):
        """ Median Absolute Deviation: a "Robust" version of standard deviation.
            Indices variabililty of the sample.
            https://en.wikipedia.org/wiki/Median_absolute_deviation
        """
        arr = np.ma.array(arr).compressed()  # should be faster to not use masked arrays.
        med = np.median(arr)
        return np.median(np.abs(arr - med))
