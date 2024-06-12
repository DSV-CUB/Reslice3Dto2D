import os
import numpy as np
import copy
import pydicom
from pydicom.uid import generate_uid
import scipy.interpolate
from scipy.stats import norm


def save_dcm(dcm, path, overwrite=False):
    '''
    saves a DICOM file from a pydicom DICOM object
    :param dcm: pydicom DICOM object
    :param path: path to export to
    :param overwrite: overwrite if file already exists
    :return: export direcrory
    '''
    name = ''.join(e for e in str(dcm[0x0010, 0x0010].value) if e.isalnum())
    seriesnumber = str(dcm[0x0020, 0x0011].value).zfill(4)
    serieddescription = ''.join(e for e in str(dcm[0x0008, 0x103E].value) if e.isalnum())
    uid = str(dcm[0x0008, 0x0018].value)

    dir_path = os.path.join(path, "R3D2Dexport", name, seriesnumber + "_" + serieddescription)
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, uid + ".dcm")
    if not overwrite and os.path.isfile(file_path):
        pass
    else:
        dcm.save_as(file_path)
    return dir_path


def save_stacked_dcm(basic_data, seriesnumber, path):
    '''
    exports stacked data as a new 3D dataset
    :param basic_data: a basic_data.Setup object
    :param seriesnumber: the seriesnumber reflecting the stack
    :param path: export path
    :return:
    '''
    indeces = np.argwhere(np.array(basic_data.data["seriesnumber"]) == seriesnumber).flatten()
    for i in range(len(indeces)):
        dcm = pydicom.dcmread(basic_data.data["filepath"][indeces[i]], force=True)
        dcm[0x0020, 0x0011].value = int(seriesnumber) # series number
        dcm[0x0008, 0x103e].value = basic_data.data["seriesdescription"][indeces[i]] # series description
        dcm[0x0020, 0x0013].value = int(basic_data.data["instancenumber"][indeces[i]]) # instance number
        dcm[0x0018, 0x0023].value = basic_data.data["acquisitiontype"][indeces[i]] # acquisitiontype
        dcm[0x0020, 0x000e].value = generate_uid(entropy_srcs=[str(seriesnumber), basic_data.data["seriesdescription"][indeces[i]]]) # series instance UID
        dcm[0x0008, 0x0018].value = generate_uid(entropy_srcs=[str(seriesnumber), basic_data.data["seriesdescription"][indeces[i]], str(basic_data.data["instancenumber"][indeces[i]])]) # SOP instance UID
        dcm.file_meta[0x0002, 0x0003].value = generate_uid(entropy_srcs=[str(seriesnumber), basic_data.data["seriesdescription"][indeces[i]], str(basic_data.data["instancenumber"][indeces[i]])]) # Media Storage SOP Instance UID
        save_dcm(dcm, path, True)
    return


def get_pixel_data(dcmpath, **kwargs):
    '''
    function to get pixel data as numpy array with formatting according to rescale or representation setting
    :param dcmpath: path to DICOM file
    :param kwargs: options to adapt raw pixel data
        rescale - converts integer pixel values into quantitative float values
        representation - windows the pixel data to increae contrast in the relevant value range
    :return:
    '''
    try:
        dcm = pydicom.dcmread(dcmpath, force=True)
    except:
        return []

    options_representation = kwargs.get("representation", False)
    options_rescale = kwargs.get("rescale", True)

    pixel_data = copy.deepcopy(dcm.pixel_array)

    if options_rescale or options_representation:
        try:
            n = dcm[0x0028, 0x1052].value
        except:
            n = None

        try:
            m = dcm[0x0028, 0x1053].value
        except:
            m = None

        if not m is None:
            pixel_data = pixel_data * float(m)

        if not n is None:
            pixel_data = pixel_data + float(n)

    if options_representation:
        try:
            c = float(dcm[0x0028, 0x1050].value) # window center
        except:
            c = None
        try:
            w = float(dcm[0x0028, 0x1051].value) # window width
        except:
            w = None

        if not c is None and not w is None:
            pixel_min = c - w//2
            pixel_max = c + w//2
            pixel_data[pixel_data<pixel_min] = pixel_min
            pixel_data[pixel_data>pixel_max] = pixel_max
            pixel_data[pixel_data<0]=0

    return pixel_data


