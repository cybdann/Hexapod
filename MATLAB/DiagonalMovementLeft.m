function coordsD = DiagonalMovementLeft(steps, x_radius, y_radius, z_radius, leg)
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
coordsD = [];

%% Start coordinates
x_start = 128.8 * cos(deg2rad(offset));
y_start = 128.8 * sin(deg2rad(offset));
z_start = -158.6;

%% Diagonal line - X, Y changes
for i = 1 : halfsteps
    coordsD = [coordsD; [x_start + (x_radius - i*x_radius*2/(halfsteps)) * cos(deg2rad(135)), ...
                            y_start + (y_radius - i*y_radius*2/(halfsteps)) * sin(deg2rad(135)),...
                            z_start]];
end

%% Semi circle in 3D space
for i = 1 : halfsteps
    angle = pi - step_angle*i;
    y = coordsD(halfsteps + 1 - i, 2);
    x = coordsD(halfsteps + 1 - i, 1);
    z = z_radius * sin(angle) + z_start;
    
    coordsD = [coordsD; [x, y, z]];
end

% Start from apoapsis
coordsD = [coordsD(2 * halfsteps - ceil(halfsteps/2) : 2 * halfsteps, :);
            coordsD(1: halfsteps, :);           
            coordsD(halfsteps + 1: 2 * halfsteps - ceil(halfsteps/2) - 1, :)];
end