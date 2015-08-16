"""
/***************************************************************************
 rasterstats and np matrix vizualiser for QGIS
 
    Name:        QGIS plgin iniitalizer
                              -------------------
        begin                : 2014-03-19
        copyright            : Pedro Camargo
        Original Author: Pedro Camargo pedro@xl-optim.com
        Contributors: 
        Licence: See LICENSE.TXT
 ***************************************************************************/
"""

from qgis.core import *
import qgis
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import gdal, ogr, osr
import time
import numpy as np

Qt = QtCore.Qt

#For the GIS tools portion
from ui_rasterstats_visualizer import *

import operator
import time

#####################################################################################################
###############################         rasterstats MATRIX VIEWER          ##################################

class WorkerThread(QThread):
    def __init__(self, parentThread):
        QThread.__init__(self, parentThread)

    def run(self):
        self.running = True
        success = self.doWork()
        self.emit(SIGNAL("jobFinished( PyQt_PyObject )"), success)

    def stop(self):
        self.running = False
        pass

    def doWork(self):
        return True

    def cleanUp(self):
        pass


class RunMyRasterStatistics(WorkerThread):
    def __init__(self, parentThread, input_zone_polygon, input_value_raster, output_file, histogram):
        WorkerThread.__init__(self, parentThread)
        self.input_zone_polygon = input_zone_polygon
        self.input_value_raster = input_value_raster
        self.output_file = output_file
        self.histogram = histogram
        self.emit(SIGNAL("ProgressValue( PyQt_PyObject )"), 50)
    def doWork(self):
        # We colect info on the vector file
        shp = ogr.Open(self.input_zone_polygon)
        lyr = shp.GetLayer()
        featList = range(lyr.GetFeatureCount())
        statDict = {}
        
        columns=0
        for FID in featList:
            feat = lyr.GetFeature(FID)
            statistics = self.zonal_stats(feat, self.input_zone_polygon, self.input_value_raster, self.histogram)
            statDict[feat.GetField("ID")] = statistics
            if self.histogram and statistics is not None:
                if columns < statistics.shape[0]:
                    columns = statistics.shape[0]
                
            #self.emit(SIGNAL("ProgressValue( PyQt_PyObject )"), (evol_bar, self.featcount))
            

        O=open(self.output_file,'w')
        if self.histogram:
            txt = 'Zone ID'
            for i in range(columns):
                    txt=txt+','+str(i)
            print >>O, txt
        else:
            print >>O, 'Zone ID,Average,Mean,Median,Standard deviation,Variance,Minimum,Maximum'
        for ids in statDict.keys():
            txt=str(ids)
            if statDict[ids] is None:
                print >>O, txt + ',No data or error in computation'
            else:
                for i in statDict[ids]:
                    txt=txt+','+str(i)
                print >>O, txt
        O.flush()
        O.close()
        self.emit(SIGNAL("FinishedThreadedProcedure( PyQt_PyObject )"),0)
    def zonal_stats(self, feat, input_zone_polygon, input_value_raster, histogram=False):

        # Open data
        raster = gdal.Open(input_value_raster)
        shp = ogr.Open(input_zone_polygon)
        lyr = shp.GetLayer()


        # Get raster georeference info
        transform = raster.GetGeoTransform()
        xOrigin = transform[0]
        yOrigin = transform[3]
        pixelWidth = transform[1]
        pixelHeight = transform[5]

        # Reproject vector geometry to same projection as raster
        sourceSR = lyr.GetSpatialRef()
        targetSR = osr.SpatialReference()
        targetSR.ImportFromWkt(raster.GetProjectionRef())
        coordTrans = osr.CoordinateTransformation(sourceSR,targetSR)
        geom = feat.GetGeometryRef()
        geom.Transform(coordTrans)

        # Get extent of feat
        geom = feat.GetGeometryRef()
        if (geom.GetGeometryName() == 'MULTIPOLYGON'):
            count = 0
            pointsX = []; pointsY = []
            for polygon in geom:
                geomInner = geom.GetGeometryRef(count)
                ring = geomInner.GetGeometryRef(0)
                numpoints = ring.GetPointCount()
                for p in range(numpoints):
                        lon, lat, z = ring.GetPoint(p)
                        pointsX.append(lon)
                        pointsY.append(lat)
                count += 1
        elif (geom.GetGeometryName() == 'POLYGON'):
            ring = geom.GetGeometryRef(0)
            numpoints = ring.GetPointCount()
            pointsX = []; pointsY = []
            for p in range(numpoints):
                    lon, lat, z = ring.GetPoint(p)
                    pointsX.append(lon)
                    pointsY.append(lat)

        else:
            sys.exit("ERROR: Geometry needs to be either Polygon or Multipolygon")

        xmin = min(pointsX)
        xmax = max(pointsX)
        ymin = min(pointsY)
        ymax = max(pointsY)

        # Specify offset and rows and columns to read
        xoff = int((xmin - xOrigin)/pixelWidth)
        yoff = int((yOrigin - ymax)/pixelWidth)
        xcount = int((xmax - xmin)/pixelWidth)+1
        ycount = int((ymax - ymin)/pixelWidth)+1

        # Create memory target raster
        target_ds = gdal.GetDriverByName('MEM').Create('', xcount, ycount, 1, gdal.GDT_Byte)
        target_ds.SetGeoTransform((
            xmin, pixelWidth, 0,
            ymax, 0, pixelHeight,
        ))

        # Create for target raster the same projection as for the value raster
        raster_srs = osr.SpatialReference()
        raster_srs.ImportFromWkt(raster.GetProjectionRef())
        target_ds.SetProjection(raster_srs.ExportToWkt())

        # Rasterize zone polygon to raster
        gdal.RasterizeLayer(target_ds, [1], lyr, burn_values=[1])

        
        
        
        #try:
        a=['Error in computation']
        # Read raster as arrays
        banddataraster = raster.GetRasterBand(1)
        dataraster = banddataraster.ReadAsArray(xoff, yoff, xcount, ycount).astype(np.float64)

        bandmask = target_ds.GetRasterBand(1)
        datamask = bandmask.ReadAsArray(0, 0, xcount, ycount).astype(np.int)

        # Calculate statistics of zonal raster`
        if histogram:
            b = np.bincount((dataraster*datamask).flat, weights=None, minlength=None)
        else:
            # Mask zone of raster
            zoneraster = np.ma.masked_array(dataraster,  np.logical_not(datamask))
            b = [np.average(zoneraster), np.mean(zoneraster), np.median(zoneraster), np.std(zoneraster), np.var(zoneraster), np.min(zoneraster), np.max(zoneraster)]
        a = b
        return a
        #except:
        #    print 'Error computing statistics'
            
