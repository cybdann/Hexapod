function coordsH = HorizontalMovement(steps, x_radius, z_radius, leg)
% Values are in radians and mm
% Default position = [128.8, 128.8, -158.6]
%% Calculate for given leg
if leg == "R1"
    offset = 45;
elseif leg == "R2"
    offset = 0;
elseif leg == "R3"
    offset = -45;
elseif leg == "L1"
    offset = 135;
elseif leg == "L2"
    offset = 180;
elseif leg == "L3"
    offset = 225;
else
    offset = 0;
end

%% Semi circle parameters
halfsteps = round(steps/2);
step_angle = pi / halfsteps;
coordsH = [];

%% Start coordinates
x_start = 127.5 * cos(deg2rad(offset));
y_start = 127.5 * sin(deg2rad(offset));
z_start = -160.1;

%% Straight line - X changes
for i = 1 : halfsteps
    coordsH = [coordsH; [x_start + x_radius - i*x_radius*2/(halfsteps), y_start, z_start]];
end

%% Semi circle in 3D space
for i = 1 : halfsteps
    angle = pi - step_angle*i;
    x = x_radius * cos(angle) + x_start;
    z = z_radius * sin(angle) + z_start;
    
    coordsH = [coordsH; [x, y_start, z]];
end

% Start from apoapsis
coordsH = [coordsH(2 * halfsteps - ceil(halfsteps/2) : 2 * halfsteps, :);
            coordsH(1: halfsteps, :);           
            coordsH(halfsteps + 1: 2 * halfsteps - ceil(halfsteps/2) - 1, :)];
end