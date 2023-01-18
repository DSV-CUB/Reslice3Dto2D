import numpy as np
import os
from tools.Reslice3Dto2D import dicom
from scipy import stats
import pandas as pd
from statsmodels.stats.anova import AnovaRM

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

def get_statistics(array, reference_column=0):


    description = ["Mean", "STD", "Median", "25%Quantile", "75%Quantile", "Min", "Max", "Shapiro", "Shapiro Log", "Wilcoxon", "ttest", "ttest log", "Friedman", "ANOVA", "ANOVA log"]
    statistics = np.zeros((15,np.shape(array)[1]))

    statistics[0,:] = np.mean(array, axis=0)
    statistics[1,:] = np.std(array, axis=0)
    statistics[2,:] = np.median(array, axis=0)
    statistics[3,:] = np.quantile(array, 0.25, axis=0)
    statistics[4,:] = np.quantile(array, 0.75, axis=0)
    statistics[5,:] = np.min(array, axis = 0)
    statistics[6,:] = np.max(array, axis=0)

    tests = []
    for i in range(np.shape(array)[1]):
        tests.append(round(stats.shapiro(array[:,i].flatten())[-1], 4))
        tests.append(round(stats.shapiro(np.log(np.array(array[:,i].flatten() + 1e-100)))[-1], 4))
        if i == reference_column:
            tests.append(-1)
            tests.append(-1)
            tests.append(-1)
        else:
            tests.append(round(stats.wilcoxon(array[:,reference_column].flatten(), array[:,i].flatten(), alternative="two-sided")[-1], 4))
            tests.append(round(stats.ttest_rel(array[:,reference_column].flatten(), array[:,i].flatten(), nan_policy="omit")[-1], 4))
            tests.append(round(stats.ttest_rel(np.log(array[:,reference_column].flatten()), np.log(array[:,i].flatten()), nan_policy="omit")[-1], 4))

    tests = np.array(tests)
    tests = np.transpose(tests.reshape(-1,5))
    statistics[7:12,:] = tests
    statistics[12,:] = np.array([round(stats.friedmanchisquare(*array)[-1], 4)] * np.shape(array)[1]).flatten()

    try:
        statdata = []
        for ii in range(np.shape(array)[1]):
            col_metrics = np.array(array[:ii].flatten())
            col_patient = np.arange(0, len(col_metrics))
            col_model = np.ones(np.shape(col_metrics)) * ii
            stack = np.stack((col_patient, col_model, col_metrics))

            if len(statdata) == 0:
                statdata = stack
            else:
                statdata = np.hstack((statdata, stack))


        df = pd.DataFrame((statdata.T), columns=["patient", "model", "metric_value"])
        arm = AnovaRM(df, "metric_value", "patient", ["model"])
        armresult = arm.fit()

        statistics[13,:] = np.array([round(armresult.anova_table["Pr > F"][0], 4)]* np.shape(array)[1]).flatten()
    except:
        statistics[13,:] = np.array([-1]* np.shape(array)[1]).flatten()

    try:
        statdata = []
        for ii in range(np.shape(array)[1]):
            col_metrics = np.log(np.array(array[:,ii].flatten()))
            col_patient = np.arange(0, len(col_metrics))
            col_model = np.ones(np.shape(col_metrics)) * ii
            stack = np.stack((col_patient, col_model, col_metrics))

            if len(statdata) == 0:
                statdata = stack
            else:
                statdata = np.hstack((statdata, stack))


        df = pd.DataFrame((statdata.T), columns=["patient", "model", "metric_value"])
        arm = AnovaRM(df, "metric_value", "patient", ["model"])
        armresult = arm.fit()

        statistics[14,:] = np.array([round(armresult.anova_table["Pr > F"][0], 4)]* np.shape(array)[1]).flatten()
    except:
        statistics[14,:] = np.array([-1]* np.shape(array)[1]).flatten()

    return statistics, description


if __name__ == "__main__":
    if True:
        path_data = r"C:\Users\CMRT\Documents\DSV\3 - Promotion\Project ReslicingTool\6 - Analysis\Testdata_New"

        dcms = dicom.Setup(path_data)
        images = dcms.get_pixel_data()
        ism = []

        for img in images:
            ism.append(get_image_sharpeness_measure(img))

        with open(os.path.join(path_data, "sharpness_measure.txt"), "w") as file:
            for i in range(len(ism)):
                file.write(dcms.file[i] + "\t" + str(ism[i]) + "\n")
            file.close()
    if False:
        path_out = r"C:\Users\CMRT\Documents\DSV\3 - Promotion\Project ReslicingTool\6 - Analysis"
        paths = [r"C:\Users\CMRT\Documents\DSV\3 - Promotion\Project ReslicingTool\6 - Analysis\Testdata_MyoMet\0", r"C:\Users\CMRT\Documents\DSV\3 - Promotion\Project ReslicingTool\6 - Analysis\Testdata_MyoMet\#None", r"C:\Users\CMRT\Documents\DSV\3 - Promotion\Project ReslicingTool\6 - Analysis\Testdata_MyoMet\9.99"]

        sharpeness_matrix = []
        for path in paths:
            dcms = dicom.Setup(path)
            images = dcms.get_pixel_data()
            ism = []
            for img in images:
                ism.append(get_image_sharpeness_measure(img))
            sharpeness_matrix.append(ism)
        sharpeness_matrix = np.transpose(sharpeness_matrix)

        statistics, names = get_statistics(sharpeness_matrix)

        with open(os.path.join(path_out, "sharpness_measure_MyoMet.txt"), "w") as file:
            for i in range(np.shape(sharpeness_matrix)[0]):
                file.write(str(i) + "\t" + "\t".join(sharpeness_matrix[i,:].flatten().astype(str).tolist()) + "\n")

            file.write("\n")
            for i in range(np.shape(statistics)[0]):
                file.write(names[i] + "\t" + "\t".join(statistics[i,:].flatten().astype(str).tolist()) + "\n")

            file.close()


        a=0