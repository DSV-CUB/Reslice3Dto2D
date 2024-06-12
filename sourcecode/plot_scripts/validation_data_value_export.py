import pydicom
import os
import numpy as np

path = r"C:\Users\CMRT\Documents\DSV\3 - Promotion\Project ReslicingTool\6 - Analysis\R3D2Dexport\ValidationDataset"

wfile = open(os.path.join(path, "overview.txt"), "w")
for root, _, files in os.walk(path):
    for file in files:
        try:
            dcm = pydicom.dcmread(os.path.join(root, file))
            values = dcm.pixel_array.astype(str)[:,0].tolist()
            sd = str(dcm[0x0008, 0x103e].value)
            s = sd + "\t" + "\t".join(values) + "\n"
            wfile.write(s)
        except:
            pass
wfile.close()