import os
import pydicom
import copy
import numpy as np

class Setup:
    def __init__(self, path):
        self.obj = []
        self.name = []
        self.series = []
        self.series_num = []
        self.instance_num = []
        self.file = []
        self.load(path)
        return

    def load(self, path):
        for root, _, files in os.walk(path):
            for file in files:
                try:
                    dcm = pydicom.dcmread(os.path.join(root, file))
                    dcm.PatientName
                    self.file.append(os.path.join(root, file))
                    self.obj.append(dcm)
                    self.name.append(dcm[0x0010, 0x0010].value)
                    self.series.append(dcm[0x0008, 0x103e].value)
                    self.series_num.append(dcm[0x0020, 0x0011].value)
                    self.instance_num.append(dcm[0x0020, 0x0013].value)
                except:
                    pass
        return

    def get_pixel_data(self, indices=None, **kwargs):
        if indices is None:
            run_indices = range(len(self.obj))
        elif isinstance(indices, int):
            run_indices = [indices]
        else:
            run_indices = indices

        result = []

        options_representation = kwargs.get("representation", False)
        options_rescale = kwargs.get("rescale", True)
        options_min = kwargs.get("min", 0)
        options_max = kwargs.get("max", 255)

        if len(self.obj) > np.max(run_indices):
            for i in run_indices:
                pixel_data = copy.deepcopy(self.obj[i].pixel_array)

                if options_rescale:
                    try:
                        n = self.obj[i][0x0028, 0x1052].value
                    except:
                        n = None

                    try:
                        m = self.obj[i][0x0028, 0x1053].value
                    except:
                        m = None

                    if not m is None:
                        pixel_data = pixel_data * float(m)

                    if not n is None:
                        pixel_data = pixel_data + float(n)

                if options_representation:
                    try:
                        c = float(self.obj[i][0x0028, 0x1050]) # window center
                    except:
                        c = None
                    try:
                        w = float(self.obj[i][0x0028, 0x1051]) # window width
                    except:
                        w = None

                    if not c is None and not w is None:
                        search_if = pixel_data <= (c-0.5)-((w-1)/2)
                        search_elif = pixel_data > (c-0.5)+((w-1)/2)

                        pixel_data = ((pixel_data-(c-0.5)) / (w-1) + 0.5) * (options_max - options_min) + options_min
                        pixel_data[search_if] = options_min
                        pixel_data[search_elif] = options_max

                result.append(pixel_data)

        if len(result) == 1:
            result = result[0]

        return result