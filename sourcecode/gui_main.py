from PyQt5 import QtWidgets, QtGui, QtCore
import sys
import numpy as np
import qimage2ndarray
import copy
import pydicom
from pydicom.uid import generate_uid

from sourcecode import basic_data, basic_functions, basic_gui, gui_dialog_stack

class GUI(basic_gui.Inheritance_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent, __file__.replace(".py", ".ui"))

        self.data = basic_data.Setup()

        self.btn_load.clicked.connect(self.btn_load_clicked)
        self.btn_stack.clicked.connect(self.btn_stack_clicked)
        self.btn_export3D.setText(chr(129095))
        self.btn_export3D.clicked.connect(self.btn_export3D_clicked)


        self.dd_study.currentIndexChanged.connect(self.dd_study_changed)
        self.dd_study.setVisible(False)
        self.lbl_study.setVisible(False)

        self.dd_series3D.currentIndexChanged.connect(self.dd_series3D_changed)

        self.dd_sliceprofile.addItems(["rectangular", "triangular", "cosine + 1", "sinc", "standard normal 2", "standard normal 5"])

        self.opt_slicethickness_individual.toggled.connect(self.opt_slicethickness_individual_clicked)
        self.opt_slicethickness_2D.toggled.connect(self.opt_slicethickness_2D_clicked)
        self.opt_slicethickness_3D.toggled.connect(self.opt_slicethickness_3D_clicked)

        self.btn_add.clicked.connect(self.btn_add_clicked)
        self.btn_remove.clicked.connect(self.btn_remove_clicked)
        self.btn_reslice.clicked.connect(self.btn_reslice_clicked)

        self.pb_run.setVisible(False)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.timer_event)
        self.timer.start(100) # triggers every 100 miliseconds

        self.export_path = None
        self.selectedstudy = None
        self.selecteddata = None
        self.reslicetasks = {}
        self.draw3D_index = 0
        self.draw2D_index = 0

        self.thread = None
        self.worker = None
        self.thread_object = QtCore.QObject()
        QtCore.QThread.currentThread().setObjectName("main")
        return


    def btn_load_clicked(self):
        '''
        loads data from chosen directory and stores the information in the self.data variable
        :return:
        '''
        dirpath = self.get_directory(None)
        if not dirpath == "":
            data_load = basic_data.Setup(dirpath)
            if len(data_load.data["studyUID"]) > 0:
                self.selectedstudy = None
                self.selecteddata = None
                self.reslicetasks = {}
                self.draw3D_index = 0
                self.draw2D_index = 0
                self.lbl_hide.hide()
                self.data = data_load
                self.fill_data()
            else:
                self.show_dialog("No DICOM data found in given directory", "Information")
        return

    def btn_stack_clicked(self):
        '''
        opens dialog to stack multiple 2D data to 3D
        :return:
        '''
        dialog = gui_dialog_stack.GUI(self)
        dialog.exec()
        #if dialog.exec():
        #    print(dialog.result)
        return

    def btn_export3D_clicked(self):
        '''
        download the current 3D data (possibly needed if stacked)
        :return:
        '''
        if not self.export_path is None:
            self.export_path = self.get_directory(None, path=self.export_path)
        else:
            self.export_path = self.get_directory(None)

        if not self.export_path == "":
            basic_functions.save_stacked_dcm(self.selecteddata, int(self.dd_series3D.currentText().split(" | ")[0]), self.export_path)
            self.show_dialog("3D data export successfull")
        return

    def fill_data(self):
        '''
        fills list controls and resets choices from previous tasks
        :return:
        '''
        if self.selectedstudy is None:
            SUIDs = np.array(self.data.data["studyUID"])
            PNs = np.array(self.data.data["patientname"])
            uPNSUID = np.unique([PNs[i] + " | " + SUIDs[i] for i in range(len(SUIDs))]) # unique patientname SUIDs
            if len(uPNSUID) == 1:
                self.dd_study.setVisible(False)
                self.lbl_study.setVisible(False)
            else:
                self.dd_study.setVisible(True)
                self.lbl_study.setVisible(True)

            self.selectedstudy = -1
            self.dd_study.clear()
            self.dd_study.addItems(uPNSUID)
            self.dd_study.view().setMinimumWidth(self.dd_study.view().sizeHintForColumn(0))


        self.selectedstudy = self.dd_study.currentText().split(" | ")[1]
        self.selecteddata = self.data.get_subset(self.selectedstudy)

        indeces = np.argwhere(np.array(self.selecteddata.data["acquisitiontype"]) == "3D").flatten()
        if len(indeces) > 0:
            seriesnumber3d = np.array(self.selecteddata.data["seriesnumber"])[indeces]
            seriesdescription3d = np.array(self.selecteddata.data["seriesdescription"])[indeces]
            series3D = np.unique([str(seriesnumber3d[i]).zfill(4) + " | " + seriesdescription3d[i] for i in range(len(indeces))]).flatten()
            self.dd_series3D.clear()
            self.dd_series3D.addItems(series3D)
            self.dd_series3D.view().setMinimumWidth(self.dd_series3D.view().sizeHintForColumn(0))
        else:
            self.dd_series3D.clear()

        serieses = np.unique([str(self.selecteddata.data["seriesnumber"][i]).zfill(4) + " | " + self.selecteddata.data["seriesdescription"][i] for i in range(len(self.selecteddata.data["seriesdescription"]))]).flatten()
        self.lst_serieses.clear()
        self.lst_serieses.addItems(serieses)

        self.lst_reslices.clear()
        if self.selecteddata.data["studyUID"][0] in self.reslicetasks and len(self.reslicetasks[self.selecteddata.data["studyUID"][0]]) > 0: # restore reslice tasks if switched between studies
            self.lst_reslices.addItems(self.reslicetasks[self.selecteddata.data["studyUID"][0]])

        self.draw3D_index = 0
        self.draw2D_index = 0
        return


    def dd_study_changed(self, event):
        '''
        if loaded data contains data from multiple studys, then only one study can be worked on, therefore
        :param event:
        :return:
        '''
        if self.dd_study.count() > 0:
            self.fill_data()
        return

    def dd_series3D_changed(self, event):
        '''
        restarts the counter for the 3D print
        :param event:
        :return:
        '''
        self.draw3D_index = 0
        return

    def opt_slicethickness_individual_clicked(self):
        '''
        uncheck other slicethickness options and make their label grey to visualize which option is chosen
        :return:
        '''
        if self.opt_slicethickness_individual.isChecked():
            self.sb_slicethickness.setEnabled(True)
            self.lbl_slicethickness_mm.setEnabled(True)
            self.lbl_slicethickness_2D.setEnabled(False)
            self.lbl_slicethickness_3D.setEnabled(False)

            self.opt_slicethickness_2D.setChecked(False)
            self.opt_slicethickness_3D.setChecked(False)
        return

    def opt_slicethickness_2D_clicked(self):
        '''
        uncheck other slicethickness options and make their label grey to visualize which option is chosen
        :return:
        '''
        if self.opt_slicethickness_2D.isChecked():
            self.sb_slicethickness.setEnabled(False)
            self.lbl_slicethickness_mm.setEnabled(False)
            self.lbl_slicethickness_2D.setEnabled(True)
            self.lbl_slicethickness_3D.setEnabled(False)

            self.opt_slicethickness_individual.setChecked(False)
            self.opt_slicethickness_3D.setChecked(False)
        return

    def opt_slicethickness_3D_clicked(self):
        '''
        uncheck other slicethickness options and make their label grey to visualize which option is chosen
        :return:
        '''
        if self.opt_slicethickness_3D.isChecked():
            self.sb_slicethickness.setEnabled(False)
            self.lbl_slicethickness_mm.setEnabled(False)
            self.lbl_slicethickness_2D.setEnabled(False)
            self.lbl_slicethickness_3D.setEnabled(True)

            self.opt_slicethickness_2D.setChecked(False)
            self.opt_slicethickness_individual.setChecked(False)
        return

    def timer_event(self):
        '''
        draws in the two image labels the 3D selected data and the selected 2D data whenever the timer event is called
        :return:
        '''
        if not self.selecteddata is None:
            if not self.dd_series3D.currentText() == "":
                indeces = np.argwhere(np.array(self.selecteddata.data["seriesnumber"]) == int(self.dd_series3D.currentText().split(" | ")[0])).flatten()
                indeces = indeces[np.argsort(np.array(self.selecteddata.data["instancenumber"])[indeces])]
                if self.draw3D_index >= len(indeces):
                    self.draw3D_index = 0
                index = indeces[self.draw3D_index]
                self.draw3D_index = self.draw3D_index + 1
                self.draw_image(self.lbl_image_view, basic_functions.get_pixel_data(self.selecteddata.data["filepath"][index], rescale=False))
            else:
                self.draw_image(self.lbl_image_view, None)

            selected = self.lst_serieses.selectedItems()
            if len(selected) > 0:
                serieses = []
                for i in range(len(selected)):
                    serieses.append(int(selected[i].text().split(" | ")[0]))
                serieses = np.array(serieses)

                indeces = []
                for series in serieses:
                    indeces_series = np.argwhere(self.selecteddata.data["seriesnumber"]==series).flatten()
                    indeces_series = indeces_series[np.argsort(np.array(self.selecteddata.data["instancenumber"])[indeces_series])]
                    indeces = indeces + indeces_series.tolist()
                indeces = np.array(indeces)
                #indeces = np.argwhere(np.isin(np.array(self.selecteddata.data["seriesnumber"]), np.array(serieses))).flatten()
                if self.draw2D_index >= len(indeces):
                    self.draw2D_index = 0
                index = indeces[self.draw2D_index]
                self.draw2D_index = self.draw2D_index + 1
                self.draw_image(self.lbl_image_view_2, basic_functions.get_pixel_data(self.selecteddata.data["filepath"][index], rescale=False, representation=True))
            else:
                self.draw_image(self.lbl_image_view_2, None)
        return

    def draw_image(self, label, pixeldata):
        '''
        draws images into labels
        :param label: label to draw in
        :param pixeldata: image data, if None, then the image is white filled
        :return:
        '''
        if pixeldata is None:
            image = qimage2ndarray.array2qimage(255 * np.ones((10,10)))
        else:
            sizex, sizey = np.shape(pixeldata)
            if sizex > sizey:
                delta = int((sizex-sizey)/2)
                pdcrop = pixeldata[delta:sizey+delta,:]
            elif sizey > sizex:
                delta = int((sizey-sizex)/2)
                pdcrop = pixeldata[:,delta:sizex+delta]
            else:
                pdcrop = pixeldata
            image = qimage2ndarray.array2qimage(pdcrop, normalize=True)

        pixmap = QtGui.QPixmap.fromImage(image)

        if pixmap.height() > pixmap.width():
            pixmap = pixmap.scaledToHeight(label.height())
        else:
            pixmap = pixmap.scaledToWidth(label.width())

        label.setPixmap(pixmap)
        return

    def btn_add_clicked(self):
        '''
        adds reslice tasks if not existing yet
        :return:
        '''
        series3D = self.dd_series3D.currentText()

        if series3D is None or series3D == "":
            return

        serieses = self.lst_serieses.selectedItems()
        ST = (str(self.sb_slicethickness.value()) + " mm" if self.opt_slicethickness_individual.isChecked() else ("as 2D" if self.opt_slicethickness_2D.isChecked() else "as 3D"))

        for i in range(len(serieses)):
            convert = series3D + " | " + serieses[i].text() + " | " + self.dd_sliceprofile.currentText() + " | " + ST

            exist=False
            for j in range(self.lst_reslices.count()):
                if self.lst_reslices.item(j).text() == convert:
                    exist=True
                    break

            if not exist:
                self.lst_reslices.addItem(convert)

        self.reslicetasks[self.selecteddata.data["studyUID"][0]] = [self.lst_reslices.item(x).text() for x in range(self.lst_reslices.count())]
        return

    def btn_remove_clicked(self):
        '''
        drops selected reslice tasks
        :return:
        '''
        selected = self.lst_reslices.selectedItems()
        for item in selected:
            self.lst_reslices.takeItem(self.lst_reslices.row(item))

        self.reslicetasks[self.selecteddata.data["studyUID"][0]] = [self.lst_reslices.item(x).text() for x in range(self.lst_reslices.count())]
        return

    def btn_reslice_clicked(self):
        '''
        run reslice
        :return:
        '''
        if self.lst_reslices.count() > 0: # if no reslice tasks are available, do nothing
            if not self.export_path is None:
                self.export_path = self.get_directory(None, path=self.export_path)
            else:
                self.export_path = self.get_directory(None)

            if not self.export_path is None and not self.export_path == "":  #if no directory was chosen, do nothing
                self.pb_run.setVisible(True)
                self.enable_buttons(False)

                reslicetasks = [self.lst_reslices.item(x).text() for x in range(self.lst_reslices.count())]

                self.worker = Worker(self.selecteddata, reslicetasks, self.export_path)
                self.thread = QtCore.QThread(parent=self.thread_object)
                self.thread.setObjectName("thread")
                self.worker.moveToThread(self.thread)

                self.worker.sig_progress.connect(self.update_pb_run)
                self.worker.finished.connect(lambda: self.show_dialog("Export successfull"))
                self.worker.finished.connect(lambda: self.pb_run.setVisible(False))
                self.worker.finished.connect(lambda: self.enable_buttons(True))

                self.worker.finished.connect(self.thread.quit)
                self.worker.finished.connect(self.worker.deleteLater)

                self.thread.finished.connect(self.thread.deleteLater)

                self.thread.started.connect(self.worker.run)
                self.thread.start()

    def enable_buttons(self, enable):
        for pbn in self.ui.centralwidget.findChildren(QtWidgets.QPushButton):
            pbn.setEnabled(enable)
        return

    def update_pb_run(self, percentage):
        self.pb_run.setValue(int(np.clip(percentage, 0, 100)))
        return


