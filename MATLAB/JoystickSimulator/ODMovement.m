function coordsOD = ODMovement(steps, x_radius, y_radius, z_radius, rot_angle, leg, i)
% Values are in radians and mm
% Default position = [128.8, 128.8, -158.6]
%% Calculate for given leg
if leg == "R1"
    offset = pi/4;
elseif leg == "R2"
    offset = 0;
elseif leg == "R3"
    offset = -pi/4;
elseif leg == "L1"
    offset = 3*pi/4;
elseif leg == "L2"
    offset = pi;
elseif leg == "L3"
    offset = 5*pi/4;
else
    offset = 0;
end

%% Semi circle parameters
step_angle = pi / steps;
coordsOD = [];

%% Start coordinates
x_start = 127.5 * cos(offset);
y_start = 127.5 * sin(offset);
z_start = -160.1;

%% Start from apoapsis
if i < 15
    angle = pi/2 - 2 * i * step_angle;
    x = x_start + i * x_radius / (steps / 4) * cos(rot_angle);
    y = y_start + i * y_radius / (steps / 4) * sin(rot_angle);
    z = z_radius * sin(angle) + z_start;
    
    coordsOD = [x, y, z];
%% Straight line - X, Y changes
elseif i < 45
    coordsOD = [x_start + (x_radius - (i - 15)*x_radius / (steps / 4)) * cos(rot_angle), ...
                y_start + (y_radius - (i - 15)*y_radius / (steps / 4)) * sin(rot_angle), ...
                z_start];
%% Semi circle in 3D space
else 
    angle = pi - 2 * (i-45) * step_angle;
    x = x_start - (x_radius - (i - 45)*x_radius / (steps / 4)) * cos(rot_angle);
    y = y_start - (y_radius - (i - 45)*y_radius / (steps / 4)) * sin(rot_angle);
    z = z_radius * sin(angle) + z_start;
    
    coordsOD = [x, y, z];
end
end