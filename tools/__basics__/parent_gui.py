import sys
import os
from PyQt5 import QtWidgets, QtGui, QtCore, uic
from tools.__basics__ import parent_configuration

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib
matplotlib.use('QT5Agg')

# Matplotlib canvas class to create figure
class MplCanvas(FigureCanvas):
    def __init__(self):
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

# Matplotlib widget
class QWidgetMatplotlib(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)   # Inherit from QWidget
        self.canvas = MplCanvas()                  # Create canvas object
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.vbl = QtWidgets.QVBoxLayout()         # Set box for plotting
        self.vbl.addWidget(self.toolbar)
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)

        stsh = """border-color: rgb(238, 238, 238); border-width : 2px; border-style:solid;"""
        self.setStyleSheet(stsh)


class Inheritance(QtWidgets.QMainWindow):
    def __init__(self, parent=None, config=None, ui=None):
        super().__init__(parent)

        if config is None:
            self.configuration = parent_configuration.Inheritance()
            self.configuration.load()
        else:
            self.configuration = config

        self.ui = uic.loadUi(ui, self)

        try:
            self.setWindowIcon(QtGui.QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)), "logo.png")))
        except:
            pass


        self.ui.setWindowFlag(QtCore.Qt.CustomizeWindowHint, True)
        self.ui.setWindowFlag(QtCore.Qt.WindowMinMaxButtonsHint, False)
        self.ui.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, False)
        self.ui.setWindowFlag(QtCore.Qt.WindowMinimizeButtonHint, True)
        self.ui.centralwidget.setWindowState(self.ui.centralwidget.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.ui.centralwidget.activateWindow()

        list_mpl = []
        for parent_widget in self.ui.centralwidget.children():
            if "layout" in parent_widget.objectName().lower():
                for widget in parent_widget.children():
                    if widget.objectName().startswith("mpl_"):
                        oname = widget.objectName()
                        opos = parent_widget.layout().getItemPosition(parent_widget.layout().indexOf(widget))
                        parent_widget.layout().removeWidget(widget)
                        widget.close()
                        widget.deleteLater()
                        widget = QWidgetMatplotlib(parent_widget)#myDumpBox(self.ui.centralwidget)
                        widget.setObjectName(oname)
                        parent_widget.layout().addWidget(widget, opos[0], opos[1], opos[2], opos[3])
                        parent_widget.update()
                        exec("self." + oname + " = parent_widget.children()[-1]")
                        list_mpl.append(oname)

        try:
            for mpl in list_mpl:
                exec("self." + mpl + ".canvas.ax.imshow(matplotlib.pyplot.imread(self.configuration.path_icon_mpl))")
                exec("self." + mpl + ".canvas.ax.grid(False)")
                exec("self." + mpl + ".canvas.ax.xaxis.set_visible(False)")
                exec("self." + mpl + ".canvas.ax.yaxis.set_visible(False)")
                exec("self.mpl_image.canvas.ax.set_frame_on(False)")
                exec("self." + mpl + ".canvas.draw()")
        except:
            pass

        for parent_widget in self.ui.centralwidget.children():
            try:
                parent_widget.setFont(QtGui.QFont("Arial", 12))

                #screen = QtGui.QGuiApplication.primaryScreen()
                #ratio = screen.devicePixelRatio()
                #a = 0
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
