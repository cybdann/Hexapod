function coordsV = VerticalMovement(steps, x_radius, y_radius, z_radius, leg)
% Default position = [161.216, 0, -107]
%% Calculate for given leg
if leg == "L1"
    offset = 45;
elseif leg == "L2"
    offset = 0;
elseif leg == "L3"
    offset = -45;
elseif leg == "R1"
    offset = 135;
elseif leg == "R2"
    offset = 180;
elseif leg == "R3"
    offset = 225;
else
    offset = 0;
end

%% Semi circle parameters
halfsteps = round(steps/2);
step_angle = pi / halfsteps;
coordsV = [];

%% Start coordinates
x_start = 161.216 * cos(deg2rad(offset));
y_start = 161.216 * sin(deg2rad(offset));
z_start = -107;

%% Straight line - Y changes
for i = 1 : halfsteps
    coordsV = [coordsV; [x_start, y_start + y_radius - i*y_radius*2/(halfsteps), z_start]];
end

%% Semi circle in 3D space
for i = 1 : halfsteps
    angle = pi - step_angle*i;
    y = y_radius * cos(angle) + y_start;
    z = z_radius * sin(angle) + z_start;
    % Sign function for robot side determination
    x = x_radius * sign(cos(deg2rad(offset))) * sin(angle) + x_start;
    coordsV = [coordsV; [x, y, z]];
end

end