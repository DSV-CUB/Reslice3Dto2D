import sys
from PyQt5 import QtWidgets
from tools.Reslice3Dto2D import gui

def main():
    gui_run = gui.GUI()
    gui_run.show()
    return gui_run

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    gui_run = main()
    gui_run.show()
    sys.exit(app.exec_())