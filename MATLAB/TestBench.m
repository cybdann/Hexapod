clear all;
close all;
clc;

% Coordinates for leg locomotion
coords = SemiCircle(50, 92.73, 50, 50);
% Calculate angles for joints
angles = InverseKinematics(coords);
% Calculate points for every joint
points = ForwardKinematics(angles, zeros(1, size(angles(:, 1), 1)));

% DrawLegs();
% DrawPath(coords);
% AnimateLegs();