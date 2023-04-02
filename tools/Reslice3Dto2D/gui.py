from PyQt5 import QtWidgets, QtGui, QtCore

import sys
import os
import numpy as np
import qimage2ndarray
import copy
import scipy.interpolate
from scipy.stats import norm
from datetime import datetime

from tools import __basics__
from tools.Reslice3Dto2D import dicom

class GUI(__basics__.parent_gui.Inheritance):
    def __init__(self, parent=None, config=None):
        super().__init__(parent, config, os.path.join(os.path.dirname(os.path.realpath(__file__)), "gui.ui"))

        self.dcm = None
        self.list_series = []
        self.indeces_include = []
        self.selected_num = -1
        self.selected_max = -1

        self.txt_load_path.mousePressEvent = self.txt_load_path_clicked
        self.btn_load.clicked.connect(self.btn_load_clicked)
        self.dd_series3D.currentIndexChanged.connect(self.dd_series3D_changed)
        self.btn_image_previous.clicked.connect(self.btn_image_previous_clicked)
        self.btn_image_next.clicked.connect(self.btn_image_next_clicked)
        self.btn_include.clicked.connect(self.btn_include_clicked)
        self.btn_include_all.clicked.connect(self.btn_include_all_clicked)
        self.btn_exclude.clicked.connect(self.btn_exclude_clicked)
        self.btn_exclude_all.clicked.connect(self.btn_exclude_all_clicked)
        self.btn_reslice.clicked.connect(self.btn_reslice_clicked)

        self.cb_reslice_one.stateChanged.connect(self.cb_reslice_one_clicked)
        self.cb_export_3D.stateChanged.connect(self.cb_export_3D_clicked)
        self.cb_export_exclude.stateChanged.connect(self.cb_export_exclude_clicked)
        self.cb_export_original.stateChanged.connect(self.cb_export_original_clicked)

        self.opt_slicethickness_individual.toggled.connect(self.opt_slicethickness_individual_clicked)
        self.opt_slicethickness_2D.toggled.connect(self.opt_slicethickness_2D_clicked)
        self.opt_slicethickness_3D.toggled.connect(self.opt_slicethickness_3D_clicked)

        self.lbl_image_view.setMouseTracking(True)
        self.lbl_image_view.mouseMoveEvent = self.lbl_image_view_move

        self.dd_sliceprofile.addItems(["rectangular", "triangular", "cosine + 1", "sinc", "standard normal 2", "standard normal 5"])
        self.export_path = None
        return

    def reset(self):
        self.dcm = None
        self.list_series = []
        self.indeces_include = []
        self.selected_num = -1
        self.selected_max = -1
        self.dd_series3D.clear()
        self.lst_exclude.clear()
        self.lst_include.clear()
        self.lbl_image_view.clear()
        self.lbl_image.setText("")
        return

    def txt_load_path_clicked(self, event):
        self.get_directory(self.txt_load_path)
        return

    def btn_load_clicked(self):
        if not self.txt_load_path.text() == "":
            self.reset()

            self.dcm = dicom.Setup(self.txt_load_path.text())
            unique_series_num = np.unique(self.dcm.series_num)

            index3D = 0
            for i in unique_series_num:
                index = np.argmax(self.dcm.series_num==i)
                self.list_series.append(str(i).rjust(4, "0") + " | " + self.dcm.series[index])
                try:
                    if index3D == 0 and self.dcm.obj[index][0x0018, 0x0023].value == "3D": # MR Acquisition type
                        index3D = len(self.list_series) - 1
                except:
                    pass


            if len(self.list_series) > 0:
                self.indeces_include = np.zeros((len(self.list_series), 1)).flatten()
                self.dd_series3D.addItems(self.list_series)
                self.dd_series3D.setCurrentIndex(index3D)
                self.dd_series3D_changed(None)
                self.update_lists()
            else:
                self.draw_image()
        return

    def dd_series3D_changed(self, event):
        if not self.dcm is None and len(self.dcm.obj) > 0:
            self.selected_num = 0
            series_num = int(self.dd_series3D.currentText()[:self.dd_series3D.currentText().find(" ")])
            self.selected_max = len(np.argwhere(np.array(self.dcm.series_num).astype(int)==series_num)) - 1
            self.update_lists()
            self.draw_image()
        return

    def btn_image_previous_clicked(self):
        if not self.dcm is None and len(self.dcm.obj) > 0:
            if self.selected_num > 0:
                self.selected_num = self.selected_num - 1
                self.draw_image()
        return

    def btn_image_next_clicked(self):
        if not self.dcm is None and len(self.dcm.obj) > 0:
            if self.selected_num < self.selected_max:
                self.selected_num = self.selected_num + 1
                self.draw_image()
        return

    def btn_include_clicked(self):
        if not self.lst_exclude.currentItem() is None:
            for item in self.lst_exclude.selectedItems():
                index = int(np.argwhere(np.array(self.list_series) == item.text())) #self.lst_exclude.currentItem().text()))
                self.indeces_include[index] = 1

            self.update_lists()
        return

    def btn_include_all_clicked(self):
        self.indeces_include = np.ones((len(self.list_series), 1)).flatten()
        index = int(np.argwhere(np.array([self.list_series[i][:self.list_series[i].find(" ")] for i in range(len(self.list_series))]) == self.dd_series3D.currentText()[:self.dd_series3D.currentText().find(" ")]))
        self.indeces_include[index] = 0
        self.update_lists()
        return

    def btn_exclude_clicked(self):
        if not self.lst_include.currentItem() is None:
            for item in self.lst_include.selectedItems():
                index = int(np.argwhere(np.array(self.list_series) == item.text())) #self.lst_include.currentItem().text()))
                self.indeces_include[index] = 0

            self.update_lists()
        return

    def btn_exclude_all_clicked(self):
        self.indeces_include = np.zeros((len(self.list_series), 1)).flatten()
        self.update_lists()
        return

    def cb_reslice_one_clicked(self):
        self.lbl_reslice_one.setEnabled(self.cb_reslice_one.isChecked())
        return

    def cb_export_3D_clicked(self):
        self.lbl_export_3D.setEnabled(self.cb_export_3D.isChecked())
        return

    def cb_export_exclude_clicked(self):
        self.lbl_export_exclude.setEnabled(self.cb_export_exclude.isChecked())
        return

    def cb_export_original_clicked(self):
        self.lbl_export_original.setEnabled(self.cb_export_original.isChecked())
        return

    def opt_slicethickness_individual_clicked(self):
        if self.opt_slicethickness_individual.isChecked():
            self.sb_slicethickness.setEnabled(True)
            self.lbl_slicethickness_mm.setEnabled(True)
            self.lbl_slicethickness_2D.setEnabled(False)
            self.lbl_slicethickness_3D.setEnabled(False)

            self.opt_slicethickness_2D.setChecked(False)
            self.opt_slicethickness_3D.setChecked(False)
        return

    def opt_slicethickness_2D_clicked(self):
        if self.opt_slicethickness_2D.isChecked():
            self.sb_slicethickness.setEnabled(False)
            self.lbl_slicethickness_mm.setEnabled(False)
            self.lbl_slicethickness_2D.setEnabled(True)
            self.lbl_slicethickness_3D.setEnabled(False)

            self.opt_slicethickness_individual.setChecked(False)
            self.opt_slicethickness_3D.setChecked(False)
        return

    def opt_slicethickness_3D_clicked(self):
        if self.opt_slicethickness_3D.isChecked():
            self.sb_slicethickness.setEnabled(False)
            self.lbl_slicethickness_mm.setEnabled(False)
            self.lbl_slicethickness_2D.setEnabled(False)
            self.lbl_slicethickness_3D.setEnabled(True)

            self.opt_slicethickness_2D.setChecked(False)
            self.opt_slicethickness_individual.setChecked(False)
        return

    def btn_reslice_clicked(self):
        if not self.export_path is None:
            self.export_path = self.get_directory(None, path=self.export_path)
        else:
            self.export_path = self.get_directory(None)

        if not self.export_path is None and not self.export_path == "" and not self.dcm is None and len(self.dcm.obj) > 0:

            if self.opt_slicethickness_individual.isChecked():
                evaluate_slice_thickness = float(self.sb_slicethickness.value())
            elif self.opt_slicethickness_2D.isChecked():
                evaluate_slice_thickness = None
            elif self.opt_slicethickness_3D.isChecked():
                evaluate_slice_thickness = int(0)
            else:
                self.show_dialog("Slice Thickness not defined.", "Critical")
                return

            data_3D = []
            data_3D_value = np.array([])
            data_3D_window_center = None
            data_3D_window_width = None
            data_3D_slice_thickness = 0
            data_3D_x = np.array([])
            data_3D_y = np.array([])
            data_3D_z = np.array([])
            timestamp = datetime.now().strftime("%y%m%d%H%M%S%f")

            indeces = np.argwhere(np.array(self.dcm.series_num) == int(self.dd_series3D.currentText()[:self.dd_series3D.currentText().find(" ")])).flatten()

            for i in indeces:
                read = self.dcm.obj[i]
                try:
                    if data_3D_value.shape[0] == 0:
                        data_3D_value = np.asarray([read.pixel_array])

                        if [0x0028, 0x1050] in read:
                            data_3D_window_center = int(read[0x0028, 0x1050].value)
                        if [0x0028, 0x1051] in read:
                            data_3D_window_width = int(read[0x0028, 0x1051].value)

                        data_3D_slice_thickness = np.asarray(read[0x0018, 0x0050].value, np.double)

                        data_3D_x = np.arange(0, read.pixel_array.shape[1], 1) * read.PixelSpacing[1] + read.ImagePositionPatient[0]
                        data_3D_y = np.arange(0, read.pixel_array.shape[0], 1) * read.PixelSpacing[0] + read.ImagePositionPatient[1]
                        data_3D_z = np.asarray([read.ImagePositionPatient[2]])
                    else:
                        data_3D_value = np.append(data_3D_value, np.asarray([read.pixel_array]), axis=0)
                        data_3D_z = np.append(data_3D_z, np.asarray([read.ImagePositionPatient[2]]))

                    data_3D.append(read)
                except KeyError:
                    pass

            list_export = []

            if len(data_3D) <= 1:
                self.show_dialog("The selected 3D series is not 3D or slices are missing", "Warning", False)
            elif abs(data_3D_z[1] - data_3D_z[0]) == 0:
                self.show_dialog("There is a gap of 0 between two slices in the 3D dataset, please check for consistency", "Warning", False)
            elif len(data_3D) > 1:
                sorted_index = np.argsort(data_3D_z)
                data_3D_z = data_3D_z[sorted_index]
                data_3D_value = data_3D_value[sorted_index, :, :]

                for i in range(len(self.indeces_include)):

                    indeces_dcm = np.argwhere(np.array(self.dcm.series_num) == int(self.list_series[i][:self.list_series[i].find(" ")])).flatten()
                    if self.cb_reslice_one.isChecked() and len(indeces_dcm) > 1 and self.indeces_include[i] == 1:
                        indeces_dcm = [indeces_dcm[0]]

                    for j in indeces_dcm:
                        if self.dcm.series_num[j] == int(self.dd_series3D.currentText()[:self.dd_series3D.currentText().find(" ")]) and self.cb_export_3D.isChecked():
                            list_export.append(self.dcm.obj[j])
                        else:
                            if (self.indeces_include[i] == 0 and self.cb_export_exclude.isChecked()) or (self.indeces_include[i] == 1 and self.cb_export_original.isChecked()):
                                list_export.append(self.dcm.obj[j])

                            if self.indeces_include[i] == 1: # reslice
                                read = copy.deepcopy(self.dcm.obj[j])
                                # read in relevant dicom tags
                                try:
                                    image_position = np.asarray(read[0x0020, 0x0032].value, np.double)
                                    direction_cosine = np.asarray(read[0x0020, 0x0037].value, np.double)
                                    pixel_spacing = np.asarray(read[0x0028, 0x0030].value, np.double)

                                    if evaluate_slice_thickness is None:
                                        slice_thickness = np.asarray(read[0x0018, 0x0050].value, np.double)
                                    elif evaluate_slice_thickness == 0:
                                        slice_thickness = data_3D_slice_thickness
                                    elif evaluate_slice_thickness > 0:
                                        slice_thickness = evaluate_slice_thickness
                                    else:
                                        raise ValueError("The given evaluate_slice_thickness is neither None, 0 nor >0. Abortion.")
                                except:
                                    continue

                                # create the matrix to transform indices of slice to coordinates
                                matrix = np.zeros((3, 3))
                                matrix[0, 0] = direction_cosine[0]
                                matrix[1, 0] = direction_cosine[1]
                                matrix[2, 0] = direction_cosine[2]
                                matrix[0, 1] = direction_cosine[3]
                                matrix[1, 1] = direction_cosine[4]
                                matrix[2, 1] = direction_cosine[5]
                                # for z-direction
                                #matrix[0:3, 2] = np.cross(direction_cosine[0:3], direction_cosine[3:]) / np.linalg.norm(np.cross(direction_cosine[0:3], direction_cosine[3:]))

                                # all x, y combinations of slice
                                x = np.arange(0, read.pixel_array.shape[1], 1)
                                y = np.arange(0, read.pixel_array.shape[0], 1)
                                X, Y = np.meshgrid(x,y)
                                x = np.reshape(X, -1)
                                y = np.reshape(Y, -1)

                                # vector for matrix vector product to transform indices of slice to coordinates
                                vector = np.zeros((x.shape[0], 3))
                                vector[:, 0] = x * pixel_spacing[1]
                                vector[:, 1] = y * pixel_spacing[0]

                                # transformation
                                product = np.transpose(np.dot(matrix, np.transpose(vector)))  # x y z
                                product = np.add(product[:, 0:3], image_position.reshape((1, 3)))

                                # evaluate the orthogonal normal of the slice
                                v1 = product[1, :] - product[0, :]
                                v2 = product[read.pixel_array.shape[0], :] - product[0, :]
                                n = np.cross(v1, v2)
                                n = n / np.linalg.norm(n)

                                # number of points above and under the evaluation point along the normal
                                num = int(round(np.round(slice_thickness, 2) / np.round((2*data_3D_slice_thickness), 2)))
                                # distance of the points (close to 3D resolution)
                                if num > 0:
                                    dist = slice_thickness / (2*num)
                                else:
                                    dist = 0

                                # creates shifted slices, evaluates the interpolated values and weights them (here all the same weight = average)
                                weights = []
                                interpolate = np.zeros(product.shape[0])

                                for k in range(-num, num+1):
                                    if k == 0:
                                        weights.append(1)
                                    elif self.dd_sliceprofile.currentText() == "rectangular":
                                        weights.append(1)
                                    elif self.dd_sliceprofile.currentText() == "triangular":
                                        weights.append((num-abs(k))/num)
                                    elif self.dd_sliceprofile.currentText() == "cosine + 1":
                                        weights.append((np.cos((k/num) * np.pi) + 1) / 2)
                                    elif self.dd_sliceprofile.currentText() == "sinc":
                                        weights.append(np.sinc(k/num))
                                    elif self.dd_sliceprofile.currentText() == "standard normal 2":
                                        weights.append(norm.pdf(2 * (k/num), loc=0, scale=1) / norm.pdf(0, loc=0, scale=1))
                                    elif self.dd_sliceprofile.currentText() == "standard normal 5":
                                        weights.append(norm.pdf(5 * (k/num), loc=0, scale=1) / norm.pdf(0, loc=0, scale=1))
                                    else:
                                        self.show_dialog("Slice profile not implemented.", "Critical")
                                        return

                                    slice_2D = np.copy(product) + (n * dist * k)
                                    slice_2D[:,[0,1,2]] = slice_2D[:,[2,1,0]]
                                    interpolate = interpolate + weights[-1] * scipy.interpolate.interpn((data_3D_z,data_3D_y,data_3D_x), data_3D_value, slice_2D, bounds_error=False, fill_value=0)

                                interpolate = np.round(interpolate / np.sum(weights), 0).astype(int)



                                # writes back the interpolated values into the Pixel Data of the dicom
                                new_pixel_array = np.copy(read.pixel_array)
                                new_pixel_array[y,x] = interpolate

                                # change pixel array and corresponding slice thickness
                                read.PixelData = new_pixel_array.astype("int16").tobytes()
                                read[0x0018, 0x0050].value = str(slice_thickness)

                                if not data_3D_window_center is None:
                                    if [0x0028, 0x1050] in read:
                                        read[0x0028, 0x1050].value = str(data_3D_window_center)
                                    else:
                                        read.add_new([0x0028, 0x1050], "DS", str(data_3D_window_center))

                                if not data_3D_window_width is None:
                                    if [0x0028, 0x1051] in read:
                                        read[0x0028, 0x1051].value = str(data_3D_window_width)
                                    else:
                                        read.add_new([0x0028, 0x1051], "DS", str(data_3D_window_width))

                                # change some tags to make clear it is resliced
                                new_series_num = str(data_3D[0][0x0020, 0x0011].value) + str(read[0x0020, 0x0011].value + len(self.list_series))

                                read[0x0018, 0x1030].value = "Reslice3Dto2D_" + data_3D[0][0x0008, 0x103E].value # Protocol Name

                                uid_add = "." + timestamp + "." + new_series_num + "." + str(read[0x0020, 0x0013].value)
                                read.file_meta[0x0002, 0x0003].value = read.file_meta[0x0002, 0x0003].value[:-len(uid_add)] + uid_add # Media Storage SOP Instance UID
                                read[0x0008, 0x0018].value = read[0x0008, 0x0018].value[:-len(uid_add)] + uid_add# SOP Instance UID #str(data_3D[0][0x0008, 0x0018].value[:28])
                                #read[0x0008, 0x0018].value = pydicom.uid.PYDICOM_ROOT_UID + timestamp + "." + new_series_num + "." + str(read[0x0020, 0x0013].value)

                                uid_add = "." + timestamp + "." + new_series_num + ".0.0.0"
                                read[0x0020, 0x000e].value = read[0x0020, 0x000e].value[:-len(uid_add)] + uid_add #str(data_3D[0][0x0020, 0x000e].value[:28]) + timestamp + "." + new_series_num + ".0.0.0" # Series Instance UID

                                read[0x0008, 0x1030].value = "Reslice3Dto2D" # Study Description
                                read[0x0020, 0x0011].value =  int(new_series_num) # series num
                                #read[0x0008, 0x0020].value = "19000101"
                                #read[0x0008, 0x0021].value = "19000101"
                                #read[0x0008, 0x0022].value = "19000101"
                                #read[0x0008, 0x0023].value = "19000101"
                                read[0x0008, 0x103E].value = "rs3dt2d_" + data_3D[0][0x0008, 0x103E].value + "_" + read[0x0008, 0x103E].value # Series Description

                                try:
                                    read[0x6000, 0x3000].value = None
                                except:
                                    pass

                                list_export.append(copy.copy(read))

            for dcm in list_export:
                __basics__.functions.save_dcm(dcm, self.export_path)


            if len(list_export) > 0:
                self.show_dialog("Reslice done.", "Information", False)
                return

        self.show_dialog("Nothing to Export.", "Warning", False)
        return

    def update_lists(self):
        self.lst_exclude.clear()
        exclude_indeces = np.argwhere(self.indeces_include == 0).flatten()
        exclude_indeces = exclude_indeces[exclude_indeces != self.dd_series3D.currentIndex()]
        self.lst_exclude.addItems(np.array(self.list_series)[exclude_indeces])


        self.lst_include.clear()
        include_indeces = np.argwhere(self.indeces_include == 1).flatten()
        include_indeces = include_indeces[include_indeces != self.dd_series3D.currentIndex()]
        self.lst_include.addItems(np.array(self.list_series)[include_indeces])

        return

    def lbl_image_view_move(self, event):
        if not self.dcm is None and len(self.dcm.obj) > 0:
            # mouse move
            y = round(event.pos().x() / self.image_ratio)
            x = round(event.pos().y() / self.image_ratio)

            if x < np.shape(self.selected_data)[0] and y < np.shape(self.selected_data)[1]:
                self.lbl_image.setText(str(self.selected_num+1) + " of " + str(self.selected_max + 1) + " || ( " + str(x) + " , " + str(y) + " ) || " + str(self.selected_data[x, y]))

    def draw_image(self):
        if len(self.dcm.obj) > 0:
            series_num = int(self.dd_series3D.currentText()[:self.dd_series3D.currentText().find(" ")])
            indeces = np.argwhere(np.array(self.dcm.series_num).astype(int)==series_num)
            index = int(indeces[self.selected_num][0])

            self.selected_data = self.dcm.get_pixel_data(index, rescale=True)
            image = qimage2ndarray.array2qimage((255 * self.selected_data / np.max(self.selected_data)))
            pixmap = QtGui.QPixmap.fromImage(image)

            if np.shape(self.selected_data)[0] > np.shape(self.selected_data)[1]:
                pixmap = pixmap.scaledToHeight(570)
                self.image_ratio = 570 / np.shape(self.selected_data)[0]

            else:
                pixmap = pixmap.scaledToWidth(570)
                self.image_ratio = 570 / np.shape(self.selected_data)[1]

            self.lbl_image_view.setPixmap(pixmap)
            self.lbl_image.setText(str(self.selected_num+1) + " of " + str(self.selected_max + 1))
        return

if __name__ == "__main__":
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    global gui_run
    app = QtWidgets.QApplication(sys.argv)
    gui_run = GUI()
    gui_run.show()
    sys.exit(app.exec_())