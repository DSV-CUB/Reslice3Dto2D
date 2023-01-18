import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

size = 11
########################################################################################################################

########################################################################################################################
voxelvalues = 0.5 * np.ones((size,size))

cmap = matplotlib.cm.get_cmap('gray')
grayval = cmap(0.5)
newcolors = np.ones((256, 4))
newcolors[:,0] = grayval[0]
newcolors[:,1] = grayval[1]
newcolors[:,2] = grayval[2]
newcolors[:,3] = 0.7
ipcmap = ListedColormap(newcolors)

ax = plt.figure(figsize=(10,10)).add_subplot()
ax.imshow(voxelvalues, cmap=ipcmap)
ax.get_xaxis().set_ticks([])
ax.get_yaxis().set_ticks([])
ax.set_xlabel("x", fontsize=20)
ax.set_ylabel("y", fontsize=20)
ax.set_title("inplane", fontsize=24)
plt.tight_layout()
plt.savefig(r"D:\ECRC_AG_CMR\3 - Promotion\Project ReslicingTool\6 - Analysis\Figures\Validation_Data\inplane.jpg", dpi=300)


voxelvalues = np.arange(0, (int(size/2)+1)*20-10, step=20, dtype=int)
voxelvalues = np.repeat(np.expand_dims(np.concatenate((voxelvalues, voxelvalues[::-1][1:])), axis=1), size, axis=1)
voxelvalues = voxelvalues / np.max(voxelvalues)

ax = plt.figure(figsize=(10,10)).add_subplot()
ax.imshow(voxelvalues, cmap="gray")
ax.get_xaxis().set_ticks([])
ax.get_yaxis().set_ticks([])
ax.set_xlabel("x", fontsize=20)
ax.set_ylabel("z", fontsize=20)
ax.set_title("perplane", fontsize=24)
plt.tight_layout()
plt.savefig(r"D:\ECRC_AG_CMR\3 - Promotion\Project ReslicingTool\6 - Analysis\Figures\Validation_Data\perplane.jpg", dpi=300)
ax.set_ylabel("y-z", fontsize=20)
ax.set_title("diagplane", fontsize=24)
plt.tight_layout()
plt.savefig(r"D:\ECRC_AG_CMR\3 - Promotion\Project ReslicingTool\6 - Analysis\Figures\Validation_Data\diagplane.jpg", dpi=300)

########################################################################################################################

########################################################################################################################
ax = plt.figure(figsize=(12,10)).add_subplot(projection='3d')
voxelarray = np.ones((size, size, size)).astype(bool)

voxelvalues = np.arange(0, (int(size/2)+1)*20-10, step=20, dtype=int)
voxelvalues = np.repeat(np.expand_dims(np.repeat(np.expand_dims(np.concatenate((voxelvalues, voxelvalues[::-1][1:])), axis=1), size, axis=1), axis=2), size, axis=2)

cmap = matplotlib.cm.get_cmap('gray')
array = voxelvalues / np.max(voxelvalues)
array = cmap(array).astype(object)
for i in range(np.shape(array)[0]):
    for j in range(np.shape(array)[1]):
        for k in range(np.shape(array)[2]):
            cnum = array[i,j,k]
            cnum[-1] = 0.7
            array[i,j,k] = matplotlib.colors.to_hex(cnum, keep_alpha=True)
colorarray = array[:,:,:,0].astype(str)

ax.voxels(voxelarray, facecolors=np.swapaxes(colorarray, 2, 0))
ax.get_xaxis().set_ticks([])
ax.get_yaxis().set_ticks([])
ax.get_zaxis().set_ticks([])
ax.set_xlabel("x", fontsize=20)
ax.set_ylabel("y", fontsize=20)
ax.set_zlabel("z", fontsize=20)
plt.tight_layout()
plt.savefig(r"D:\ECRC_AG_CMR\3 - Promotion\Project ReslicingTool\6 - Analysis\Figures\Validation_Data\3d_data.jpg", dpi=300)
########################################################################################################################