def transform_ics_to_rcs(dcm, indeces):
    '''
    ics = image coordinate system (tupel of x-, y-values in units of pixel in dicom pixel data x = column, y = row)
    rcs = reference coordinate system (standard to store points in dicom tags)
    Function to do forward (ics -> rcs) or backward (rcs -> ics) transformation in dependence of arr_points
    :param dcm: object - pydicom object
    :param indeces:  array - nx2 array with x and y values (units of pixels) of the points in the dicom image plane for conversion points to (x = column, y = row)
    :return: list of lists - nx3 with points in rcs
    '''
    # conversion as described in https://dicom.innolitics.com/ciods/rt-dose/roi-contour/30060039/30060040/30060050
    result = []
    matrix = np.zeros((3, 3))

    # read in relevant dicom tags
    image_position = np.asarray(dcm[0x0020, 0x0032].value, np.double)
    direction_cosine = np.asarray(dcm[0x0020, 0x0037].value, np.double)
    pixel_spacing = np.asarray(dcm[0x0028, 0x0030].value, np.double)

    # create the matrix
    matrix[0, 0] = direction_cosine[0]
    matrix[1, 0] = direction_cosine[1]
    matrix[2, 0] = direction_cosine[2]

    matrix[0, 1] = direction_cosine[3]
    matrix[1, 1] = direction_cosine[4]
    matrix[2, 1] = direction_cosine[5]

    matrix[0:3, 2] = np.cross(direction_cosine[0:3], direction_cosine[3:]) / np.linalg.norm(np.cross(direction_cosine[0:3], direction_cosine[3:]))

    # P = Mx+S
    # the vector x consists of tuples (x, y) where x =Columns and y= Rows
    # due to cubicspline x and y can have floating numbers
    vector = np.zeros((indeces.shape[0], 3))
    vector[:, 0] = indeces[:, 0] * pixel_spacing[0]
    vector[:, 1] = indeces[:, 1] * pixel_spacing[1]

    product = np.transpose(np.dot(matrix, np.transpose(vector)))  # x y z 1
    product = np.add(product[:, 0:3], image_position.reshape((1, 3)))
    return product


def save_reslice(basic_data, series3D, series2D, profile, thickness, path, sn=0):
    '''
    apply reslice
    :param basic_data: a basic_data.Setup object
    :param series3D: 3D seriesnumber
    :param series2D: 2D seriesnumber
    :param profile: slice profile as string
    :param thickness: slice thickness as float or "as 2D" or "as 3D"
    :param path: export path
    :param seriesnumber: minimum series number to give
    :return:
    '''
    indeces3D = np.argwhere(np.array(basic_data.data["seriesnumber"]) == series3D).flatten()
    indeces2D = np.argwhere(np.array(basic_data.data["seriesnumber"]) == series2D).flatten()

    if str(thickness) == "as 2D":
        ST = basic_data.data["slicethickness"][indeces2D[0]]
    elif str(thickness) == "as 3D":
        ST = basic_data.data["slicethickness"][indeces3D[0]]
    else:
        ST = float(thickness.replace(" mm", ""))

    # evaluate 2D slices to evaluate at
    positions2D = np.unique(np.array(basic_data.data["imageposition"])[indeces2D], axis=0)
    indexlist2D = []
    for p in range(len(positions2D)):
        iindeces = np.where((np.array(basic_data.data["imageposition"])[indeces2D] == positions2D[p]).all(axis=1))[0]
        indexlist2D.append(indeces2D[iindeces][0])

    # evaluate 3D volumes (if 4D data or 3D cine is given, then cut into 3D blocks for each timepoint)
    positions3D = np.unique(np.array(basic_data.data["imageposition"])[indeces3D], axis=0)
    timepoints = len(np.where((np.array(basic_data.data["imageposition"])[indeces3D] == positions3D[0]).all(axis=1))[0])

    indexmatrix3D = np.zeros((timepoints, len(positions3D)))
    for p in range(len(positions3D)):
        iindeces = np.where((np.array(basic_data.data["imageposition"])[indeces3D] == positions3D[p]).all(axis=1))[0]
        sortindeces = np.argsort(np.array(basic_data.data["triggertime"])[indeces3D[iindeces]])
        sortindeces = indeces3D[iindeces][sortindeces]
        indexmatrix3D[:, p] = sortindeces
    indexmatrix3D = indexmatrix3D.astype(int)

    # run reslice
    dcms2D = []
    for i in range(len(indexlist2D)):
        dcms2D.append(pydicom.dcmread(basic_data.data["filepath"][indexlist2D[i]]))

    instancenum = 1
    sn = np.max((np.max(basic_data.data["seriesnumber"])+1, 20000, sn))
    for i in range(len(indexmatrix3D)):
        dcms3D =[]
        for j in range(len(indexmatrix3D[i])):
            dcms3D.append(pydicom.dcmread(basic_data.data["filepath"][indexmatrix3D[i,j]]))

        for j in range(len(dcms2D)):
            rpa = reslice(dcms3D, dcms2D[j], ST, profile)
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
            dcm[0x0008, 0x103e].value = "R3D2D_" + dcms3D[0][0x0008, 0x103e].value + "_" + dcm[0x0008, 0x103e].value + "_" + str(ST) + "mm_" + profile # series description
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
            save_dcm(dcm, path, True)
            instancenum = instancenum + 1
    return sn


