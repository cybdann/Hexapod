function coordsV = VerticalMovement(steps, x_radius, y_radius, z_radius)
% Default position = [161.216, 0, -107]
%% Semi circle parameters
halfsteps = round(steps/2);
step_angle = pi / halfsteps;
coordsV = [];

%% Straight line - Y changes
for i = 1 : halfsteps
    coordsV = [coordsV; [161.216, y_radius - i*y_radius*2/(halfsteps), -107]];
end

%% Semi circle in 3D space
for i = 1 : halfsteps
    angle = pi - step_angle*i;
    y = y_radius * cos(angle);
    z = z_radius * sin(angle) - 107;
    x = x_radius * sin(angle) + 161.216;
    coordsV = [coordsV; [x, y, z]];
end

end