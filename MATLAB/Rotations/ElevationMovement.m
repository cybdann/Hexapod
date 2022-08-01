function coordsE = ElevationMovement(steps, z_radius)
%% Semi circle parameters
halfsteps = round(steps/2);
coordsE = [];

%% Start coordinates
x_start = 0;
y_start = 0;
z_start = 0;

%% Straight line - Z changes
for i = 1 : halfsteps
    coordsE = [coordsE; [x_start, y_start, z_start + z_radius - i*z_radius*2/(halfsteps)]];
end

end