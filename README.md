# Reslice3Dto2D

This sourcecode is part of the publication

Viezzer, D. et al. Reslice3Dto2D: Introduction of a software tool to reformat quantitative 3D volumes measurements into 
reference 2D slices in cardiovascular magnetic resonance imaging. tba. https://doi.org/tba

## User Manual
Please refer to the UserManual.pdf

## Installation
- Download and install Python 3.8 from https://www.python.org/downloads/
- Download the Reslice3Dto2D software
- Run in a command window pip install -r requirements.txt 

## Usage
The application can be started using the RUN.sh or RUN_WINDOWS.bat (Microsoft Windows only).

![Screenshot](GUI.jpg)


After starting the application, the click on [1] opens a dialog to choose a directory with data that should be imported. The chosen directory must contain only data from one examination. The load button [2] imports the DICOM data in the given directory from [1]. Depending on the amount of data within the examination, this step may take some time. During that time, the GUI freezes. The suffix of the data can be arbitrary as each file is checked for DICOM information. The dropdown menu [3] automatically shows the sequence number and name of the first occurring 3D sequence. The strict axial planes of the chosen 3D Dataset are shown in [4]. The information in [5] shows the number of planes within the 3D Dataset, the pixel location when hovering through the plane and its value. The buttons [6] below the image [4] allow to scroll through the planes. The list in [7] shows all sequences that are neither the chosen 3D dataset nor a dataset that should be used as a 2D reference slice. Therefore, the list in [8] is used to define all sequences that should be used as 2D reference plane for the reslicing. Between the lists [7] and [8] can be toggled by selecting one or multiple sequences and using the buttons “>” and “<” [9]. The buttons “>>” and “<<” toggle all sequences in either direction.
For the export multiple options are available [10]: In the default case, only the novel resliced data is exported. If in the reslice list [8] CINE images are selected, multiple DICOM data at the same slice position but different phase is given. In order to obtain only one resliced plane instead of multiple replicas, the “reslice only 1” option is necessary. If the original 3D dataset should be exported in addition, the “export 3D” option is necessary. In order to have the non-resliced data from list [7] exported as well, the “export not resliced data” option needs to be checked whereas if both, the original data from the reslice list in [8] as well as the resliced data should be exported, the “export resliced and original data” option is necessary. Consequently, checking all options will export the complete dataset and the novel reformatted data at once.
The slice thickness option [11] defines the slice thickness of the resliced data. Either a fixed manual slice thickness is defined, the slice thickness of the individual reference slices in [8] should be used or the 3D resolution is used. Furthermore, the slice profile that represents the slice thickness [12] must be defined and captures one of the six options: rectangular, triangular, cosine + 1, sinc, standard normal 2 and standard normal 5. Finally, the reslice is performed by clicking on the run button [13].

