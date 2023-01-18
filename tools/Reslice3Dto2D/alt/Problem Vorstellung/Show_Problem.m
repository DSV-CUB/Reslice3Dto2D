figure(1)
hold on

% Settings
num = 10;
a = 0;
b = 1;

% Grid Points
x = 0:num;
y = 0:num;
z = 0:num;
[X, Y, Z] = meshgrid(x, y, z);
x = [X(:); X(:); X(:)];
y = [Y(:); Y(:); Y(:)];
z = [Z(:); Z(:); Z(:)];
scatter3(x,y,z, 1, 'b', '.')

% Surface of interest
num = 0.8 * num;
x = 0.5*num:0.15:num;
y = 0.5*num:0.15:num;
z = 0.5*num:0.15:num;
[X, Y] = meshgrid(x, y);
Z = a * X + b * Y;
x = [X(:); X(:); X(:)];
y = [Y(:); Y(:); Y(:)];
z = [Z(:); Z(:); Z(:)];
% surf(X, Y, Z, 'EdgeColor', 'none', 'FaceAlpha', 0.5, 'FaceColor', 'r')
scatter3(x,y,z, 1, 'r', '.')

% Surface Normal of Interest
x0 = 0.7 * num;
y0 = 0.7 * num;
z0 = a * x0 + b * y0;
x1 = 0.7 * num;
y1 = 0.75 * num;
z1 = a * x1 + b * y1;
x2 = 0.75 * num;
y2 = 0.7 * num;
z2 = a * x2 + b * y2;
v1 = [x1-x0 y1-y0 z1-z0];
v2 = [x2-x0 y2-y0 z2-z0];
n = 10 * cross(v1, v2);
quiver3(x0, y0, z0, v1(1), v1(2), v1(3))
quiver3(x0, y0, z0, v2(1), v2(2), v2(3))
quiver3(x0, y0, z0, n(1), n(2), n(3))

dot(n,v1)
dot(n,v2)
