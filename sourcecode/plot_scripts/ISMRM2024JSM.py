import pydicom
from matplotlib import pyplot as plt
import os
import numpy as np
from skimage.transform import rescale, resize
from sourcecode.plot_scripts import basic_functions_inlineplot

path_dcms = r"C:\Users\CMRT\Desktop\ISMRM Vortrag JSM\DICOMs"
path_out = r"C:\Users\CMRT\Desktop\ISMRM Vortrag JSM\Bilder"

def array_resize(array, new_size, **kwargs):
    anti_aliasing = kwargs.get("anti_aliasing", True)
    normalize = kwargs.get("normalize", False)

    shape = np.shape(array)
    if len(shape) > 2:
        new_array = np.reshape(array, (shape[0], shape[1], -1))
    else:
        new_array = np.expand_dims(array, axis=2)

    result=[]
    for j in range(np.shape(new_array)[-1]):
        resultj = eval(("resize" if isinstance(new_size, (list, tuple, np.ndarray)) else "rescale") + "(new_array[:,:,j].squeeze(), new_size, anti_aliasing=anti_aliasing)")
        resultjmax = np.amax(resultj, (0, 1))

        if not normalize or np.abs(resultjmax) == 0:
            result.append(resultj)
        else:
            result.append(resultj / resultjmax)

    result = np.moveaxis(np.array(result), 0, -1)

    if len(shape) == 2:
        result = result.squeeze()

    return result


# PLOT 2D data:
if True:
    data2d = []
    for root, _, files in os.walk(path_dcms):
        if "MOLLI" in root:
            for file in files:
                data2d.append(pydicom.dcmread(os.path.join(root, file)))
                pa = basic_functions_inlineplot.get_pixel_data(os.path.join(root, file), rescale=True, representation=True)

                if np.shape(pa)[0] > np.shape(pa)[1]:
                    delta = int((np.shape(pa)[0] - np.shape(pa)[1]) / 2)
                    pa = pa[delta:delta+np.shape(pa)[1], :]
                else:
                    delta = int((np.shape(pa)[1] - np.shape(pa)[0]) / 2)
                    pa = pa[:, delta:delta+np.shape(pa)[0]]

                pa = array_resize(pa, np.array(np.shape(pa))*10)

                fig, ax = plt.subplots(1,1,figsize=(10,10), frameon=False)
                ax.imshow(pa, cmap="gray")
                ax.plot([0, 0, np.shape(pa)[0]-1, np.shape(pa)[0]-1, 0], [0, np.shape(pa)[0]-1, np.shape(pa)[0]-1, 0, 0], c="red", lw=10)

                ax.axis("off")
                ax.spines[['right', 'top', 'left', 'bottom']].set_visible(False)
                #plt.tight_layout()
                plt.savefig(os.path.join(path_out, file.replace(".dcm", ".png")), dpi=300,  bbox_inches='tight')

# PLOT 3D
if True:
    data3d = {}
    data3d["pa"] = []
    data3d["instance"] = []
    data3d["dcms"] = []
    for root, _, files in os.walk(path_dcms):
        if not "MOLLI" in root:
            for file in files:
                dcm = pydicom.dcmread(os.path.join(root, file))
                pa = basic_functions_inlineplot.get_pixel_data(os.path.join(root, file), rescale=True, representation=True)

                data3d["pa"].append(pa)
                data3d["instance"].append(int(dcm[0x0020, 0x0013].value))
                data3d["dcms"].append(dcm)

    if True:
        ax = plt.figure(figsize=(10,10)).add_subplot(projection='3d')
        ax.axis("off")
        ax.spines[['right', 'top', 'left', 'bottom']].set_visible(False)

        for i in range(65, 75, 1): #range(int(len(data3d["instance"]) / 2)):
            index = int(np.argwhere(np.array(data3d["instance"]) == int(i+1)).flatten())

            pa = data3d["pa"][index]
            if np.shape(pa)[0] > np.shape(pa)[1]:
                delta = int((np.shape(pa)[0] - np.shape(pa)[1]) / 2)
                pa = pa[delta:delta+np.shape(pa)[1], :]
            else:
                delta = int((np.shape(pa)[1] - np.shape(pa)[0]) / 2)
                pa = pa[:, delta:delta+np.shape(pa)[0]]

            #pa = array_resize(pa, np.array(np.shape(pa))*10)

            X, Y = np.meshgrid(np.linspace(0,1,np.shape(pa)[0]), np.linspace(0,1,np.shape(pa)[0]))
            Z = int(i) * np.ones(np.shape(X))
            ax.plot_surface(X, Y, Z, rstride=1, cstride=1, facecolors=plt.cm.gray(pa), shade=False)
            #ax.imshow(pa, cmap="gray")

        x1, x2 = (np.min(X), np.max(X))
        y1, y2 = (np.min(Y), np.max(Y))
        z1, z2 = (65, 74)

        ax.plot3D([x1, x2, x2], [y1, y1, y2], [z1, z1, z1], c="#0000ff", lw=10, zorder=100, solid_capstyle='round') # frame low
        ax.plot3D([x1, x1, x2, x2, x1], [y1, y2, y2, y1, y1], [z2, z2, z2, z2, z2], c="#0000ff", lw=10, zorder=100, solid_capstyle='round') # frame high
        ax.plot3D([x1, x1], [y1, y1], [z1, z2], c="#0000ff", lw=10, zorder=100, solid_capstyle='round') # line
        #ax.plot3D([x1, x1], [y2, y2], [z1, z2], c="blue", lw=10, zorder=100, solid_capstyle='round') # line
        ax.plot3D([x2, x2], [y1, y1], [z1, z2], c="#0000ff", lw=10, zorder=100, solid_capstyle='round') # line
        ax.plot3D([x2, x2], [y2, y2], [z1, z2], c="#0000ff", lw=10, zorder=100, solid_capstyle='round') # line

        ax.xaxis.pane.fill = False # Left pane
        ax.yaxis.pane.fill = False # Right pane
        ax.zaxis.pane.fill = False # Right pane
        ax.grid(False)
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.set_zticklabels([])
        ax.w_xaxis.line.set_color((1.0, 1.0, 1.0, 0.0))
        ax.w_yaxis.line.set_color((1.0, 1.0, 1.0, 0.0))
        ax.w_zaxis.line.set_color((1.0, 1.0, 1.0, 0.0))
        ax.w_xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
        ax.w_yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_zticks([])
        plt.tight_layout()
        #plt.show()
        plt.savefig(os.path.join(path_out, "3D_stack.png"), dpi=300,  bbox_inches='tight', pad_inches=0.05, transparent=True)


    for i in range(len(data2d)):
        basic_functions_inlineplot.reslice(data3d["dcms"], data2d[i], 0.00, "rectangle")