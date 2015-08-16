import gdal, ogr, osr, numpy
import sys, os, glob
import time
import multiprocessing as M

numpy.get_include()

def zonal_stats(feat, input_zone_polygon, input_value_raster, histogram):
    # Open data
    raster = gdal.Open(input_value_raster)
    shp = ogr.Open(input_zone_polygon)
    lyr = shp.GetLayer()

    # Get raster georeference info
    transform = raster.GetGeoTransform()
    xOrigin = transform[0]
    yOrigin = transform[3]
    pixelWidth = abs(transform[1])
    pixelHeight = abs(transform[5])

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
    xoff = int((xmin - xOrigin)/pixelHeight)
    yoff = int((yOrigin - ymax)/pixelWidth)

    #Number of pixels that the rasterized vector layer will have in each coordinate
    xcount = int((xmax - xmin)/pixelHeight)+1
    ycount = int((ymax - ymin)/pixelWidth)+1

    # Create memory target raster
    target_ds = gdal.GetDriverByName('MEM').Create('', xcount, ycount, 1, gdal.GDT_Byte)
    target_ds.SetGeoTransform((
        xmin, pixelHeight, 0,
        ymax, 0, pixelWidth,
    ))

    # Create for target raster the same projection as for the value raster
    raster_srs = osr.SpatialReference()
    raster_srs.ImportFromWkt(raster.GetProjectionRef())
    target_ds.SetProjection(raster_srs.ExportToWkt())

    # Rasterize zone polygon to raster
    gdal.RasterizeLayer(target_ds, [1], lyr, burn_values=[1])

    a=['Error in computation']
    # Read raster as arrays



    banddataraster = raster.GetRasterBand(1)
    xsize = min(xcount, banddataraster.XSize-xoff)
    ysize = min(ycount, banddataraster.YSize-yoff)

    dataraster = banddataraster.ReadAsArray(xoff, yoff, xsize, ysize).astype(numpy.float64)

    bandmask = target_ds.GetRasterBand(1)
    datamask = bandmask.ReadAsArray(0, 0, xcount, ycount).astype(numpy.float64)

    #datamask = datamask[0:ysize, 0:xsize]
    datamask = datamask[ycount-ysize:, xcount-xsize:]


    # Calculate statistics of zonal raster
    if histogram:
        b = numpy.bincount((dataraster*datamask).flat, weights=None, minlength=None)
    else:
        # Mask zone of raster
        zoneraster = numpy.ma.masked_array(dataraster,  numpy.logical_not(datamask))
        b = [numpy.average(zoneraster), numpy.mean(zoneraster), numpy.median(zoneraster), numpy.std(zoneraster), numpy.var(zoneraster)]
    a = b
    return a



def main():

    input_zone_polygon = 'D:\\Downloads\\TEST\\RI_CountiesADJUSTED.shp'
    input_value_raster = 'D:\\Downloads\\TEST\\CDL_2014_44.tif'
    output_file = 'D:\\Downloads\\TEST\\Output file_b.csv'
    histogram = True

    shp = ogr.Open(input_zone_polygon)
    lyr = shp.GetLayer()
    featList = range(lyr.GetFeatureCount())
    statDict = {}

    columns=0

    for FID in featList:
        feat = lyr.GetFeature(FID)
        statistics = zonal_stats(feat, input_zone_polygon, input_value_raster, histogram)
        statDict[feat.GetField("ID")] = statistics
        if histogram and statistics is not None:
            if columns < statistics.shape[0]:
                columns = statistics.shape[0]

    O=open(output_file,'w')
    if histogram:
        txt = 'Zone ID'
        for i in range(columns):
                txt=txt+','+str(i)
        print >>O, txt
    else:
        print >>O, 'Zone ID, Average, Mean, Median, Standard deviation, variance'
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





if __name__ == "__main__":
    main()
