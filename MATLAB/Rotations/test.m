clear all;
close all;
clc;
% For body
% Current default position = [0, 0, 0]
% Current default angles = [0, 20.5, 100.15]
% DEPENDENCIES: x-Movement, ExportLegAngles

leg = "R2";

coordsE = ElevationMovement(60, 50);
anglesE = InverseKinematics(coordsE, leg);

coordsR = RollRotation(60, 30, 30);
anglesR = InverseKinematics(coordsR, leg);

DrawLegTrajectory(anglesR, coordsR, "X Movement", leg);

% for i = 1 : 25
%     points = ForwardKinematicsToBody(anglesE(i, :), [coordsE(i, :), 1]', 0, "R2");
%     points(:, 1)
% end
% points = ForwardKinematics(anglesE(12, :), 0, "R2");