function coordsH = HorizontalMovement(steps, radius)
% Values are in radians and mm
% Default position = [161.216, 0, -107]
%% Semi circle parameters
halfsteps = round(steps/2);
step_angle = pi / halfsteps;
coordsH = [];

%% Straight line - Y changes
for i = 1 : halfsteps
    coordsH = [coordsH; [161.216, radius - i*radius*2/(halfsteps), -107]];
end

%% Semi circle in 3D space
for i = 1 : halfsteps
    angle = pi - step_angle*i;
    y = radius * cos(angle);
    z = radius * sin(angle) - 107;
    
    coordsH = [coordsH; [161.216, y, z]];
end


%% Rotate path 270 degrees on Z
theta = 270;

for i = 1 : size(coordsH, 1)
   coords = coordsH(i, :)';
   
   coords = [cos(deg2rad(theta)) -sin(deg2rad(theta)) 0;
             sin(deg2rad(theta)) cos(deg2rad(theta)) 0;
             0 0 1] * coords;
   
   coords(1) = coords(1) + 161.216 + radius;
   coords(2) = coords(2) + 161.216;
   coordsH(i, :) = coords';
end
end