
function coordinates = get_slice_coordinates_and_change_resolution_THG_20180525(data,info,scaling_factor)    

position       = info.DicomInfo.ImagePositionPatient;
orientation    = info.DicomInfo.ImageOrientationPatient;
resolution     = info.DicomInfo.PixelSpacing;

% generate M matrix
v1 = [orientation(1:3)*resolution(1); 0]; 
v2 = [orientation(4:6)*resolution(2); 0];
v3 = zeros(4,1);
v4 = [position(1); position(2); position(3); 1];
M  = [v1 v2 v3 v4]; clearvars v*

% x axis pixel positions
index_x = [0:scaling_factor:size(data,1)-1];

% y axis pixel positions
index_y = [0:scaling_factor:size(data,2)-1];

% initialize coordinates
coordinates = zeros(size(data,2),size(data,1),4);
for i = 1:length(index_y)
    for j = 1:length(index_x)
        coordinates(i,j,:) = M*[index_y(i); index_x(j); 0; 1];
    end
end; clearvars i j