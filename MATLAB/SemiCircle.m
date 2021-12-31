function coords = SemiCircle(steps, x_radius, y_radius, z_radius)
%% Semi circle parameters
halfsteps = round(steps/2);
step_angle = pi / halfsteps;
coords = [];

%% Straight line - Y changes
for i = 1 : halfsteps
    coords = [coords; [128.9, y_radius - i*y_radius*2/(halfsteps), -125.3]];
end

%% Semi circle in 3D space
for i = 1 : halfsteps
    angle = pi - step_angle*i;
    y = y_radius * cos(angle);
    z = z_radius * sin(angle) - 125.3;
    x = x_radius * sin(angle) + 128.9;
    coords = [coords; [x, y, z]];
end

end