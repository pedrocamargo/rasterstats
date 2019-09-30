# Raster Stats
QGIS plugin, developed with the intention to provide a fast and easy-to-use tool for computing statistics on the overlap between raster and polygon layers.

## Difference from other tools available in QGIS (as of its release)
In addition to the tools that already exist in QGIS for computing raster statistics, this plugin allows for the computation of histograms for zones and provides a wider range of summary statistics (Average,Median,Standard deviation,Variance,Minimum,Maximum number of pixels overlaping and median absolute deviation )

## Key assumption
* Pixels are fully included in a polygon, regardless of the total overlap. For this reason, care should be taken if the pixel size in the raster layer is relatively big when compared to the polygon size

## QGIS plugin page

[QGIS plugin repository](http://plugins.qgis.org/plugins/rasterstats/)

