import pydicom
import numpy as np
import os

class Setup:
    def __init__(self, path=None):
        self.data = {}
        self.data["studyUID"] = []
        self.data["patientname"] = []
        self.data["seriesnumber"] = []
        self.data["seriesdescription"] = []
        self.data["instancenumber"] = []
        self.data["acquisitiontype"] = []
        self.data["triggertime"] = []
        self.data["imageposition"] = []
        self.data["imageorientation"] = []
        self.data["slicethickness"] = []
        self.data["filepath"] = []

        if not path is None:
            self.load(path)
        return

    def load(self, path):
        for root, _, files in os.walk(path):
            for file in files:
                try:
                    filepath = os.path.join(root, file)
                    dcm = pydicom.dcmread(filepath)
                    studyUID = str(dcm[0x0020, 0x000d].value)
                    patientname = str(dcm[0x0010, 0x0010].value)
                    seriesnumber = int(dcm[0x0020, 0x0011].value)
                    seriesdescription = str(dcm[0x0008, 0x103e].value)
                    instancenumber = int(dcm[0x0020, 0x0013].value)
                    acquisitiontype = str(dcm[0x0018, 0x0023].value)
                    imageposition = np.asarray(dcm[0x0020, 0x0032].value, np.double)
                    imageorientation = np.asarray(dcm[0x0020, 0x0037].value, np.double)
                    slicethickness = float(dcm[0x0018, 0x0050].value)

                    try:
                        triggertime = float(dcm[0x0018, 0x1060].value)
                    except:
                        triggertime = 0

                    self.data["studyUID"].append(studyUID)
                    self.data["patientname"].append(patientname)
                    self.data["seriesnumber"].append(seriesnumber)
                    self.data["seriesdescription"].append(seriesdescription)
                    self.data["instancenumber"].append(instancenumber)
                    self.data["acquisitiontype"].append(acquisitiontype)
                    self.data["triggertime"].append(triggertime)
                    self.data["imageposition"].append(imageposition)
                    self.data["imageorientation"].append(imageorientation)
                    self.data["slicethickness"].append(slicethickness)
                    self.data["filepath"].append(filepath)
                except:
                    continue
        return

    def get_subset(self, SUID):
        data = Setup()
        indeces = np.argwhere(np.array(self.data["studyUID"], dtype=str) == SUID).flatten()

        for key, value in self.data.items():
            data.data[key] = np.array(value)[indeces].tolist()
        return data