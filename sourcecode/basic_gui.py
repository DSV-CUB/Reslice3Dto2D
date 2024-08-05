import sys
import os
from PyQt5 import QtWidgets, QtGui, QtCore, uic


class Inheritance_MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None, ui=None):
        super().__init__(parent)

        self.ui = uic.loadUi(ui, self)

        if getattr(sys, 'frozen', False):
            logopath=os.path.join(sys._MEIPASS, "logo.png")
        else:
            logopath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "logo.png")


        try:
            self.setWindowIcon(QtGui.QIcon(logopath))
        except:
            pass

        self.ui.setWindowFlag(QtCore.Qt.CustomizeWindowHint, True)
        self.ui.setWindowFlag(QtCore.Qt.WindowMinMaxButtonsHint, False)
        self.ui.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, False)
        self.ui.setWindowFlag(QtCore.Qt.WindowMinimizeButtonHint, True)
        self.ui.centralwidget.setWindowState(self.ui.centralwidget.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.ui.centralwidget.activateWindow()

        for parent_widget in self.ui.centralwidget.children():
            try:
                parent_widget.setFont(QtGui.QFont("Arial", 12))
            except:
                pass
        return

    def closeEvent(self, event):
        event.accept()
        return

    def get_directory(self, control, **kwargs):
        base_path = kwargs.get("path", os.path.expanduser("~"))

        if isinstance(control, QtWidgets.QLabel):
            if control.text() == "":
                result = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select a Directory', base_path)
            else:
                result = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select a Directory', control.text())

            if not result == "":
                control.setText(result)
        else:
            result = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select a Directory', base_path)
        return result

    def get_file(self, control, filetype=None):
        if filetype is None:
            filetype = "All Files (*.*)"

        if isinstance(control, QtWidgets.QLabel):
            if control.text() == "":
                result = QtWidgets.QFileDialog.getOpenFileName(self, 'Select a File', os.path.expanduser("~"), filetype)
            else:
                result = QtWidgets.QFileDialog.getOpenFileName(self, 'Select a File', control.text(), filetype)

            if not result == "":
                control.setText(result[0])
        else:
            result = QtWidgets.QFileDialog.getOpenFileName(self, 'Select a File', os.path.expanduser("~"), filetype)
        return result

    def show_dialog(self, text, icon="Information", include_Cancel=False):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(eval("QtWidgets.QMessageBox." + icon.capitalize()))

        #msg.setWindowIcon(QtGui.QIcon(QtGui.QPixmap(32, 32).fill(QtCore.Qt.blue)))

        msg.setText(text)
        #msg.setInformativeText("This is additional information")
        msg.setWindowTitle(icon.capitalize())
        #msg.setDetailedText("The details are as follows:")
        if icon.capitalize() == "Information" or icon.capitalize() == "Critical" or icon.capitalize() == "Warning":
            if include_Cancel:
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
            else:
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        elif icon.capitalize() == "Question":
            if include_Cancel:
                msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel)
            else:
                msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

        result = msg.exec_()
        return result


class Inheritance_Dialog(QtWidgets.QDialog):
    def __init__(self, parent=None, ui=None):
        super().__init__(parent)

        self.ui = uic.loadUi(ui, self)

        try:
            self.setWindowIcon(QtGui.QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)), "logo.png")))
        except:
            pass

        self.ui.setWindowFlag(QtCore.Qt.CustomizeWindowHint, False)
        self.ui.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, False)
        self.ui.setWindowFlag(QtCore.Qt.WindowMinimizeButtonHint, False)
        self.ui.setWindowFlag(QtCore.Qt.WindowMinMaxButtonsHint, False)
        self.ui.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.ui.activateWindow()

        for parent_widget in self.ui.children():
            try:
                parent_widget.setFont(QtGui.QFont("Arial", 12))
            except:
                pass
        return

    def closeEvent(self, event):
        event.accept()
        return

    def get_directory(self, control, **kwargs):
        base_path = kwargs.get("path", os.path.expanduser("~"))

        if isinstance(control, QtWidgets.QLabel):
            if control.text() == "":
                result = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select a Directory', base_path)
            else:
                result = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select a Directory', control.text())

            if not result == "":
                control.setText(result)
        else:
            result = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select a Directory', base_path)
        return result.replace("/", "\\")

    def get_file(self, control, filetype=None):
        if filetype is None:
            filetype = "All Files (*.*)"

        if isinstance(control, QtWidgets.QLabel):
            if control.text() == "":
                result = QtWidgets.QFileDialog.getOpenFileName(self, 'Select a File', os.path.expanduser("~"), filetype)
            else:
                result = QtWidgets.QFileDialog.getOpenFileName(self, 'Select a File', control.text(), filetype)

            if not result == "":
                control.setText(result[0])
        else:
            result = QtWidgets.QFileDialog.getOpenFileName(self, 'Select a File', os.path.expanduser("~"), filetype)
        return result[0].replace("/", "\\")

    def show_dialog(self, text, icon="Information", include_Cancel=False):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(eval("QtWidgets.QMessageBox." + icon.capitalize()))

        #msg.setWindowIcon(QtGui.QIcon(QtGui.QPixmap(32, 32).fill(QtCore.Qt.blue)))

        msg.setText(text)
        #msg.setInformativeText("This is additional information")
        msg.setWindowTitle(icon.capitalize())
        #msg.setDetailedText("The details are as follows:")
        if icon.capitalize() == "Information" or icon.capitalize() == "Critical" or icon.capitalize() == "Warning":
            if include_Cancel:
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
            else:
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        elif icon.capitalize() == "Question":
            if include_Cancel:
                msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel)
            else:
                msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

        result = msg.exec_()
        return result


if __name__ == "__main__":
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    global gui_run
    app = QtWidgets.QApplication(sys.argv)
    gui_run = Inheritance()
    gui_run.show()
    sys.exit(app.exec_())
