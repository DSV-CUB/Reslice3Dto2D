from tools import __basics__

import os
import sys
from PyQt5 import QtWidgets

class GUI(__basics__.parent_gui.Inheritance):
    def __init__(self, parent=None, config=None):
        super().__init__(parent, config, os.path.join(os.path.dirname(os.path.realpath(__file__)), "__basics__", "gui.ui"))

        self.btn_application_start.clicked.connect(self.btn_application_start_clicked)

        applications = []
        for subdir in os.listdir(os.path.join(os.path.dirname(os.path.realpath(__file__)))):
            if os.path.isdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), subdir)) and subdir not in ["__basics__", "data"] and not subdir.startswith("_") and not subdir.startswith("."):
                applications.append(subdir)

        self.lst_applications.addItems(applications)
        self.lst_applications.setCurrentRow(0)
        return

    def btn_application_start_clicked(self):
        app = self.lst_applications.currentItem().text()
        exec("from tools import " + app)
        exec(app + ".main()")
        return


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    gui_run = GUI()
    gui_run.show()
    sys.exit(app.exec_())