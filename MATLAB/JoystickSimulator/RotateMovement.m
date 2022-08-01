function coordsR = RotateMovement(steps, x_radius, y_radius, z_radius, leg, i)
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
coordsR = [];

%% Start coordinates
x_start = 127.5 * cos(offset);
y_start = 127.5 * sin(offset);
z_start = -160.1;

%% Start from apoapsis
if i < 15
    angle = pi/2 - 2 * i * step_angle;
    coordsR = [coordsR; [x_start + x_radius * sin(angle + offset), ...
                         y_start - y_radius * cos(angle + offset), ...
                         z_start + z_radius * sin(angle)]];
%% Straight line - X, Y changes
elseif i < 45
    coordsR = [x_start + (x_radius - (i - 15)*x_radius / (steps / 4)) * sin(offset), ...
                y_start - (y_radius - (i - 15)*y_radius / (steps / 4)) * cos(offset), ...
                z_start];
%% Semi circle in 3D space
else 
    angle = pi - 2 * (i-45) * step_angle;
    coordsR = [coordsR; [x_start + x_radius * sin(angle + offset), ...
                         y_start - y_radius * cos(angle + offset), ...
                         z_start + z_radius * sin(angle)]];
end
end