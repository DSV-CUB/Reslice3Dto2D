import sys
import os
import numpy as np
import pydicom
from PyQt5 import QtWidgets

from sourcecode import basic_gui, basic_functions

class GUI(basic_gui.Inheritance_Dialog):
    def __init__(self, parent):
        if getattr(sys, 'frozen', False):
            uipath=os.path.join(sys._MEIPASS, "gui_dialog_stack.ui")
        else:
            uipath = __file__.replace(".py", ".ui")

        super().__init__(parent, uipath)
        self.result = None

        self.btn_stack.clicked.connect(self.btn_stack_clicked)

        serieses = np.unique([str(self.parent().selecteddata.data["seriesnumber"][i]).zfill(4) + " | " + self.parent().selecteddata.data["seriesdescription"][i] for i in range(len(self.parent().selecteddata.data["seriesdescription"]))]).flatten()
        self.lst_serieses.clear()
        self.lst_serieses.addItems(serieses)
        return

    def closeEvent(self, event):
        event.accept()
        return

    def btn_stack_clicked(self):
        serieses = self.lst_serieses.selectedItems()
        sd = self.txt_description.text().replace("|", "").strip()

        if len(serieses) < 1:
            self.show_dialog("Stacking not possible: Please select at least one series", "Warning")
            return

        if sd == "":
            self.show_dialog("Stacking not possible: Please provide a Series Description for the new 3D data stack.", "Warning")
            return

        sns = [int(serieses[i].text().split(" | ")[0]) for i in range(len(serieses))]
        ic = [] # counts images per selected series
        si = [] # selected indeces
        for i in range(len(sns)):
            sni = np.argwhere(np.array(self.parent().selecteddata.data["seriesnumber"]) == sns[i]).flatten()
            sni = sni[np.argsort(np.array(self.parent().selecteddata.data["instancenumber"])[sni])]
            si.append(sni)
            ic.append(len(sni))

        if len(np.unique(np.array(ic))) > 1:
            self.show_dialog("Stacking not possible: At least one selcted series has a different amount of instances than the other(s).", "Warning")
            return

        si = np.concatenate(si)

        if len(np.unique(np.array(self.parent().selecteddata.data["imageorientation"])[si],axis=0)) > 1:
            self.show_dialog("Stacking not possible: The chosen serieses are not parallel as they do not have equal imageorientations (DICOM tag (0x0020 0x0037))", "Warning")
            return

        rps = [] # reference points (upper left corner)
        pas = [] # pixel array shapes
        for i in range(len(si)):
            dcm = pydicom.dcmread(self.parent().selecteddata.data["filepath"][si[i]], force=True)
            rps.append(np.array(basic_functions.transform_ics_to_rcs(dcm, np.array([[0,0]]))).flatten())
            pas.append(np.array(np.shape(dcm.pixel_array)).flatten())

        if len(np.unique(np.array(pas), axis=0)) > 1:
            self.show_dialog("Stacking not possible: The chosen serieses have different pixel array sizes.", "Warning")
            return

        stackvectors = np.unique(np.array(rps), axis=0)
        stackvectors = (stackvectors - stackvectors[0])[1:]

        if len(stackvectors) == 0:
            self.show_dialog("Stacking not possible: The chosen serieses are all at the same image plane position (DICOM tag (0x0020, 0x0032))", "Warning")
            return

        if len(np.unique(np.round(np.abs(stackvectors / np.linalg.norm(stackvectors, axis=1)[:,None]), 4), axis=0)) > 1:
            self.show_dialog("Stacking not possible: The chosen serieses are not aligned.", "Warning")
            return

        for key in self.parent().selecteddata.data.keys():
            if key == "seriesnumber":
                self.parent().selecteddata.data[key] = self.parent().selecteddata.data[key] + [np.max((np.max(np.array(self.parent().selecteddata.data["seriesnumber"]))+1, 10000))] * len(si)
                self.parent().data.data[key] = self.parent().data.data[key] + [np.max((np.max(np.array(self.parent().selecteddata.data["seriesnumber"]))+1, 1000))] * len(si)
            elif key == "seriesdescription":
                self.parent().selecteddata.data[key] = self.parent().selecteddata.data[key] + [sd] * len(si)
                self.parent().data.data[key] = self.parent().data.data[key] + [sd] * len(si)
            elif key == "instancenumber":
                self.parent().selecteddata.data[key] = self.parent().selecteddata.data[key] + np.arange(1, len(si)+1, 1).tolist()
                self.parent().data.data[key] = self.parent().data.data[key] + np.arange(1, len(si)+1, 1).tolist()
            elif key == "acquisitiontype":
                self.parent().selecteddata.data[key] = self.parent().selecteddata.data[key] + ["3D"] * len(si)
                self.parent().data.data[key] = self.parent().data.data[key] + ["3D"] * len(si)
            else:
                self.parent().selecteddata.data[key] = self.parent().selecteddata.data[key] + np.array(self.parent().selecteddata.data[key])[si].tolist()
                self.parent().data.data[key] = self.parent().data.data[key] + np.array(self.parent().selecteddata.data[key])[si].tolist()

        self.parent().lst_serieses.addItem(str(self.parent().selecteddata.data["seriesnumber"][-1]).zfill(4) + " | " + sd)
        self.parent().dd_series3D.addItem(str(self.parent().selecteddata.data["seriesnumber"][-1]).zfill(4) + " | " + sd)
        self.parent().dd_series3D.setCurrentText(str(self.parent().selecteddata.data["seriesnumber"][-1]).zfill(4) + " | " + sd)
        self.parent().dd_series3D.view().setMinimumWidth(self.parent().dd_series3D.view().sizeHintForColumn(0))

        self.result = True
        self.accept()
        return


if __name__ == "__main__":
    global gui_run
    app = QtWidgets.QApplication(sys.argv)
    gui_run = GUI()
    gui_run.show()
    sys.exit(app.exec_())
