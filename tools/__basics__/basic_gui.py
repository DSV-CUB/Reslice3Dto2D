import sys
import os
from PyQt5 import QtWidgets, QtCore
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, False) #enable highdpi scaling
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, False) #use highdpi icons
from tools import __basics__


# USE IF APPLICATION WAS CREATED WITH PyQtDesigner, rename gui.ui according to your application
class GUI(__basics__.parent_gui.Inheritance):
    def __init__(self, parent=None, config=None):
        super().__init__(parent, config, os.path.join(os.path.dirname(os.path.realpath(__file__)), "gui.ui"))

        return

if __name__ == "__main__":
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    global gui_run
    app = QtWidgets.QApplication(sys.argv)
    gui_run = GUI()
    gui_run.show()
    sys.exit(app.exec_())