class open_rasterstats_class(QtGui.QDialog,Ui_rasterstats_view):
    def __init__(self, iface):
        QtGui.QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)
        self.all_inputs = np.zeros(3,np.int32)
        
        self.but_raster.clicked.connect(self.browse_rasterfile)
        self.but_vector.clicked.connect(self.browse_vectorfile)
        self.but_output.clicked.connect(self.browse_outputfile)
        
        self.but_run.clicked.connect(self.run_stats)
        self.but_close.clicked.connect(self.closewidget)
        
    
    def browse_rasterfile(self):
        newname = QFileDialog.getOpenFileName(None, 'Raster file',self.raster_name.text() , "Tif(*.tif);;Tiff(*.tiff)")
        if newname is None:
            self.raster_name.setText('')
        else:
            self.raster_name.setText(newname)
            self.all_inputs[0] = 1
                
    def browse_vectorfile(self):
        newname = QFileDialog.getOpenFileName(None, 'Polygon file',self.vector_name.text() , "ShapeFile(*.shp)")
        if newname is None:
            self.vector_name.setText('')
        else:
            self.vector_name.setText(newname)
            self.all_inputs[1] = 1
            
    def browse_outputfile(self):
        newname = QFileDialog.getSaveFileName(None, 'Output file', self.output_file.text(), "Comma-separated file(*.csv)")
        if newname is None:
            self.output_file.setText('')
        else:
            self.output_file.setText(newname)
            self.all_inputs[2] = 1
            
    def closewidget(self):
        self.close()
    
    def ProgressValueFromThread(self, val):
        self.progressbar.setValue(val)
        
    def runThread(self):
        QObject.connect(self.workerThread, SIGNAL("ProgressValue( PyQt_PyObject )"), self.ProgressValueFromThread)
        QObject.connect(self.workerThread, SIGNAL("FinishedThreadedProcedure( PyQt_PyObject )"), self.closewidget)
        
        self.workerThread.start()
        self.exec_()
    
                                                          
    def run_stats(self):
        if np.sum(self.all_inputs) < 3:
            qgis.utils.iface.messageBar().pushMessage("No sufficient inputs", 'User needs to supply all three outputs', level=3)
        else:
            histogram = False
            if self.histogram.isChecked():
                histogram = True
            
            self.workerThread = RunMyRasterStatistics(qgis.utils.iface.mainWindow(), self.vector_name.text(), self.raster_name.text(), 
                                self.output_file.text(), histogram)
            self.runThread()
            