########################################################################################################################
ax = plt.figure(figsize=(12,10)).add_subplot(projection='3d')

voxelarray[:, :int(size-0.33*size), int(0.33*size)+1:] = False
colorarray[:, :int(size-0.33*size), int(0.33*size)+1:] = None
ax.voxels(np.swapaxes(voxelarray, 2, 0), facecolors=np.swapaxes(colorarray, 2, 0))

# inplane
x = [0, size, size, 0, 0]
y = [0, 0, size, size, 0]
z = [size/2, size/2, size/2, size/2, size/2]
ax.plot3D(x,y,z, c="red", zorder=100)

x = [int(0.33*size)+1, size, size, int(0.33*size)+1, int(0.33*size)+1]
y = [0, 0, int(size-0.33*size), int(size-0.33*size), 0]
z = [size/2, size/2, size/2, size/2, size/2]
xyz = [x,y,z]
verts = [(xyz[0][i], xyz[1][i], xyz[2][i]) for i in range(len(xyz[0]))]
ax.add_collection3d(Poly3DCollection([verts],color="#ff000054")) # Add a polygon instead of fill_between

# perplane
x = [0, size, size, 0, 0]
y = [size/2, size/2, size/2, size/2, size/2]
z = [0, 0, size, size, 0]
ax.plot3D(x,y,z, c="red", zorder=100)

x = [int(0.33*size)+1, size, size, int(0.33*size)+1]
y = [size/2, size/2, size/2, size/2]
z = [0, 0, size, size]
xyz = [x,y,z]
verts = [(xyz[0][i], xyz[1][i], xyz[2][i]) for i in range(len(xyz[0]))]
ax.add_collection3d(Poly3DCollection([verts],color="#ff000054")) # Add a polygon instead of fill_between

# diagplane
x = [0, size, size, 0, 0]
y = [0, 0, size, size, 0]
z = [0, 0, size, size, 0]
ax.plot3D(x,y,z, c="red", zorder=100)

x = [int(0.33*size)+1, size, size, int(0.33*size)+1]
y = [0, 0, int(size-0.33*size), int(size-0.33*size)]
z = [0, 0, int(size-0.33*size), int(size-0.33*size)]
xyz = [x,y,z]
verts = [(xyz[0][i], xyz[1][i], xyz[2][i]) for i in range(len(xyz[0]))]
ax.add_collection3d(Poly3DCollection([verts],color="#ff000054")) # Add a polygon instead of fill_between

#settings
ax.get_xaxis().set_ticks([])
ax.get_yaxis().set_ticks([])
ax.get_zaxis().set_ticks([])
ax.set_xlabel("x", fontsize=20)
ax.set_ylabel("y", fontsize=20)
ax.set_zlabel("z", fontsize=20)
plt.tight_layout()
plt.savefig(r"D:\ECRC_AG_CMR\3 - Promotion\Project ReslicingTool\6 - Analysis\Figures\Validation_Data\3d_data_sliced.jpg", dpi=300)
########################################################################################################################

########################################################################################################################
ax = plt.figure(figsize=(12,10)).add_subplot(projection='3d')

# frame
x = [0, size, size, 0, 0]
y = [0, 0, size, size, 0]
z = [0, 0, 0, 0, 0]
ax.plot3D(x,y,z, c="blue", zorder=100)
x = [0, size, size, 0, 0]
y = [0, 0, size, size, 0]
z = [size, size, size, size, size]
ax.plot3D(x,y,z, c="blue", zorder=100)
x = [0, 0]
y = [0, 0]
z = [0, size]
ax.plot3D(x,y,z, c="blue", zorder=100)
x = [size, size]
y = [0, 0]
z = [0, size]
ax.plot3D(x,y,z, c="blue", zorder=100)
x = [0, 0]
y = [size, size]
z = [0, size]
ax.plot3D(x,y,z, c="blue", zorder=100)
x = [size, size]
y = [size, size]
z = [0, size]
ax.plot3D(x,y,z, c="blue", zorder=100)

