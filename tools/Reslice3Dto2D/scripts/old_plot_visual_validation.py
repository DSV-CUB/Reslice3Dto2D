import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib import pyplot as plt
from matplotlib.colors import ListedColormap
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

if __name__ == "__main__":

    # create own colormap
    newcolors = np.ones((256, 4))
    newcolors[:,1] = 0
    newcolors[:,2] = 0
    redcmp = ListedColormap(newcolors)

    newcolors = np.ones((256, 4))
    newcolors[:,0] = 0
    newcolors[:,2] = 0
    greencmp = ListedColormap(newcolors)


    fig = plt.figure(1)
    ax = fig.add_subplot(projection='3d')

    ax.plot3D([-10, -10, 10, 10, -10],[-10, 10, 10, -10, -10],[0,0,0,0,0], c="red")
    ax.plot3D([0,0,0,0,0], [-10, -10, 10, 10, -10],[-10, 10, 10, -10, -10], c="red")
    ax.plot3D([-10, -10, 10, 10, -10],[-10, 10, 10, -10, -10],[-10,-10,10,10,-10], c="red")

    xyz = [[-10, -10, 10, 10, -10],[-10, 10, 10, -10, -10],[0,0,0,0,0]]
    verts = [(xyz[0][i], xyz[1][i], xyz[2][i]) for i in range(len(xyz[0]))]
    ax.add_collection3d(Poly3DCollection([verts],color="#ff000054")) # Add a polygon instead of fill_between

    xyz = [[0,0,0,0,0], [-10, -10, 10, 10, -10],[-10, 10, 10, -10, -10]]
    verts = [(xyz[0][i], xyz[1][i], xyz[2][i]) for i in range(len(xyz[0]))]
    ax.add_collection3d(Poly3DCollection([verts],color="#ff000054")) # Add a polygon instead of fill_between

    xyz = [[-10, -10, 10, 10, -10],[-10, 10, 10, -10, -10],[-10,-10,10,10,-10]]
    verts = [(xyz[0][i], xyz[1][i], xyz[2][i]) for i in range(len(xyz[0]))]
    ax.add_collection3d(Poly3DCollection([verts],color="#ff000054")) # Add a polygon instead of fill_between

    ax.plot3D([-10, -10, 10, 10, -10],[-10, 10, 10, -10, -10],[-10,-10,-10,-10,-10], c="blue")
    ax.plot3D([-10, -10, 10, 10, -10],[-10, 10, 10, -10, -10],[10,10,10,10,10], c="blue")
    ax.plot3D([-10, -10],[-10, -10],[-10, 10], c="blue")
    ax.plot3D([-10, -10],[10, 10],[-10, 10], c="blue")
    ax.plot3D([10, 10],[10, 10],[-10, 10], c="blue")
    ax.plot3D([10, 10],[-10, -10],[-10, 10], c="blue")

    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])
    #ax.set_axis_off()
    ax.view_init(20, -135)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

    plt.tight_layout()
    plt.show()

