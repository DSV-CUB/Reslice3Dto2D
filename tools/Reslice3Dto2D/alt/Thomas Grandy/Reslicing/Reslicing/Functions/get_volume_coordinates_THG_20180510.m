function [X,Y,Z] = get_volume_coordinates_THG_20180510(data,info)

position       = info.DicomInfo.ImagePositionPatient;
orientation    = info.DicomInfo.ImageOrientationPatient;
resolution     = info.DicomInfo.PixelSpacing;

% x axis
x_axis = [0:size(data,2)-1] .* resolution(1) + position(1);

% y axis
y_axis = [0:size(data,1)-1] .* resolution(2) + position(2);

% z axis
z_axis = [0:size(data,3)-1] .* 1.25 + position(3);

% generate grid with world coordinates
[X,Y,Z] = meshgrid(x_axis,y_axis,z_axis);


