import pydicom
import numpy as np
import os
import copy
from argparse import ArgumentParser
from datetime import datetime

def create_dataset(example_dicom, path_out):
    stack_num = 11
    series_num = 0
    timestamp = datetime.now().strftime("%y.%m.%d.%H.%M.%S.%f")
    path_out_dir = os.path.join(path_out, "rs3dto2d_visualdata_" + timestamp)

    # 3D Dataset
    series_num = series_num + 1
    os.makedirs(os.path.join(path_out_dir, "3D_Dataset"), exist_ok=True)
    for i in range(stack_num):
        distance = (i - int((stack_num-1) / 2))
        array = np.ones((11, 11))

        array = array * (1000 * round((1-abs(distance/int((stack_num-1) / 2))),3))


        dcm = copy.copy(example_dicom)
        dcm.PixelData = array.astype("int16").tobytes()
        dcm[0x0018, 0x0050].value = str(1) # slice thickness
        dcm[0x0028, 0x0030].value = [1, 1] # pixel spacing
        dcm[0x0018, 0x0088].value = str(1) # spacing between slices

        dcm[0x0020, 0x1041].value = str(distance) # slice location
        dcm[0x0020, 0x0032].value = [-5, -5, distance] # Patient position
        dcm[0x0020, 0x0037].value = [1, 0, 0, 0, 1, 0] # Image Orientation
        dcm[0x0018, 0x1310].value = [0, 11, 11, 0] # Acquisition matrix
        dcm[0x0028, 0x0010].value = 11 # Rows
        dcm[0x0028, 0x0011].value = 11 # Cols

        dcm[0x0020, 0x0011].value = int(series_num) # series number
        dcm[0x0008, 0x103E].value = "3D_Test" # Series Description
        dcm[0x0008, 0x1030].value = "Reslice3Dto2DTest" # Study description
        dcm[0x0018, 0x1030].value = "Reslice3Dto2DTest" # Protocol Name
        dcm[0x0018, 0x0023].value = "3D" # MR Acquisition Type
        dcm[0x0020, 0x0013].value = int(i+1) # Instance Number

        dcm.file_meta[0x0002, 0x0003].value = timestamp + "." + str(series_num) + "." + str(i) # Media Storage SOP Instance UID
        dcm[0x0008, 0x0018].value = timestamp + "." + str(series_num) + "." + str(i) # SOP Instance UID
        dcm[0x0020, 0x000e].value = timestamp + "." + str(series_num) # Series Instance UID
        dcm[0x0010, 0x0010].value = "Validation Dataset" # patient name
        dcm[0x0010, 0x0040].value = "D" # gender
        dcm[0x0010, 0x1010].value = "021Y" # age
        dcm[0x0010, 0x1020].value = "1.00" # height
        dcm[0x0010, 0x1030].value = "25" # weight

        if [0x0028, 0x1050] in dcm: # window center
            del dcm[0x0028, 0x1050]
        if [0x0028, 0x1051] in dcm: # window width
            del dcm[0x0028, 0x1051]

        dcm.save_as(os.path.join(path_out_dir, "3D_Dataset", str(i) + ".dcm"))

    # 2D in plane iso-center
    series_num = series_num + 1
    os.makedirs(os.path.join(path_out_dir, "2D_inplane_iso"), exist_ok=True)

    array = np.random.randint(0, 1000, (11, 11))

    dcm = copy.copy(example_dicom)
    dcm.PixelData = array.astype("int16").tobytes()
    dcm[0x0018, 0x0050].value = str(2) # slice thickness
    dcm[0x0028, 0x0030].value = [1, 1] # pixel spacing
    dcm[0x0018, 0x0088].value = str(1) # spacing between slices

    dcm[0x0020, 0x1041].value = str(0) # slice location
    dcm[0x0020, 0x0032].value = [-5, -5, 0] # Patient position
    dcm[0x0020, 0x0037].value = [1, 0, 0, 0, 1, 0] # Image Orientation
    dcm[0x0018, 0x1310].value = [0, 11, 11, 0] # Acquisition matrix
    dcm[0x0028, 0x0010].value = 11 # Rows
    dcm[0x0028, 0x0011].value = 11 # Cols

    dcm[0x0020, 0x0011].value = int(series_num) # series number
    dcm[0x0008, 0x103E].value = "2D_inplane_Test" # Series Description
    dcm[0x0008, 0x1030].value = "Reslice3Dto2DTest" # Study description
    dcm[0x0018, 0x1030].value = "Reslice3Dto2DTest" # Protocol Name
    dcm[0x0018, 0x0023].value = "2D" # MR Acquisition Type
    dcm[0x0020, 0x0013].value = int(1) # Instance Number

    dcm.file_meta[0x0002, 0x0003].value = timestamp + "." + str(series_num) + "." + str(1) # Media Storage SOP Instance UID
    dcm[0x0008, 0x0018].value = timestamp + "." + str(series_num) + "." + str(1) # SOP Instance UID
    dcm[0x0020, 0x000e].value = timestamp + "." + str(series_num) # Series Instance UID
    dcm[0x0010, 0x0010].value = "Validation Dataset" # patient name
    dcm[0x0010, 0x0040].value = "D" # gender
    dcm[0x0010, 0x1010].value = "021Y" # age
    dcm[0x0010, 0x1020].value = "1.00" # height
    dcm[0x0010, 0x1030].value = "25" # weight

    if [0x0028, 0x1050] in dcm: # window center
        del dcm[0x0028, 0x1050]
    if [0x0028, 0x1051] in dcm: # window width
        del dcm[0x0028, 0x1051]

    dcm.save_as(os.path.join(path_out_dir, "2D_inplane_iso", "1.dcm"))

    # 2D perpendicular plane
    series_num = series_num + 1
    os.makedirs(os.path.join(path_out_dir, "2D_perplane"), exist_ok=True)

    array = np.random.randint(0, 1000, (11, 11))

    dcm = copy.copy(example_dicom)
    dcm.PixelData = array.astype("int16").tobytes()
    dcm[0x0018, 0x0050].value = str(2) # slice thickness
    dcm[0x0028, 0x0030].value = [1, 1] # pixel spacing
    dcm[0x0018, 0x0088].value = str(1) # spacing between slices

    dcm[0x0020, 0x1041].value = str(0) # slice location
    dcm[0x0020, 0x0032].value = [0, -5, -5] # Patient position
    dcm[0x0020, 0x0037].value = [0, 1, 0, 0, 0, 1] # Image Orientation
    dcm[0x0018, 0x1310].value = [0, 11, 11, 0] # Acquisition matrix
    dcm[0x0028, 0x0010].value = 11 # Rows
    dcm[0x0028, 0x0011].value = 11 # Cols

    dcm[0x0020, 0x0011].value = int(series_num) # series number
    dcm[0x0008, 0x103E].value = "2D_perplane_Test" # Series Description
    dcm[0x0008, 0x1030].value = "Reslice3Dto2DTest" # Study description
    dcm[0x0018, 0x1030].value = "Reslice3Dto2DTest" # Protocol Name
    dcm[0x0018, 0x0023].value = "2D" # MR Acquisition Type
    dcm[0x0020, 0x0013].value = int(1) # Instance Number

    dcm.file_meta[0x0002, 0x0003].value = timestamp + "." + str(series_num) + "." + str(1) # Media Storage SOP Instance UID
    dcm[0x0008, 0x0018].value = timestamp + "." + str(series_num) + "." + str(1) # SOP Instance UID
    dcm[0x0020, 0x000e].value = timestamp + "." + str(series_num) # Series Instance UID
    dcm[0x0010, 0x0010].value = "Validation Dataset" # patient name
    dcm[0x0010, 0x0040].value = "D" # gender
    dcm[0x0010, 0x1010].value = "021Y" # age
    dcm[0x0010, 0x1020].value = "1.00" # height
    dcm[0x0010, 0x1030].value = "25" # weight

    if [0x0028, 0x1050] in dcm: # window center
        del dcm[0x0028, 0x1050]
    if [0x0028, 0x1051] in dcm: # window width
        del dcm[0x0028, 0x1051]

    dcm.save_as(os.path.join(path_out_dir, "2D_perplane", "1.dcm"))

    # 2D diagonal plane
    series_num = series_num + 1
    os.makedirs(os.path.join(path_out_dir, "2D_diagplane"), exist_ok=True)

    array = np.random.randint(0, 1000, (10, 11))

    dcm = copy.copy(example_dicom)
    dcm.PixelData = array.astype("int16").tobytes()
    dcm[0x0018, 0x0050].value = str(2.73) # slice thickness
    dcm[0x0028, 0x0030].value = [1.1, 1.1] # pixel spacing
    dcm[0x0018, 0x0088].value = str(1) # spacing between slices

    dcm[0x0020, 0x1041].value = str(0) # slice location
    dcm[0x0020, 0x0032].value = [-5, -5, -5] # Patient position
    dcm[0x0020, 0x0037].value = [0, 1, 0, 1/1.1, 0, 1/1.1] # Image Orientation
    dcm[0x0018, 0x1310].value = [0, 10, 11, 0] # Acquisition matrix
    dcm[0x0028, 0x0010].value = 11 # Rows
    dcm[0x0028, 0x0011].value = 10 # Cols

    dcm[0x0020, 0x0011].value = int(series_num) # series number
    dcm[0x0008, 0x103E].value = "2D_diagplane_Test" # Series Description
    dcm[0x0008, 0x1030].value = "Reslice3Dto2DTest" # Study description
    dcm[0x0018, 0x1030].value = "Reslice3Dto2DTest" # Protocol Name
    dcm[0x0018, 0x0023].value = "2D" # MR Acquisition Type
    dcm[0x0020, 0x0013].value = int(1) # Instance Number

    dcm.file_meta[0x0002, 0x0003].value = timestamp + "." + str(series_num) + "." + str(1) # Media Storage SOP Instance UID
    dcm[0x0008, 0x0018].value = timestamp + "." + str(series_num) + "." + str(1) # SOP Instance UID
    dcm[0x0020, 0x000e].value = timestamp + "." + str(series_num) # Series Instance UID
    dcm[0x0010, 0x0010].value = "Validation Dataset" # patient name
    dcm[0x0010, 0x0040].value = "D" # gender
    dcm[0x0010, 0x1010].value = "021Y" # age
    dcm[0x0010, 0x1020].value = "1.00" # height
    dcm[0x0010, 0x1030].value = "25" # weight

    if [0x0028, 0x1050] in dcm: # window center
        del dcm[0x0028, 0x1050]
    if [0x0028, 0x1051] in dcm: # window width
        del dcm[0x0028, 0x1051]

    dcm.save_as(os.path.join(path_out_dir, "2D_diagplane", "1.dcm"))


    return

