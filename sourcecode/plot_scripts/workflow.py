import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import matplotlib
import os
matplotlib.use('Qt5Agg')

path_out = r"C:\Users\CMRT\Documents\DSV\3 - Promotion\Project ReslicingTool\6 - Analysis\Workflow"
size = 10
########################################################################################################################

########################################################################################################################

def plot(path, options=[]):
    ax = plt.figure(figsize=(10,10)).add_subplot(projection='3d')
    ax.view_init(elev=12, azim=-50)

    # frame
    x = [0, size, size, 0, 0]
    y = [0, 0, size, size, 0]
    z = [0, 0, 0, 0, 0]
    ax.plot3D(x,y,z, c="blue", lw=3, zorder=100)
    x = [0, size, size, 0, 0]
    y = [0, 0, size, size, 0]
    z = [size, size, size, size, size]
    ax.plot3D(x,y,z, c="blue", lw=3, zorder=100)
    x = [0, 0]
    y = [0, 0]
    z = [0, size]
    ax.plot3D(x,y,z, c="blue", lw=3, zorder=100)
    x = [size, size]
    y = [0, 0]
    z = [0, size]
    ax.plot3D(x,y,z, c="blue", lw=3, zorder=100)
    x = [0, 0]
    y = [size, size]
    z = [0, size]
    ax.plot3D(x,y,z, c="blue", lw=3, zorder=100)
    x = [size, size]
    y = [size, size]
    z = [0, size]
    ax.plot3D(x,y,z, c="blue", lw=3, zorder=100)

    if "points3D" in options:
        x = np.arange(0,size+1,1)
        y = np.arange(0,size+1,1)
        z = np.arange(0,size+1,1)
        X,Y,Z = np.meshgrid(x,y,z)
        ax.scatter(X,Y,Z,c="blue", s=5)

    # plane
    xp = [0, size, size, 0, 0]
    yp = [0, 0, size, size, 0]
    zp = [0, 0, size, size, 0]
    x = [0, size, size, 0, 0]
    y = [0, 0, size, size, 0]
    z = [0, 0, size, size, 0]
    xyz = [x,y,z]
    verts = [np.array((xyz[0][i], xyz[1][i], xyz[2][i])) for i in range(len(xyz[0]))]
    if "plane" in options:
        ax.plot3D(xp,yp,zp, c="red", zorder=100)
        ax.add_collection3d(Poly3DCollection([verts],color="#ff000054")) # Add a polygon instead of fill_between

    # plane normal
    v1 = verts[1] - verts[0]
    v2 = verts[2] - verts[0]
    n = np.cross(v1, v2)
    n = n / np.linalg.norm(n)
    nminus = -n

    if "normal" in options:
        #ax.plot3D([int(size/2), int(size/2)+5*n[0]], [int(size/2), int(size/2)+5*n[1]], [int(size/2), int(size/2)+5*n[2]],c="red")

        ax.quiver(int(size/2),int(size/2),int(size/2), 5*n[0], 5*n[1], 5*n[2], color="red", lw=2)
        ax.quiver(int(size/2),int(size/2),int(size/2), 5*nminus[0], 5*nminus[1], 5*nminus[2], color="red", lw=2)

    # parallel planes
    if "parallel" in options:
        for i in range(3):
            ax.plot3D(xp+(i+1)*n[0], yp+(i+1)*n[1], zp+(i+1)*n[2], c="#ffaaaa", zorder=100)
            verts = [np.array((xyz[0][j]+(i+1)*n[0], xyz[1][j]+(i+1)*n[1], xyz[2][j]+(i+1)*n[2])) for j in range(len(xyz[0]))]
            ax.add_collection3d(Poly3DCollection([verts],color="#ffaaaa54")) # Add a polygon instead of fill_between

            ax.plot3D(xp+(i+1)*nminus[0], yp+(i+1)*nminus[1], zp+(i+1)*nminus[2], c="#ffaaaa", zorder=100)
            verts = [np.array((xyz[0][j]+(i+1)*nminus[0], xyz[1][j]+(i+1)*nminus[1], xyz[2][j]+(i+1)*nminus[2])) for j in range(len(xyz[0]))]
            ax.add_collection3d(Poly3DCollection([verts],color="#ffaaaa54")) # Add a polygon instead of fill_between

    # point plot
    if "point" in options:
        xyzp = np.array([size-0.5, size/2, size/2])
        #ax.scatter(xyzp[0], xyzp[1], xyzp[2], c="#6c02d6", s=50, zorder=10000)


        x = [size-1, size, size, size-1]
        y = [size/2-0.5, size/2-0.5, size/2+0.5, size/2+0.5]
        z = [size/2-0.5, size/2-0.5, size/2+0.5, size/2+0.5]
        xyz = [x,y,z]
        verts = [np.array((xyz[0][i], xyz[1][i], xyz[2][i])) for i in range(len(xyz[0]))]
        ax.add_collection3d(Poly3DCollection([verts],color="#6c02d6")) # Add a polygon instead of fill_between

    if "pointparallel" in options:
        for i in range(-3,4,1):
            x = [size-1, size, size, size-1] + i * n[0]
            y = [size/2-0.5, size/2-0.5, size/2+0.5, size/2+0.5]+ i * n[1]
            z = [size/2-0.5, size/2-0.5, size/2+0.5, size/2+0.5]+ i * n[2]
            xyz = [x,y,z]
            verts = [np.array((xyz[0][i], xyz[1][i], xyz[2][i])) for i in range(len(xyz[0]))]
            ax.add_collection3d(Poly3DCollection([verts],color="#6c02d6")) # Add a polygon instead of fill_between

    if "pointweight" in options:
        # point weight
        xyzp = np.array([size-1, size/2-0.5, size/2-0.5])
        ax.plot3D([xyzp[0]-3*n[0], xyzp[0]+3*n[0]], [xyzp[1]-3*n[1], xyzp[1]+3*n[1]], [xyzp[2]-3*n[2], xyzp[2]+3*n[2]], c="#6c02d6", zorder=100, lw=2, solid_capstyle="round")
        xyzp = np.array([size, size/2-0.5, size/2-0.5])
        ax.plot3D([xyzp[0]-3*n[0], xyzp[0]+3*n[0]], [xyzp[1]-3*n[1], xyzp[1]+3*n[1]], [xyzp[2]-3*n[2], xyzp[2]+3*n[2]], c="#6c02d6", zorder=100, lw=2, solid_capstyle="round")
        xyzp = np.array([size, size/2+0.5, size/2+0.5])
        ax.plot3D([xyzp[0]-3*n[0], xyzp[0]+3*n[0]], [xyzp[1]-3*n[1], xyzp[1]+3*n[1]], [xyzp[2]-3*n[2], xyzp[2]+3*n[2]], c="#6c02d6", zorder=100, lw=2, solid_capstyle="round")

        ax.plot3D([size-1, size, size, size-1, size-1] + 3*n[0], [size/2-0.5, size/2-0.5, size/2+0.5, size/2+0.5, size/2-0.5]+ 3*n[1], [size/2-0.5, size/2-0.5, size/2+0.5, size/2+0.5, size/2-0.5] + 3*n[2], c="#6c02d6", zorder=100, lw=2, solid_capstyle="round")
        ax.plot3D([size-1, size, size] - 3*n[0], [size/2-0.5, size/2-0.5, size/2+0.5] - 3*n[1], [size/2-0.5, size/2-0.5, size/2+0.5] - 3*n[2], c="#6c02d6", zorder=100, lw=2, solid_capstyle="round")



    #settings
    ax.get_xaxis().set_ticks([])
    ax.get_yaxis().set_ticks([])
    ax.get_zaxis().set_ticks([])
    ax.axis("off")
    ax.set_xlim(-2, size+2)
    ax.set_ylim(-2, size+2)
    ax.set_zlim(-2, size+2)
    plt.tight_layout()
    #plt.show()
    plt.savefig(path, dpi=600,  bbox_inches='tight')
    return
