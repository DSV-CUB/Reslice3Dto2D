import os
import numpy as np
from scipy.stats import norm
from matplotlib import pyplot as plt
plt.rcParams["font.family"] = "Calibri"

profiles = ["rectangular", "triangular", "cosine + 1", "sinc", "standard normal 2", "standard normal 5"]
num_points = 3
path_out = r"C:\Users\CMRT\Documents\DSV\3 - Promotion\Project ReslicingTool\6 - Analysis\SliceProfiles"

########################################################################################################################

def get_weight(profile, k, n):
    if k == 0 or profile == "rectangular":
        result = 1
    elif profile == "triangular":
        result = (n-abs(k))/n
    elif profile == "cosine + 1":
        result = (np.cos((k/n) * np.pi) + 1) / 2
    elif profile == "sinc":
        result = np.sinc(k/n)
    elif profile == "standard normal 2":
        result = norm.pdf(2 * (k/n), loc=0, scale=1) / norm.pdf(0, loc=0, scale=1)
    elif profile == "standard normal 5":
        result = norm.pdf(5 * (k/n), loc=0, scale=1) / norm.pdf(0, loc=0, scale=1)
    return result


for profile in profiles:
    point_x = np.arange(-num_points, num_points+1,1).astype(int)
    point_y = np.array([get_weight(profile, k, num_points) for k in point_x])
    cont_x = np.linspace(-num_points, num_points, 1000, endpoint=True)
    cont_y = np.array([get_weight(profile, k, num_points) for k in cont_x])

    ax = plt.figure(figsize=(20,10)).add_subplot()

    ax.scatter(point_x, point_y, c="red", s=300, zorder=100)
    ax.plot(cont_x, cont_y, c="#6c02d6", lw=7)
    ax.plot([cont_x[0], cont_x[0]], [0, cont_y[0]], c="#6c02d6", lw=7)
    ax.plot([cont_x[-1], cont_x[-1]], [0, cont_y[-1]], c="#6c02d6", lw=7)




    ax.set_xlim([-num_points-0.25, num_points+0.25])
    ax.set_ylim([0, (num_points*2+0.5)/(2*num_points)])
    ax.set_title(profile, fontdict={'fontsize': 40, "fontweight": "bold"})
    ax.set_xlabel("relative position", fontdict={'fontsize': 38})
    ax.set_ylabel("relative weight", fontdict={'fontsize': 38})
    ax.set_xticks([-num_points, 0, num_points])
    ax.set_xticklabels(["-num", 0, "num"], fontdict={'fontsize': 36})
    ax.set_yticks([0, 1])
    ax.set_yticklabels([0, 1], fontdict={'fontsize': 36})

    plt.tight_layout()
    plt.savefig(os.path.join(path_out, profile + ".jpg"), dpi=600)