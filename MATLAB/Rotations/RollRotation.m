function coordsR = RollRotation(steps, x_radius, z_radius)
% Default position = [128.8, 128.8, -158.6]
%% Semi circle parameters
halfsteps = round(steps/2);
step_angle = pi / halfsteps;
coordsR = [];

%% Start coordinates
x_start = 0;
y_start = 0;
z_start = 0;

%% Semi circle in 3D space
for i = 1 : halfsteps
    angle = pi - step_angle*i;
    coordsR = [coordsR; [x_start + x_radius * cos(angle), ...
                         y_start, ...
                         z_start + z_radius * sin(angle) - z_radius]];
end
        
end