import numpy as np
import os

if __name__ == "__main__":
    from sourcecode import basic_data, basic_functions
    import pydicom

    path = r"C:\Users\CMRT\Documents\DSV\3 - Promotion\Project ReslicingTool\3 - Measurements\Test_Data"
    path_out = r"C:\Users\CMRT\Documents\DSV\3 - Promotion\Project ReslicingTool\6 - Analysis\TestDataExport"
    STs = ["as 3D", "as 2D", "2x2D"]
    profiles = ["rectangular", "triangular", "cosine + 1", "sinc", "standard normal 2", "standard normal 5"]
    studies = os.listdir(path)

    for study in studies:
        cases = os.listdir(os.path.join(path, study))
        for case in cases:
            data = basic_data.Setup(os.path.join(path, study, case))

            index2D = int(np.argwhere(np.array(data.data["acquisitiontype"]) == "2D").flatten())
            sn2D = data.data["seriesnumber"][index2D]
            usn = np.unique(np.array(data.data["seriesnumber"]))
            sn3Ds = usn[usn != sn2D]

            dcm = pydicom.dcmread(data.data["filepath"][index2D])
            counter3D = 0
            for sn3D in sn3Ds:
                counter3D = counter3D + 1
                indeces3D = np.argwhere(np.array(data.data["seriesnumber"]) == sn3D).flatten()
                dcms3D =[]
                for i in range(len(indeces3D)):
                    dcms3D.append(pydicom.dcmread(data.data["filepath"][indeces3D[i]]))

                for profile in profiles:
                    sharpeness = []

                    for ST in STs:
                        if "x" in ST:
                            factor = float(ST[:ST.find("x")])
                            slicethickness = factor * data.data["slicethickness"][index2D]
                        elif ST == "as 2D":
                            slicethickness = data.data["slicethickness"][index2D]
                        else:
                            slicethickness = data.data["slicethickness"][indeces3D[0]]

                        basic_functions.save_reslice(data, sn3D, sn2D, profile, str(slicethickness), os.path.join(path_out, study, profile, str(slicethickness)))
