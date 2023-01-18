function out = spline_interpolation_3D_THG_20181019(data,scaling_factor)

% 3D spline interpolation with defined integer scaling factor
%
% THG 19.10.2018

% prepare meshgrid
dim = size(data);
[Xq,Yq,Zq] = meshgrid(1/scaling_factor:1/scaling_factor:dim(1),1/scaling_factor:1/scaling_factor:dim(2),1/scaling_factor:1/scaling_factor:dim(3));

% interpolate data
out = interp3(data,Xq,Yq,Zq,'spline');

% replace negative values and values above maximal value in original data
out(out<0) = 0;
out(out>max(max(max(data)))) = max(max(max(data)));