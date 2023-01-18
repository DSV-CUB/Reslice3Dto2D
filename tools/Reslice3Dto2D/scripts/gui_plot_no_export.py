import sys
import os
import numpy as np
from PyQt5 import QtWidgets, QtGui
import qimage2ndarray
import copy
import scipy.interpolate
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

        self.lbl_image_view.setMouseTracking(True)
        self.lbl_image_view.mouseMoveEvent = self.lbl_image_view_move

        return

    def reset(self):
        self.dcm = None
        self.list_series = []
        self.indeces_include = []
        self.selected_num = -1
        self.selected_max = -1
        self.dd_series3D.clear()
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
        if not self.dcm is None:
            self.selected_num = 0
            series_num = int(self.dd_series3D.currentText()[:self.dd_series3D.currentText().find(" ")])
            self.selected_max = len(np.argwhere(np.array(self.dcm.series_num).astype(int)==series_num)) - 1
            self.update_lists()
            self.draw_image()
        return

    def btn_image_previous_clicked(self):
        if not self.dcm is None:
            if self.selected_num > 0:
                self.selected_num = self.selected_num - 1
                self.draw_image()
        return

    def btn_image_next_clicked(self):
        if not self.dcm is None:
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

    def btn_reslice_clicked(self):

        evaluate_slice_thickness = self.txt_slice_thickness.text().strip()

        if evaluate_slice_thickness == ".":
            evaluate_slice_thickness = None # 2D data slice thickness
        else:
            if evaluate_slice_thickness.endswith("."):
                evaluate_slice_thickness = evaluate_slice_thickness[:-1]

            if float(evaluate_slice_thickness) == 0.0:
                evaluate_slice_thickness = int(0) # 3D data slice thickness
            else:
                evaluate_slice_thickness = float(evaluate_slice_thickness) # any slice thickness

        data_3D = []
        data_3D_value = np.array([])
        data_3D_window_center = None
        data_3D_window_width = None
        data_3D_slice_thickness = 0
        data_3D_z_resolution = 0
        data_3D_x = np.array([])
        data_3D_y = np.array([])
        data_3D_z = np.array([])
        timestamp = datetime.now().strftime("%y%m%d%H%M%S%f")

        indeces = np.argwhere(np.array(self.dcm.series_num)==int(self.dd_series3D.currentText()[:self.dd_series3D.currentText().find(" ")])).flatten()

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
            data_3D_z_resolution = abs(data_3D_z[1] - data_3D_z[0])

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
                            num = int(round(slice_thickness / (2*data_3D_z_resolution)))
                            # distance of the points (close to 3D resolution)
                            if num > 0:
                                dist = slice_thickness / (2*num)
                            else:
                                dist = 0

                            ### PLOT ###
                            import matplotlib
                            matplotlib.use('Qt5Agg')
                            from matplotlib import pyplot as plt
                            from matplotlib.colors import ListedColormap

                            # create own colormap
                            newcolors = np.ones((256, 4))
                            newcolors[:,1] = 0
                            newcolors[:,2] = 0
                            redcmp = ListedColormap(newcolors)

                            newcolors = np.ones((256, 4))
                            newcolors[:,0] = 0
                            newcolors[:,2] = 0
                            greencmp = ListedColormap(newcolors)


                            scatterx, scattery, scatterz = np.meshgrid(data_3D_x,data_3D_y,data_3D_z)

                            # PLOT 1
                            fig = plt.figure(1)
                            ax = fig.add_subplot(projection='3d')

                            ax.scatter(scatterx, scattery, scatterz, c="blue", s=1)
                            ax.scatter(product[:,0], product[:,1], product[:,2], c="red")
                            ax.plot_trisurf(product[:,0], product[:,1], product[:,2], edgecolor=(1,0,0,0.33), linewidth=0, antialiased=True, cmap=redcmp, alpha=0.33)

                            ax.set_xticks([])
                            ax.set_yticks([])
                            ax.set_zticks([])
                            #ax.set_axis_off()
                            ax.view_init(0, -135)
                            fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

                            # PLOT 2
                            fig = plt.figure(2)
                            ax = fig.add_subplot(projection='3d')

                            ax.scatter(scatterx, scattery, scatterz, c="blue", s=1)
                            ax.plot_trisurf(product[:,0], product[:,1], product[:,2], edgecolor=(1,0,0,0.33), linewidth=0, antialiased=True, cmap=redcmp, alpha=0.33)
                            ax.quiver(0,0,0, n[0], n[1], n[2], color="r")
                            ax.quiver(0,0,0, -n[0], -n[1], -n[2], color="r")

                            ax.set_xticks([])
                            ax.set_yticks([])
                            ax.set_zticks([])
                            #ax.set_axis_off()
                            ax.view_init(0, -135)
                            fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

                            # PLOT 3
                            fig = plt.figure(3)
                            ax = fig.add_subplot(projection='3d')

                            ax.scatter(scatterx, scattery, scatterz, c="blue", s=1)
                            ax.plot_trisurf(product[:,0], product[:,1], product[:,2], edgecolor=(1,0,0,0.33), linewidth=0, antialiased=True, cmap=redcmp, alpha=0.33)
                            for k in range(-num, num+1):
                                if not k == 0:
                                    slice_2D = np.copy(product) + (n * dist * k)
                                    ax.plot_trisurf(slice_2D[:,0], slice_2D[:,1], slice_2D[:,2], edgecolor=(0,1,0,0.33), linewidth=0, antialiased=True, cmap=greencmp, alpha=0.33)

                            ax.set_xticks([])
                            ax.set_yticks([])
                            ax.set_zticks([])
                            #ax.set_axis_off()
                            ax.view_init(0, -135)
                            fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

                            plt.tight_layout()

                            # PLOT 4
                            fig = plt.figure(4)
                            ax = fig.add_subplot(projection='3d')

                            ax.scatter(scatterx, scattery, scatterz, c="blue", s=1)
                            ax.plot_trisurf(product[:,0], product[:,1], product[:,2], edgecolor=(1,0,0,0.33), linewidth=0, antialiased=True, cmap=redcmp, alpha=0.33)
                            ax.scatter(product[:,0], product[:,1], product[:,2], c="red")
                            for k in range(-num, num+1):
                                if not k == 0:
                                    slice_2D = np.copy(product) + (n * dist * k)
                                    ax.plot_trisurf(slice_2D[:,0], slice_2D[:,1], slice_2D[:,2], edgecolor=(0,1,0,0.33), linewidth=0, antialiased=True, cmap=greencmp, alpha=0.33)
                                    ax.scatter(slice_2D[:,0], slice_2D[:,1], slice_2D[:,2], c="green")

                            ax.set_xticks([])
                            ax.set_yticks([])
                            ax.set_zticks([])
                            #ax.set_axis_off()
                            ax.view_init(0, -135)
                            fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

                            # PLOT 5
                            fig = plt.figure(5)
                            ax = fig.add_subplot(projection='3d')

                            ax.scatter(scatterx, scattery, scatterz, c="blue", s=1)
                            ax.plot_trisurf(product[:,0], product[:,1], product[:,2], edgecolor=(1,0,0,0.33), linewidth=0, antialiased=True, cmap=redcmp, alpha=0.33)
                            x_x = np.min(product[:,0])
                            y_y = np.min(product[:,1])
                            z_z = np.min(product[:,2])
                            ax.scatter([x_x], [y_y], [z_z], c="red")

                            for k in range(-num, num+1):
                                slice_2D = np.copy(product) + (n * dist * k)

                                if k == -num:
                                    x_0 = np.min(slice_2D[:,0])
                                    y_0 = np.min(slice_2D[:,1])
                                    z_0 = np.min(slice_2D[:,2])

                                if k == num:
                                    x_1 = np.min(slice_2D[:,0])
                                    y_1 = np.min(slice_2D[:,1])
                                    z_1 = np.min(slice_2D[:,2])

                                if not k == 0:
                                    ax.plot_trisurf(slice_2D[:,0], slice_2D[:,1], slice_2D[:,2], edgecolor=(0,1,0,0.33), linewidth=0, antialiased=True, cmap=greencmp, alpha=0.33)

                                    x_x = np.min(slice_2D[:,0])
                                    y_y = np.min(slice_2D[:,1])
                                    z_z = np.min(slice_2D[:,2])
                                    ax.scatter([x_x], [y_y], [z_z], c="green")

                            ax.plot3D(np.array([x_0, x_1]), np.array([y_0, y_1]), np.array([z_0, z_1]), c="purple", lw=10)

                            ax.set_xticks([])
                            ax.set_yticks([])
                            ax.set_zticks([])
                            #ax.set_axis_off()
                            ax.view_init(0, -135)
                            fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

                            # PLOT 1
                            fig = plt.figure(6)
                            ax = fig.add_subplot(projection='3d')

                            ax.scatter(scatterx, scattery, scatterz, c="blue", s=1)
                            ax.scatter(product[:,0], product[:,1], product[:,2], c="purple")
                            ax.plot_trisurf(product[:,0], product[:,1], product[:,2], edgecolor=(1,0,0,0.33), linewidth=0, antialiased=True, cmap=redcmp, alpha=0.33)

                            ax.set_xticks([])
                            ax.set_yticks([])
                            ax.set_zticks([])
                            #ax.set_axis_off()
                            ax.view_init(0, -135)
                            fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

                            plt.tight_layout()
                            plt.show()

                            ### END ###


                            # creates shifted slices, evaluates the interpolated values and weights them (here all the same weight = average)
                            interpolate = np.zeros(product.shape[0])
                            for k in range(-num, num+1):
                                slice_2D = np.copy(product) + (n * dist * k)
                                slice_2D[:,[0,1,2]] = slice_2D[:,[2,1,0]]
                                interpolate = interpolate + scipy.interpolate.interpn((data_3D_z,data_3D_y,data_3D_x), data_3D_value, slice_2D, bounds_error = False, fill_value = 0)
                            interpolate = np.round(interpolate / (2*num+1), 0).astype(int)


                            # writes back the interpolated values into the Pixel Data of the dicom
                            new_pixel_array = np.copy(read.pixel_array)
                            new_pixel_array[y,x] = interpolate

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
        if not self.dcm is None:
            # mouse move
            y = round(event.pos().x() / self.image_ratio)
            x = round(event.pos().y() / self.image_ratio)

            if x < np.shape(self.selected_data)[0] and y < np.shape(self.selected_data)[1]:
                self.lbl_image.setText(str(self.selected_num+1) + " of " + str(self.selected_max + 1) + " || ( " + str(x) + " , " + str(y) + " ) || " + str(self.selected_data[x, y]))

    def draw_image(self):
        series_num = int(self.dd_series3D.currentText()[:self.dd_series3D.currentText().find(" ")])
        indeces = np.argwhere(np.array(self.dcm.series_num).astype(int)==series_num)
        index = int(indeces[self.selected_num][0])

        self.selected_data = self.dcm.get_pixel_data(index, rescale=True)
        image = qimage2ndarray.array2qimage((255 * self.selected_data / np.max(self.selected_data)))
        pixmap = QtGui.QPixmap.fromImage(image)

        if np.shape(self.selected_data)[0] > np.shape(self.selected_data)[1]:
            pixmap = pixmap.scaledToHeight(600)
            self.image_ratio = 600 / np.shape(self.selected_data)[0]

        else:
            pixmap = pixmap.scaledToWidth(600)
            self.image_ratio = 600 / np.shape(self.selected_data)[1]

        self.lbl_image_view.setPixmap(pixmap)
        self.lbl_image.setText(str(self.selected_num+1) + " of " + str(self.selected_max + 1))
        return

if __name__ == "__main__":
    global gui_run
    app = QtWidgets.QApplication(sys.argv)
    gui_run = GUI()
    gui_run.show()
    sys.exit(app.exec_())