import os
import sys
from PyQt5 import QtWidgets, QtCore

from tools import __basics__, Reslice3Dto2D


if __name__ == "__main__":
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app = QtWidgets.QApplication(sys.argv)
    gui_run = Reslice3Dto2D.gui.GUI()
    gui_run.show()
    sys.exit(app.exec_())