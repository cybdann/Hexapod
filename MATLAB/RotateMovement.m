function coordsR = RotateMovement(steps, x_radius, y_radius, z_radius, leg)
% Default position = [95, 95, -115]
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
coordsR = [];

%% Start coordinates
x_start = 95 * cos(deg2rad(offset));
y_start = 95 * sin(deg2rad(offset));
z_start = -150;

% % % Straight line - Y changes
% for i = halfsteps : -1 : 1
%     coordsR = [coordsR; [x_start, y_start + y_radius - i*y_radius*2/(halfsteps), z_start]];
% end

%% Semi circle in 3D spaces
for i = 1 : halfsteps
    angle = pi/2 - step_angle*i;
    coordsR = [coordsR; [x_start + x_radius * cos(angle + deg2rad(offset)), ...
                         y_start + y_radius * sin(angle + deg2rad(offset)), ...
                         z_start + z_radius * cos(angle)]];
end
        
%% Straight line - Y, X changes
l = coordsR(halfsteps, 1) - coordsR(1, 1);
m = coordsR(halfsteps, 2) - coordsR(1, 2);

x_steps = l / halfsteps;
y_steps = m / halfsteps;

for i = 1 : halfsteps
    coordsR = [coordsR; [coordsR(halfsteps, 1) - x_steps * i, ...
                coordsR(halfsteps, 2) - y_steps * i, ...
                z_start]];
end

% Start from apoapsis
coordsR = [coordsR(ceil(halfsteps/2) : halfsteps, :);
            coordsR(halfsteps + 1: 2 * halfsteps, :);
            coordsR(1 : ceil(halfsteps/2) - 1, :)];
end