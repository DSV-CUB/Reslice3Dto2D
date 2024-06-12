import sys
from PyQt5 import QtWidgets, QtCore
from sourcecode import gui_main as gui


def main():
    gui_run = gui.GUI()
    gui_run.show()
    return gui_run


if __name__ == "__main__":
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    global gui_run
    app = QtWidgets.QApplication(sys.argv)
    gui_run = main()
    sys.exit(app.exec_())