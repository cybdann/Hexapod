function points = ForwardKinematicsToBody(angles, d, leg)
PS = [0; 0; 0; 1]; % Starting point

%% Calculate for given leg
if leg == "R1"
    offset = 45;
    r0 = 112.13;
elseif leg == "R2"
    offset = 0;
    r0 = 79.8;
elseif leg == "R3"
    offset = -45;
    r0 = 112.13;
elseif leg == "L1"
    offset = 135;
    r0 = 112.13;
elseif leg == "L2"
    offset = 180;
    r0 = 79.8;
elseif leg == "L3"
    offset = 225;
    r0 = 112.13;
else
    offset = 0;
    r0 = 79.8;
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

% Center of body
A0 =  @(theta) [cos(deg2rad(theta)) 0 0 r0.*cos(deg2rad(theta));
             sin(deg2rad(theta)) 0 0 r0.*sin(deg2rad(theta));
      0 0 1 0;
      0 0 0 1];

A1 = @(theta) [cos(deg2rad(theta)) 0 sin(deg2rad(theta)) r1.*cos(deg2rad(theta));
             sin(deg2rad(theta)) 0 -cos(deg2rad(theta)) r1.*sin(deg2rad(theta));
             0 1 0 d1;
             0 0 0 1];
         
A2 = @(theta) [cos(deg2rad(theta)) sin(deg2rad(theta)) 0 r2.*cos(deg2rad(theta));
              sin(deg2rad(theta)) -cos(deg2rad(theta)) 0 r2.*sin(deg2rad(theta));
              0 0 -1 d2;
              0 0 0 1];
          
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

P0 = A0(offset) * PS;
P1 = A0(offset) * A1(theta0(i)) * PS;
P2 = A0(offset) * A1(theta0(i)) * A2(theta1(i)) * PS;
P3 = A0(offset) * A1(theta0(i)) * A2(theta1(i)) * A3(theta2(i)) * PS;
P4 = A0(offset) * A1(theta0(i)) * A2(theta1(i)) * A3(theta2(i)) * A4(d(i)) * PS;

points = [points; P0, P1, P2, P3, P4];
end

end
