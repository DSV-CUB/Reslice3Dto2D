function out = spline_interpolation_THG_20180516(data,scaling_factor)

% in-plane spline interpolation with defined integer scaling factor
%
% THG 16.05.2018

dim = size(data);

% 2D matrix
if length(dim) == 2

    [Xq,Yq] = meshgrid(1/scaling_factor:1/scaling_factor:dim(2),1/scaling_factor:1/scaling_factor:dim(1));
    out     = interp2(data,Xq,Yq,'spline');

% 3D matrix (assuming images are in x-y dimensions)
elseif length(dim) == 3
    
    out     = zeros(dim(1)*scaling_factor,dim(2)*scaling_factor,dim(3));
    [Xq,Yq] = meshgrid(1/scaling_factor:1/scaling_factor:dim(2),1/scaling_factor:1/scaling_factor:dim(1));
    
    for j = 1:dim(3)
        
        out(:,:,j) = interp2(squeeze(data(:,:,j)),Xq,Yq,'spline');
        
    end
    
end

% replace negative values and values above maximal value in original data
out(out<0) = 0;
out(out>max(max(max(data)))) = max(max(max(data)));