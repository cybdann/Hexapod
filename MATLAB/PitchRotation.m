function coordsP = PitchRotation(steps, y_radius, z_radius, leg)
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
coordsP = [];

%% Start coordinates
x_start = 128.8 * cos(deg2rad(offset));
y_start = 128.8 * sin(deg2rad(offset));
z_start = -158.6;

%% Semi circle in 3D space
for i = 1 : halfsteps
    angle = pi - step_angle*i;
    coordsP = [coordsP; [x_start, ...
                         y_start + y_radius * cos(angle), ...
                         z_start + z_radius * sin(angle) - z_radius]];
end
        
% Start from 90 degrees
coordsP = [coordsP(ceil(halfsteps/2) : halfsteps, :); coordsP(1: ceil(halfsteps/2) - 1, :)];
end