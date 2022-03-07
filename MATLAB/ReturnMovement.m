function coordsR = ReturnMovement(steps, last_pos, leg)
% Values are in mm
% Default angles = [0, 45, 125]
%% Straight line to default position
def_pos = ForwardKinematics([0, 20.5, 99.5, 0], 0, leg);

l = last_pos(1) - def_pos(1, 4);
m = last_pos(2) - def_pos(2, 4);
n = last_pos(3) - def_pos(3, 4);

x_steps = l / steps;
y_steps = m / steps;
z_steps = n / steps;

coordsR = [];
%% Get line coords
for i = 1 : steps
    coordsR = [coordsR; [last_pos(1) - x_steps * i, last_pos(2) - y_steps * i, last_pos(3) - z_steps * i]];
end

end