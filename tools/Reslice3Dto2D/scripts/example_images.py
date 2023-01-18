import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib import pyplot as plt
import numpy as np
import os
import pydicom

#path = r"D:\ECRC_AG_CMR\3 - Promotion\Project ReslicingTool\6 - Analysis\Reslice\3DCS_LV_001_055Y(1)"
path = r"C:\Users\CMRT\Documents\DSV\3 - Promotion\Project ReslicingTool\6 - Analysis\Testdata_New"
size = 140

list_pixel_array = []
for root, _, files in os.walk(path):
    for file in files:
        try:
            dcm = pydicom.dcmread(os.path.join(root, file))
            pa = dcm.pixel_array
            dx = int((np.shape(pa)[0]-size)/2)
            dy = int((np.shape(pa)[1]-size)/2)
            pa = pa[dx:dx+size, dy:dy+size]

            fig = plt.figure(1, figsize=[16, 9], dpi=250)
            plt.imshow(pa, cmap="gray")
            plt.axis('off')
            plt.tight_layout()
            plt.savefig(os.path.join(root, file) +".jpg", bbox_inches="tight", pad_inches = 0)
            plt.clf()
        except:
            pass