function coordsE = ElevationMovement(steps, z_radius, leg)
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
coordsE = [];

%% Start coordinates
x_start = 128.8 * cos(deg2rad(offset));
y_start = 128.8 * sin(deg2rad(offset));
z_start = -158.6;

%% Straight line - Z changes
for i = 1 : halfsteps
    coordsE = [coordsE; [x_start, y_start, z_start + z_radius - i*z_radius*2/(halfsteps)]];
end

end