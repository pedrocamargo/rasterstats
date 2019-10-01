#copied from https://github.com/AequilibraE/AequilibraE-GUI

from qgis.core import *
from qgis.PyQt.QtCore import *


class WorkerThread(QThread):
    jobFinished = pyqtSignal("PyQt_PyObject")
    ProgressValue = pyqtSignal("PyQt_PyObject")
    ProgressMaxValue = pyqtSignal("PyQt_PyObject")
    ProgressText = pyqtSignal("PyQt_PyObject")
    finished_threaded_procedure = pyqtSignal("PyQt_PyObject")

    def __init__(self, parentThread):
        QThread.__init__(self, parentThread)

    def run(self):
        self.running = True
        success = self.doWork()
        self.jobFinished.emit(success)

    def stop(self):
        self.running = False
        pass

    def doWork(self):
        return True

    def cleanUp(self):
        pass