# inplane
x = [0, size, size, 0, 0]
y = [0, 0, size, size, 0]
z = [size/2, size/2, size/2, size/2, size/2]
ax.plot3D(x,y,z, c="red", zorder=100)

x = [0, size, size, 0, 0]
y = [0, 0, size, size, 0]
z = [size/2, size/2, size/2, size/2, size/2]
xyz = [x,y,z]
verts = [(xyz[0][i], xyz[1][i], xyz[2][i]) for i in range(len(xyz[0]))]
ax.add_collection3d(Poly3DCollection([verts],color="#ff000054")) # Add a polygon instead of fill_between

# perplane
x = [0, size, size, 0, 0]
y = [size/2, size/2, size/2, size/2, size/2]
z = [0, 0, size, size, 0]
ax.plot3D(x,y,z, c="red", zorder=100)

x = [0, size, size, 0, 0]
y = [size/2, size/2, size/2, size/2, size/2]
z = [0, 0, size, size, 0]
xyz = [x,y,z]
verts = [(xyz[0][i], xyz[1][i], xyz[2][i]) for i in range(len(xyz[0]))]
ax.add_collection3d(Poly3DCollection([verts],color="#ff000054")) # Add a polygon instead of fill_between

# diagplane
x = [0, size, size, 0, 0]
y = [0, 0, size, size, 0]
z = [0, 0, size, size, 0]
ax.plot3D(x,y,z, c="red", zorder=100)

x = [0, size, size, 0, 0]
y = [0, 0, size, size, 0]
z = [0, 0, size, size, 0]
xyz = [x,y,z]
verts = [(xyz[0][i], xyz[1][i], xyz[2][i]) for i in range(len(xyz[0]))]
ax.add_collection3d(Poly3DCollection([verts],color="#ff000054")) # Add a polygon instead of fill_between

#settings
ax.get_xaxis().set_ticks([])
ax.get_yaxis().set_ticks([])
ax.get_zaxis().set_ticks([])
ax.set_xlabel("x", fontsize=20)
ax.set_ylabel("y", fontsize=20)
ax.set_zlabel("z", fontsize=20)
plt.tight_layout()
plt.savefig(r"D:\ECRC_AG_CMR\3 - Promotion\Project ReslicingTool\6 - Analysis\Figures\Validation_Data\2d_data.jpg", dpi=300)
########################################################################################################################

########################################################################################################################
size = 101

#x, y, z = np.indices((size, size, size))
voxelarray = np.ones((size, size, size)).astype(bool)

voxelvalues = np.arange(0, (int(size/2)+1)*20-10, step=20, dtype=int)
voxelvalues = np.repeat(np.expand_dims(np.repeat(np.expand_dims(np.concatenate((voxelvalues, voxelvalues[::-1][1:])), axis=1), size, axis=1), axis=2), size, axis=2)

cmap = matplotlib.cm.get_cmap('gray')
array = voxelvalues / np.max(voxelvalues)
array = cmap(array).astype(object)
for i in range(np.shape(array)[0]):
    for j in range(np.shape(array)[1]):
        for k in range(np.shape(array)[2]):
            cnum = array[i,j,k]
            cnum[-1] = 0.7
            array[i,j,k] = matplotlib.colors.to_hex(cnum, keep_alpha=True)
colorarray = array[:,:,:,0].astype(str)


ax = plt.figure(figsize=(12,10)).add_subplot(projection='3d')
ax.voxels(voxelarray, facecolors=np.swapaxes(colorarray, 2, 0))
ax.get_xaxis().set_ticks([])
ax.get_yaxis().set_ticks([])
ax.get_zaxis().set_ticks([])
ax.set_xlabel("x", fontsize=20)
ax.set_ylabel("y", fontsize=20)
ax.set_zlabel("z", fontsize=20)
plt.tight_layout()
plt.savefig(r"D:\ECRC_AG_CMR\3 - Promotion\Project ReslicingTool\6 - Analysis\Figures\Validation_Data\3d_space.jpg", dpi=300)
########################################################################################################################

#plt.show()
stop = True