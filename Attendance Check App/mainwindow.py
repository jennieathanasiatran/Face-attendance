import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QDialog
import resource
from out_window import Ui_OutputDialog

class Ui_Dialog(QDialog):
    def __init__(self):
        super().__init__()
        loadUi("mainwindow.ui", self)
        self.runButton.clicked.connect(self.runSlot)
        self._new_window = None
        self.Videocapture_ = None

    def accessWebcam(self):
        self.Videocapture_ = "0"

    @pyqtSlot()
    def runSlot(self):
        self.accessWebcam()
        ui.hide()  # hide the main window
        self.outputWindow_()  # Create and open new output window

    def outputWindow_(self):
        self._new_window = Ui_OutputDialog()
        self._new_window.show()
        self._new_window.startVideo(self.Videocapture_)

app = QApplication(sys.argv)
ui = Ui_Dialog()
ui.show()
sys.exit(app.exec_())