class Worker(QtCore.QObject):
    '''
    thread worker
    '''
    finished = QtCore.pyqtSignal()
    sig_progress = QtCore.pyqtSignal(float)

    def __init__(self, data, tasks, path):
        super().__init__()
        self.data = data
        self.tasks = tasks
        self.path = path

    def run(self):
        '''
        run the reslice tasks in a seperated thread in order to not freeze the GUI
        :return:
        '''
        sn = -1
        taskpercent = 100 / len(self.tasks)
        for t in range(len(self.tasks)):
            task_commands = self.tasks[t].split(" | ")

            indeces3D = np.argwhere(np.array(self.data.data["seriesnumber"]) == int(task_commands[0])).flatten()
            indeces2D = np.argwhere(np.array(self.data.data["seriesnumber"]) == int(task_commands[2])).flatten()

            if str(task_commands[5]) == "as 2D":
                ST = self.data.data["slicethickness"][indeces2D[0]]
            elif str(task_commands[5]) == "as 3D":
                ST = self.data.data["slicethickness"][indeces3D[0]]
            else:
                ST = float(str(task_commands[5]).replace(" mm", ""))

            # evaluate 2D slices to evaluate at
            positions2D = np.unique(np.array(self.data.data["imageposition"])[indeces2D], axis=0)
            indexlist2D = []
            for p in range(len(positions2D)):
                iindeces = np.where((np.array(self.data.data["imageposition"])[indeces2D] == positions2D[p]).all(axis=1))[0]
                indexlist2D.append(indeces2D[iindeces][0])

            # evaluate 3D volumes (if 4D data or 3D cine is given, then cut into 3D blocks for each timepoint)
            positions3D = np.unique(np.array(self.data.data["imageposition"])[indeces3D], axis=0)
            timepoints = len(np.where((np.array(self.data.data["imageposition"])[indeces3D] == positions3D[0]).all(axis=1))[0])

            indexmatrix3D = np.zeros((timepoints, len(positions3D)))
            for p in range(len(positions3D)):
                iindeces = np.where((np.array(self.data.data["imageposition"])[indeces3D] == positions3D[p]).all(axis=1))[0]
                sortindeces = np.argsort(np.array(self.data.data["triggertime"])[indeces3D[iindeces]])
                sortindeces = indeces3D[iindeces][sortindeces]
                indexmatrix3D[:, p] = sortindeces
            indexmatrix3D = indexmatrix3D.astype(int)

            # run reslice
            dcms2D = []
            for i in range(len(indexlist2D)):
                dcms2D.append(pydicom.dcmread(self.data.data["filepath"][indexlist2D[i]]))

            instancenum = 1
            counter = 0
            sn = np.max((np.max(self.data.data["seriesnumber"])+1, 20000, sn+1))
            for i in range(len(indexmatrix3D)):
                dcms3D =[]
                for j in range(len(indexmatrix3D[i])):
                    dcms3D.append(pydicom.dcmread(self.data.data["filepath"][indexmatrix3D[i,j]]))

                for j in range(len(dcms2D)):
                    rpa = basic_functions.reslice(dcms3D, dcms2D[j], ST, task_commands[4])

                    dcm = copy.deepcopy(dcms2D[j])

                    dcm.PixelData = rpa.astype("int16").tobytes() # pixel data
                    dcm[0x0018, 0x0050].value = ST # slice thickness

                    # image display and value attributes
                    tags =["[0x0028, 0x1050]", "[0x0028, 0x1051]", "[0x0028, 0x1052]", "[0x0028, 0x1053]"]
                    # window center, winow width, slope, intercept
                    for tag in tags:
                        if eval(tag) in dcms3D[0] and not eval("dcms3D[0]" + tag + ".value") is None:
                            if eval(tag) in dcm:
                                exec("dcm" + tag + ".value = dcms3D[0]" + tag + ".value")
                            else:
                                exec("dcm.add_new(" + tag + ", \"DS\", dcms3D[0]" + tag + ".value")
                        elif eval(tag) in dcm:
                            exec("dcm" + tag + ".value = None")

                    dcm[0x0020, 0x0011].value = sn # series number
                    dcm[0x0008, 0x103e].value = "R3D2D_" + dcms3D[0][0x0008, 0x103e].value + "_" + dcm[0x0008, 0x103e].value + "_" + str(ST) + "mm_" + task_commands[4] # series description
                    dcm[0x0018, 0x1030].value = "R3D2D_" + dcms3D[0][0x0018, 0x1030].value # protocol name
                    dcm[0x0018, 0x1060].value = dcms3D[0][0x0018, 0x1060].value # trigger time
                    dcm[0x0020, 0x0013].value = instancenum #i+1 # instance number
                    dcm[0x0020, 0x000e].value = generate_uid(entropy_srcs=[str(sn), dcm[0x0008, 0x103e].value]) # series instance UID
                    dcm[0x0008, 0x0018].value = generate_uid(entropy_srcs=[str(sn), dcm[0x0008, 0x103e].value, str(instancenum)]) # SOP instance UID
                    dcm.file_meta[0x0002, 0x0003].value = generate_uid(entropy_srcs=[str(sn), dcm[0x0008, 0x103e].value, str(instancenum)]) # Media Storage SOP Instance UID
                    try:
                        dcm[0x6000, 0x3000].value = None
                    except:
                        pass

                    basic_functions.save_dcm(dcm, self.path, True)
                    instancenum = instancenum + 1
                    counter = counter + 1

                    self.sig_progress.emit(np.max((0,taskpercent * (t-1))) + (taskpercent * counter / (len(indexmatrix3D) * len(dcms2D)))) # update progress bar by tasks done and the part that is dne in the current task
        self.sig_progress.emit(0)
        self.finished.emit()
        return


if __name__ == "__main__":
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    global gui_run
    app = QtWidgets.QApplication(sys.argv)
    gui_run = GUI()
    gui_run.show()
    sys.exit(app.exec_())