if __name__ == "__main__":
    parser = ArgumentParser(description="Script")
    parser.add_argument("-d", "--data", dest="path_dicom", help="dicom file or dir with dicom files", default=None, required=False, type=str)
    parser.add_argument("-p", "--path", dest="path_out", help="output path", default=None, required=False, type=str)
    args = vars(parser.parse_args())

    path_dicom = args["path_dicom"]
    path_out = args["path_out"]

    path_dicom = r"D:\ECRC_AG_CMR\3 - Promotion\Project ReslicingTool\3 - Measurements\Reslice Johanna\MyoMet-CMR-014\series0001-Body"
    path_out = r"C:\Users\Omen\Desktop"

    if not path_dicom is None:
        try:
            dcm = pydicom.dcmread(path_dicom)
            dcm.PatientName
        except:
            for root, _, files in os.walk(path_dicom):

                for file in files:
                    try:
                        dcm = pydicom.dcmread(os.path.join(root, file))
                        dcm.PatientName
                        break
                    except:
                        dcm = None

                if not dcm is None:
                    break
    else:
        dcm = None

    if dcm is None:
        raise RuntimeError("There could not be a dicom loaded from the given dicom data path. Please specify a valid dicom data path with -d-")

    if path_out is None:
        raise RuntimeError("No output path was given, please specify an output path with -p")

    create_dataset(dcm, path_out)