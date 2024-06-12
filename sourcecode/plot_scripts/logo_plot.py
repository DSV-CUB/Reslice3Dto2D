import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

size = 11
########################################################################################################################

########################################################################################################################

ax = plt.figure(figsize=(10,10)).add_subplot(projection='3d')

# frame
x = [0, size, size, 0, 0]
y = [0, 0, size, size, 0]
z = [0, 0, 0, 0, 0]
ax.plot3D(x,y,z, c="blue", lw=10, zorder=100)
x = [0, size, size, 0, 0]
y = [0, 0, size, size, 0]
z = [size, size, size, size, size]
ax.plot3D(x,y,z, c="blue", lw=10, zorder=100)
x = [0, 0]
y = [0, 0]
z = [0, size]
ax.plot3D(x,y,z, c="blue", lw=10, zorder=100)
x = [size, size]
y = [0, 0]
z = [0, size]
ax.plot3D(x,y,z, c="blue", lw=10, zorder=100)
x = [0, 0]
y = [size, size]
z = [0, size]
ax.plot3D(x,y,z, c="blue", lw=10, zorder=100)
x = [size, size]
y = [size, size]
z = [0, size]
ax.plot3D(x,y,z, c="blue", lw=10, zorder=100)

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
ax.axis("off")
plt.tight_layout()
plt.savefig(r"C:\Users\CMRT\Documents\DSV\3 - Promotion\Project ReslicingTool\6 - Analysis\logo.png", dpi=300,  bbox_inches='tight')
########################################################################################################################

########################################################################################################################