if False:
    plot(os.path.join(path_out, "1.jpg"), [])
    plot(os.path.join(path_out, "2.jpg"), ["plane"])
    plot(os.path.join(path_out, "3.jpg"), ["plane", "point"])
    plot(os.path.join(path_out, "4.jpg"), ["plane", "normal", "point"])
    plot(os.path.join(path_out, "5.jpg"), ["plane", "parallel", "point", "pointparallel", "pointweight"])

ax = plt.figure(figsize=(10,10)).add_subplot()

image = np.random.rand(100).reshape((10, 10))
image = 0.5*(image/np.max(image))
image[2, 5] = 1
image[2, 6] = 1
image[3, 7] = 1
image[4, 8] = 1
image[5, 8] = 1
image[6, 7] = 1
image[6, 6] = 1
image[6, 5] = 1
image[5, 4] = 1
image[4, 4] = 1
image[3, 4] = 1

image[4, 3] = 1
image[5, 2] = 1
image[6, 2] = 1
image[7, 3] = 1
image[7, 4] = 1
image[7, 5] = 1


ax.imshow(image, cmap="Purples")

ax.get_xaxis().set_ticks([])
ax.get_yaxis().set_ticks([])
#ax.axis("off")
for axis in ['top','bottom','left','right']:
    ax.spines[axis].set_linewidth(4)
    ax.spines[axis].set_color('red')

plt.tight_layout()
#plt.show()
plt.savefig(os.path.join(path_out, "6.jpg"), dpi=600,  bbox_inches='tight')

########################################################################################################################

########################################################################################################################