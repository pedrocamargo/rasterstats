# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_rasterstats_visualizer.ui'
#
# Created: Fri Aug 14 13:34:41 2015
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_rasterstats_view(object):
    def setupUi(self, rasterstats_view):
        rasterstats_view.setObjectName(_fromUtf8("rasterstats_view"))
        rasterstats_view.resize(817, 204)
        self.centralwidget = QtGui.QWidget(rasterstats_view)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.but_raster = QtGui.QPushButton(self.centralwidget)
        self.but_raster.setGeometry(QtCore.QRect(20, 50, 131, 23))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.but_raster.setFont(font)
        self.but_raster.setObjectName(_fromUtf8("but_raster"))
        self.but_close = QtGui.QPushButton(self.centralwidget)
        self.but_close.setGeometry(QtCore.QRect(160, 155, 131, 23))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.but_close.setFont(font)
        self.but_close.setObjectName(_fromUtf8("but_close"))
        self.but_vector = QtGui.QPushButton(self.centralwidget)
        self.but_vector.setGeometry(QtCore.QRect(20, 88, 131, 23))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.but_vector.setFont(font)
        self.but_vector.setObjectName(_fromUtf8("but_vector"))
        self.but_run = QtGui.QPushButton(self.centralwidget)
        self.but_run.setGeometry(QtCore.QRect(20, 155, 131, 23))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.but_run.setFont(font)
        self.but_run.setObjectName(_fromUtf8("but_run"))
        self.histogram = QtGui.QRadioButton(self.centralwidget)
        self.histogram.setGeometry(QtCore.QRect(130, 13, 101, 17))
        self.histogram.setChecked(True)
        self.histogram.setObjectName(_fromUtf8("histogram"))
        self.general = QtGui.QRadioButton(self.centralwidget)
        self.general.setGeometry(QtCore.QRect(20, 13, 91, 17))
        self.general.setObjectName(_fromUtf8("general"))
        self.raster_name = QtGui.QLabel(self.centralwidget)
        self.raster_name.setGeometry(QtCore.QRect(180, 55, 611, 16))
        self.raster_name.setObjectName(_fromUtf8("raster_name"))
        self.vector_name = QtGui.QLabel(self.centralwidget)
        self.vector_name.setGeometry(QtCore.QRect(180, 93, 621, 16))
        self.vector_name.setObjectName(_fromUtf8("vector_name"))
        self.but_output = QtGui.QPushButton(self.centralwidget)
        self.but_output.setGeometry(QtCore.QRect(20, 121, 131, 23))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.but_output.setFont(font)
        self.but_output.setObjectName(_fromUtf8("but_output"))
        self.output_file = QtGui.QLabel(self.centralwidget)
        self.output_file.setGeometry(QtCore.QRect(180, 126, 621, 16))
        self.output_file.setObjectName(_fromUtf8("output_file"))
        self.progressbar = QtGui.QProgressBar(self.centralwidget)
        self.progressbar.setEnabled(True)
        self.progressbar.setGeometry(QtCore.QRect(330, 155, 461, 23))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Highlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(240, 240, 240))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Highlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(51, 153, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Highlight, brush)
        self.progressbar.setPalette(palette)
        self.progressbar.setProperty("value", 0)
        self.progressbar.setTextVisible(True)
        self.progressbar.setObjectName(_fromUtf8("progressbar"))
        #rasterstats_view.setCentralWidget(self.centralwidget)
        #self.statusbar = QtGui.QStatusBar(rasterstats_view)
        #self.statusbar.setObjectName(_fromUtf8("statusbar"))
        #rasterstats_view.setStatusBar(self.statusbar)

        self.retranslateUi(rasterstats_view)
        QtCore.QMetaObject.connectSlotsByName(rasterstats_view)

    def retranslateUi(self, rasterstats_view):
        rasterstats_view.setWindowTitle(_translate("rasterstats_view", "Raster Statistics", None))
        self.but_raster.setText(_translate("rasterstats_view", "Choose Raster file", None))
        self.but_close.setText(_translate("rasterstats_view", "Close", None))
        self.but_vector.setText(_translate("rasterstats_view", "Choose Raster file", None))
        self.but_run.setText(_translate("rasterstats_view", "Run", None))
        self.histogram.setText(_translate("rasterstats_view", "Histogram", None))
        self.general.setText(_translate("rasterstats_view", "General stats", None))
        self.raster_name.setText(_translate("rasterstats_view", "Raster file", None))
        self.vector_name.setText(_translate("rasterstats_view", "Vector file", None))
        self.but_output.setText(_translate("rasterstats_view", "Choose output file", None))
        self.output_file.setText(_translate("rasterstats_view", "Output file", None))

