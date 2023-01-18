function [n,V,p] = affine_fit(X)
% 
% computes a plane that best fits a set of sample points (least square of 
% the normal distance to the plane)
%
% input:  X = n x 3 matrix, each line is a sample point 
% output: n = unit (column) vector normal to the plane
%         V = 3 x 3 matrix; columns of V form an orthonormal basis of the
%             plane
%         p = a point belonging to the plane (mean of the samples)

% 30.08.2013: initial code provided by Adrien Leygue on MATLAB Central - 
%             File Exchange

% mean of the samples (belongs to the plane)
p = mean(X,1);

% reduction of samples
R = bsxfun(@minus,X,p);

% principal directions
[V,D] = eig(R'*R);

% extract the output from the eigenvectors
n = V(:,1);
V = V(:,2:end);

% generate plane
tmp = [];
d = 1;
for k = -d:1:d
for l = -d:1:d

    tmp = p + V(:,1)'.*k + V(:,2)'.*l;
    xd(d+1+k,d+1+l) = tmp(1);
    yd(d+1+k,d+1+l) = tmp(2);
    zd(d+1+k,d+1+l) = tmp(3);
        
end;
end;

hsp = surf(tmp(:,1),tmp(:,2),tmp)
xd = hsp.XData

%demo for affine_fit 
%Author: Adrien Leygue
%Date: December 3 2014
% close all
% clear all
figure;
%generate points that lie approximately in the Z=0 plane
% N = 10;
% [X,Y] = meshgrid(linspace(0,1,N));
% X = [X(:) Y(:) 0.05*randn(N^2,1)];
plot3(X(:,1),X(:,2),X(:,3),'r.');
hold on


X1 = [0; 3];
Y1 = [0; 3];

Z1 = (-n(1).*X1 - n(2).*Y1 + n(1).*p(1) + n(2).*p(2) + n(3).*p(3)) ./ n(3);

[X2,Y2,Z2] = meshgrid(X1,Y1,Z1);


surf(X1,Y1,Z2,'facecolor','red','facealpha',0.5);


%compute the normal to the plane and a point that belongs to the plane
% [n,~,p] = affine_fit(X);
%generate points that lie approximately in the Z=X plane
%the normal vector is
n_2_exact = [-sqrt(2)/2 0 sqrt(2)/2];
% N = 12;
% [X,Y] = meshgrid(linspace(0,1,N));
% XYZ_2 = [X(:) Y(:) X(:)] + bsxfun(@times,0.05*randn(N^2,1),n_2_exact);
% plot3(XYZ_2(:,1),XYZ_2(:,2),XYZ_2(:,3),'b.');
% %compute the normal to the plane and a point that belongs to the plane
[n_2,V_2,p_2] = affine_fit(XYZ_2);
%plot the two points p and p_2
plot3(p(1),p(2),p(3),'ro','markersize',15,'markerfacecolor','red');
% plot3(p_2(1),p_2(2),p_2(3),'bo','markersize',15,'markerfacecolor','blue');
%plot the normal vector
quiver3(p(1),p(2),p(3),n(1)/3,n(2)/3,n(3)/3,'r','linewidth',2)
% h = quiver3(p_2(1),p_2(2),p_2(3),n_2(1)/3,n_2(2)/3,n_2(3)/3,'b','linewidth',2)
%plot the two adjusted planes
[X,Y] = meshgrid(linspace(0,1,3));
%first plane
surf(X,Y, - (n(1)/n(3)*X+n(2)/n(3)*Y-dot(n,p)/n(3)),'facecolor','red','facealpha',0.5);
%second plane
%NB: if the plane is vertical the above method cannot be used, one should
%use the secont output of affine_fit which contains a base of the plane.
%this is illustrated below
%S1 and S2 are the coordinates of the plane points in the basis made of the
%columns ov V_2
[S1,S2] = meshgrid([-1 0 1]);
%generate the pont coordinates
X = p_2(1)+[S1(:) S2(:)]*V_2(1,:)';
Y = p_2(2)+[S1(:) S2(:)]*V_2(2,:)';
Z = p_2(3)+[S1(:) S2(:)]*V_2(3,:)';
%plot the plane
surf(reshape(X,3,3),reshape(Y,3,3),reshape(Z,3,3),'facecolor','blue','facealpha',0.5);
xlabel('x');
ylabel('y');
zlabel('z');
axis equal
%compute the angle between the planes in [0 90] degrees
angle = acosd(dot(n,n_2));
if angle>90
    angle = 180-angle;
end
angle
