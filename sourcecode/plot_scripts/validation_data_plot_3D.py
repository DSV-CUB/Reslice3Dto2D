from matplotlib import pyplot as plt
import matplotlib
matplotlib.use('Qt5Agg')

import os
import pydicom
import numpy as np

from sourcecode import basic_data, basic_functions

path = r"C:\Users\CMRT\Documents\DSV\3 - Promotion\Project ReslicingTool\3 - Measurements\Validation_Data\rs3dto2d_validation_data_24.05.07.14.18.06.329133"


data = basic_data.Setup()
data.load(path)

indeces3D = np.argwhere(np.array(data.data["seriesdescription"]) == "3D_Validate").flatten()
indeces2D = np.argwhere(np.array(data.data["seriesdescription"]) != "3D_Validate").flatten()

min3D = int(indeces3D[np.argmin(np.array(data.data["instancenumber"])[indeces3D])])
max3D = int(indeces3D[np.argmax(np.array(data.data["instancenumber"])[indeces3D])])

dcm = pydicom.dcmread(data.data["filepath"][min3D])
square3D1 = basic_functions.transform_ics_to_rcs(dcm, np.array([[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]]))
dcm = pydicom.dcmread(data.data["filepath"][max3D])
square3D2 = basic_functions.transform_ics_to_rcs(dcm, np.array([[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]]))

square2D = []
for i in range(len(indeces2D)):
    dcm = pydicom.dcmread(data.data["filepath"][indeces2D[i]])
    square2D.append(basic_functions.transform_ics_to_rcs(dcm, np.array([[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]])))


ax = plt.figure(figsize=(10,10)).add_subplot(projection='3d')

ax.plot3D(square3D1[:,0], square3D1[:,1], square3D1[:,2], c="#0000ff", lw=5, zorder=100, solid_capstyle='round') # frame low
ax.plot3D(square3D2[:,0], square3D2[:,1], square3D2[:,2], c="#0000ff", lw=5, zorder=100, solid_capstyle='round') # frame high
ax.plot3D([square3D1[0,0], square3D2[0,0]], [square3D1[0,1], square3D2[0,1]], [square3D1[0,2], square3D2[0,2]], c="#0000ff", lw=5, zorder=100, solid_capstyle='round') # frame high
ax.plot3D([square3D1[1,0], square3D2[1,0]], [square3D1[1,1], square3D2[1,1]], [square3D1[1,2], square3D2[1,2]], c="#0000ff", lw=5, zorder=100, solid_capstyle='round') # frame high
ax.plot3D([square3D1[2,0], square3D2[2,0]], [square3D1[2,1], square3D2[2,1]], [square3D1[2,2], square3D2[2,2]], c="#0000ff", lw=5, zorder=100, solid_capstyle='round') # frame high
ax.plot3D([square3D1[3,0], square3D2[3,0]], [square3D1[3,1], square3D2[3,1]], [square3D1[3,2], square3D2[3,2]], c="#0000ff", lw=5, zorder=100, solid_capstyle='round') # frame high

for i in range(len(indeces2D)):
    ax.plot3D(square2D[i][:,0], square2D[i][:,1], square2D[i][:,2], c="#ff0000", lw=5, zorder=100, solid_capstyle='round') # frame low


plt.show()

a=0