function points = ForwardKinematics(angles, d, leg)
P0 = [0; 0; 0; 1]; % Starting point

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

%% Get joint angles
theta0 = angles(:, 1);
theta1 = angles(:, 2);
theta2 = angles(:, 3);

%% Model parameters
r1 = 36.13;
d1 = -16.43; %-- real z offset
% d1 = 0;

r2 = 65.982;
% d2 = -12.8 -- real z offset
d2 = 0;

% r3 = 72.981 -- real x offset
% d3 = 5.78 -- real z offset
% To align with End-Effector
r3 = 71.497;
d3 = 0;
% d4 = 97.652; -- real x/z offset
d4 = 96.548;

%% DH Table
% H = Trans_z(d_i) * Rot_z(theta_i) * Trans_x(r_i) * Rot_x(alpha_i)
% Aplha is already calculated here
A1 = @(theta) [cos(deg2rad(theta)) 0 sin(deg2rad(theta)) r1.*cos(deg2rad(theta));
             sin(deg2rad(theta)) 0 -cos(deg2rad(theta)) r1.*sin(deg2rad(theta));
             0 1 0 d1;
             0 0 0 1];
         
A2 = @(theta) [cos(deg2rad(theta)) sin(deg2rad(theta)) 0 r2.*cos(deg2rad(theta));
              sin(deg2rad(theta)) -cos(deg2rad(theta)) 0 r2.*sin(deg2rad(theta));
              0 0 -1 d2;
              0 0 0 1];
          
% -24 is to align the Tarsus servo to align with the End-Effector
% Basically we are disregarding the existence of the piston mechanizm
A3 = @(theta) [cos(deg2rad(theta)) 0 -sin(deg2rad(theta)) r3.*cos(deg2rad(theta));
             sin(deg2rad(theta)) 0 cos(deg2rad(theta)) r3.*sin(deg2rad(theta));
             0 -1 0 d3;
             0 0 0 1];

% From P3 to P4 the you need 2 rotational matrices, this is the simplified version 
A4 = @(d) [1 0 0 d4;
              0 1 0 0;
              0 0 1 d;
              0 0 0 1];

%% Calculate points
points = [];

for i = 1 : size(theta0, 1)
P1 = A1(theta0(i) + offset) * P0;
P2 = A1(theta0(i) + offset) * A2(theta1(i)) * P0;
P3 = A1(theta0(i) + offset) * A2(theta1(i)) * A3(theta2(i)) * P0;
P4 = A1(theta0(i) + offset) * A2(theta1(i)) * A3(theta2(i)) * A4(d(i)) * P0;

points = [points; P1, P2, P3, P4];
end

end