def sort3Dstack(dcms3D):
    '''
    sorts parallel slices in ascending order among all three dimensions
    :param dcms3D:
    :return: indeces of sorting
    '''
    cornerpoints = []
    for i in range(len(dcms3D)):
        cornerpoints.append(transform_ics_to_rcs(dcms3D[i], np.array([[0,0]])))
    return np.lexsort(np.transpose(np.array(cornerpoints).squeeze()))


def reslice(dcms3D, dcm2D, reslice_thickness, reslice_profile):
    '''
    reslice funcation
    :param dcms3D: list of pydicom DICOM objects reflecting the 3D data
    :param dcm2D: a single pydicom DICOM object reflecting the 2D slice
    :param reslice_thickness: slice thickness as float or "as 2D" or "as 3D"
    :param reslice_profile: slice profile as string
    :return: pixel array of reslice
    '''
    sorted3D = sort3Dstack(dcms3D)

    # create trans function to transform rcs to new coordinate system
    p000 = transform_ics_to_rcs(dcms3D[sorted3D[0]], np.array([[0,0]])).flatten()
    p100 = transform_ics_to_rcs(dcms3D[sorted3D[0]], np.array([[1,0]])).flatten()
    p010 = transform_ics_to_rcs(dcms3D[sorted3D[0]], np.array([[0,1]])).flatten()
    p001 = transform_ics_to_rcs(dcms3D[sorted3D[1]], np.array([[0,0]])).flatten()
    exn = (p100-p000) / np.linalg.norm((p100-p000))
    eyn = (p010-p000) / np.linalg.norm((p010-p000))
    ezn = (p001-p000) / np.linalg.norm((p001-p000))
    R = np.array([exn, eyn, ezn])
    trans = lambda point: np.matmul(R, (point-p000))
    ###

    # create 3D regular grid data
    data_3D_x = np.round(np.arange(0, dcms3D[0].pixel_array.shape[1], 1) * dcms3D[0].PixelSpacing[1], 3)
    data_3D_y = np.round(np.arange(0, dcms3D[0].pixel_array.shape[0], 1) * dcms3D[0].PixelSpacing[0], 3)
    data_3D_z = np.zeros((len(sorted3D),))
    data_3D_values = np.zeros((dcms3D[0].pixel_array.shape[1], dcms3D[0].pixel_array.shape[0], len(sorted3D)))
    for i in range(len(sorted3D)):
        data_3D_z[i] = trans(transform_ics_to_rcs(dcms3D[sorted3D[i]], np.array([[0,0]])).flatten())[-1]
        data_3D_values[:,:,i] = np.transpose(dcms3D[sorted3D[i]].pixel_array)
    data3DST = np.min(np.abs(data_3D_z-np.roll(data_3D_z,1)))
    data_3D_z = np.round(data_3D_z, 3)
    ###

    # create 2D planes in regular grid coordinates
    x = np.arange(0, dcm2D.pixel_array.shape[1], 1) #
    y = np.arange(0, dcm2D.pixel_array.shape[0], 1) #
    X, Y = np.meshgrid(x,y)
    x = np.reshape(X, (-1,1))
    y = np.reshape(Y, (-1,1))
    plane2Dpoints = transform_ics_to_rcs(dcm2D, np.hstack((x,y)))

    # evaluate the orthogonal normal of the slice
    v1 = plane2Dpoints[1, :] - plane2Dpoints[0, :]
    v2 = plane2Dpoints[dcm2D.pixel_array.shape[0], :] - plane2Dpoints[0, :]
    n = np.cross(v1, v2)
    n = n / np.linalg.norm(n)

    # number of points above and under the evaluation point along the normal
    num = int(round(np.round(reslice_thickness, 2) / np.round((2*data3DST), 2)))
    # distance of the points (close to 3D resolution)
    if num > 0:
        dist = reslice_thickness / (2*num)
    else:
        dist = 0

    # creates shifted slices, evaluates the interpolated values and weights them (here all the same weight = average)
    weights = []
    interpolate = np.zeros(plane2Dpoints.shape[0])

    for k in range(-num, num+1):
        if k == 0:
            weights.append(1)
        elif reslice_profile == "rectangular":
            weights.append(1)
        elif reslice_profile == "triangular":
            weights.append((num-abs(k))/num)
        elif reslice_profile == "cosine + 1":
            weights.append((np.cos((k/num) * np.pi) + 1) / 2)
        elif reslice_profile == "sinc":
            weights.append(np.sinc(k/num))
        elif reslice_profile == "standard normal 2":
            weights.append(norm.pdf(2 * (k/num), loc=0, scale=1) / norm.pdf(0, loc=0, scale=1))
        elif reslice_profile == "standard normal 5":
            weights.append(norm.pdf(5 * (k/num), loc=0, scale=1) / norm.pdf(0, loc=0, scale=1))
        else:
            raise ValueError("Reslice profile unknown.")

        slice_2D = np.copy(plane2Dpoints) + (n * dist * k)
        slice_2D = np.array([trans(slice_2D[x]) for x in range(np.shape(slice_2D)[0])])
        slice_2D[:,[0,1,2]] = slice_2D[:,[2,1,0]]
        slice_2D = np.round(slice_2D, 3)

        interpolate = interpolate + weights[-1] * scipy.interpolate.interpn((data_3D_z,data_3D_y,data_3D_x), np.swapaxes(data_3D_values, 0, 2), slice_2D, bounds_error=False, fill_value=0)

    interpolate = np.round(interpolate / np.sum(weights), 0).astype(int)
    new_pixel_array = np.zeros(np.shape(dcm2D.pixel_array))
    new_pixel_array[y,x] = interpolate.reshape((-1,1))

    # save 2D reslice
    from matplotlib import pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    pa = np.copy(new_pixel_array)
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
    plt.savefig(os.path.join(r"C:\Users\CMRT\Desktop\ISMRM Vortrag JSM\Bilder", str(dcm2D[0x0008, 0x103e].value) + ".png"), dpi=300,  bbox_inches='tight')

    # save slice in box
    planeedges = np.array([[0, 0], [0, dcm2D.pixel_array.shape[0]-1], [dcm2D.pixel_array.shape[1]-1, dcm2D.pixel_array.shape[0]-1], [dcm2D.pixel_array.shape[1]-1, 0]])
    planeedges = np.array([trans(transform_ics_to_rcs(dcm2D, planeedges)[x]) for x in range(np.shape(planeedges)[0])])

    ax = plt.figure(figsize=(10,10)).add_subplot(projection='3d')
    ax.axis("off")
    ax.spines[['right', 'top', 'left', 'bottom']].set_visible(False)

    x1, x2 = (np.min(data_3D_x), np.max(data_3D_x))
    y1, y2 = (np.min(data_3D_y), np.max(data_3D_y))
    z1, z2 = (np.min(data_3D_z), np.max(data_3D_z))

    ax.plot3D([x1, x1, x2, x2, x1], [y1, y2, y2, y1, y1], [z1, z1, z1, z1, z1], c="blue", lw=10, zorder=100, solid_capstyle='round') # frame low
    ax.plot3D([x1, x1, x2, x2, x1], [y1, y2, y2, y1, y1], [z2, z2, z2, z2, z2], c="blue", lw=10, zorder=100, solid_capstyle='round') # frame high
    ax.plot3D([x1, x1], [y1, y1], [z1, z2], c="blue", lw=10, zorder=100, solid_capstyle='round') # line
    ax.plot3D([x1, x1], [y2, y2], [z1, z2], c="blue", lw=10, zorder=100, solid_capstyle='round') # line
    ax.plot3D([x2, x2], [y1, y1], [z1, z2], c="blue", lw=10, zorder=100, solid_capstyle='round') # line
    ax.plot3D([x2, x2], [y2, y2], [z1, z2], c="blue", lw=10, zorder=100, solid_capstyle='round') # line

    ax.plot3D([planeedges[0, 0], planeedges[1, 0], planeedges[2, 0], planeedges[3, 0], planeedges[0, 0]], [planeedges[0, 1], planeedges[1, 1], planeedges[2, 1], planeedges[3, 1], planeedges[0, 1]], [planeedges[0, 2], planeedges[1, 2], planeedges[2, 2], planeedges[3, 2], planeedges[0, 2]], c="red", lw=10, solid_capstyle='round') # frame 2D plane
    ax.add_collection3d(Poly3DCollection([planeedges],color="#ff000054"))

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

    maxval = np.max((x2, y2, z2, np.max(planeedges)))

    ax.set_xlim((0, maxval))
    ax.set_ylim((0, maxval))
    ax.set_zlim((0, maxval))

    plt.tight_layout()
    #plt.show()
    plt.savefig(os.path.join(r"C:\Users\CMRT\Desktop\ISMRM Vortrag JSM\Bilder", str(dcm2D[0x0008, 0x103e].value) + "_3D.png"), dpi=300,  bbox_inches='tight', pad_inches=0.05, transparent=True)
    return new_pixel_array

def array_resize(array, new_size, **kwargs):
    from skimage.transform import rescale, resize
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