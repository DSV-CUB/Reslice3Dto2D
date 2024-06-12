import numpy as np
import os
from sourcecode import basic_data, basic_functions
import pydicom
from matplotlib import pyplot as plt

def rgb_to_greyscale(array):
    result = np.array(array)
    result = np.squeeze(result)

    if len(np.shape(result)) == 3 and np.shape(result)[-1] == 3:
        result = np.squeeze(0.3 * result[:,:,0] + 0.59 * result[:,:,1] + 0.11 * result[:,:,2])
    else:
        result = None

    return result


def get_image_sharpeness_measure(array):
    # https://reader.elsevier.com/reader/sd/pii/S1877705813016007?token=F90A4C91FF94E4B4AE6BDC51DF8556D4DE7B5E447696DECF5305888C9EB896F5C10020D4F1702E63E2293A165D3FB401&originRegion=eu-west-1&originCreation=20221130144050
    if len(np.shape(array)) == 3:
        image = rgb_to_greyscale(array)
    elif len(np.shape(array)) == 2:
        image = np.copy(array)
    else:
        image = None

    if not image is None:
        if not np.max(image) == 0:
            image = image / np.max(image)

        F = np.fft.fft2(image)
        Fc = np.fft.fftshift(F)
        AF = np.abs(Fc)
        M = np.max(AF)
        threshold = M / 1000
        Th = np.count_nonzero(F>threshold)
        FM = Th / (np.shape(image)[0] * np.shape(image)[1])
        result = FM
    else:
        result = None
    return result



if __name__ == "__main__":
    path = r"C:\Users\CMRT\Documents\DSV\3 - Promotion\Project ReslicingTool\6 - Analysis\TestDataExamples\DICOM"
    path_out = r"C:\Users\CMRT\Documents\DSV\3 - Promotion\Project ReslicingTool\6 - Analysis\TestDataExamples"
    STs = ["as 3D", "as 2D", "2x2D"]
    profiles = ["rectangular", "triangular", "cosine + 1", "sinc", "standard normal 2", "standard normal 5"]
    size = 140

    cases = os.listdir(path)
    for case in cases:
        try:
            data = basic_data.Setup(os.path.join(path, case))

            index2D = int(np.argwhere(np.array(data.data["acquisitiontype"]) == "2D").flatten())
            sn2D = data.data["seriesnumber"][index2D]
            usn = np.unique(np.array(data.data["seriesnumber"]))
            sn3Ds = usn[usn != sn2D]
            dcm = pydicom.dcmread(data.data["filepath"][index2D])

            from sourcecode import basic_functions
            pa = basic_functions.get_pixel_data(data.data["filepath"][index2D], representation=True)
            sharpeness = get_image_sharpeness_measure(pa)
            path_to = os.path.join(path_out, "original", case)
            os.makedirs(path_to, exist_ok=True)
            dx = int((np.shape(pa)[0]-size)/2)
            dy = int((np.shape(pa)[1]-size)/2)
            pa = pa[dx:dx+size, dy:dy+size]
            fig = plt.figure(1, figsize=[16, 9], dpi=600)
            plt.imshow(pa, cmap="gray")
            plt.axis('off')
            plt.tight_layout()
            plt.savefig(os.path.join(path_to, case + "_" + str(sharpeness)) +".jpg", bbox_inches="tight", pad_inches=0, dpi=600)
            plt.clf()
            continue

            for sn3D in sn3Ds:
                indeces3D = np.argwhere(np.array(data.data["seriesnumber"]) == sn3D).flatten()
                dcms3D =[]
                for i in range(len(indeces3D)):
                    dcms3D.append(pydicom.dcmread(data.data["filepath"][indeces3D[i]]))

                for profile in profiles:
                    for ST in STs:
                        if "x" in ST:
                            factor = float(ST[:ST.find("x")])
                            slicethickness = factor * data.data["slicethickness"][index2D]
                        elif ST == "as 2D":
                            slicethickness = data.data["slicethickness"][index2D]
                        else:
                            slicethickness = data.data["slicethickness"][indeces3D[0]]

                        resliced = basic_functions.reslice(dcms3D, dcm, slicethickness, profile)
                        sharpeness = get_image_sharpeness_measure(resliced)

                        path_to = os.path.join(path_out, ''.join(e for e in profile if e.isalnum()), str(slicethickness), case)
                        os.makedirs(path_to, exist_ok=True)
                        dx = int((np.shape(resliced)[0]-size)/2)
                        dy = int((np.shape(resliced)[1]-size)/2)
                        pa = resliced[dx:dx+size, dy:dy+size]
                        fig = plt.figure(1, figsize=[16, 9], dpi=600)
                        plt.imshow(pa, cmap="gray")
                        plt.axis('off')
                        plt.tight_layout()
                        plt.savefig(os.path.join(path_to, case + "_" + str(sn3D) + "_" + str(sharpeness)) +".jpg", bbox_inches="tight", pad_inches=0, dpi=600)
                        plt.clf()
        except:
            print("ERROR with case: " + case)