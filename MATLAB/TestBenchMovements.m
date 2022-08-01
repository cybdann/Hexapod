clear all;
close all;
clc;
% For end-effector
% Current default position = [127.5, 127.5, -160.1]
% Current default angles = [0, 20.5, 100.15]
% DEPENDENCIES: x-Movement, ExportLegAngles

%% Coordinates for movements
coordsH = HorizontalMovement(50, 30, 30, "R2");
coordsV = VerticalMovement(60, 50, 50, 50, "R2");
% coordsDR = DiagonalMovementRight(50, 30, 40, 40, "R1");
% coordsDL = DiagonalMovementLeft(50, 30, 40, 40, "L2");
% coordsRot = RotateMovement(50, 90, 80, 90, "R2");
coordsE = ElevationMovement(50, 50, "R2");

%% Calculate angles for joints 
anglesH = InverseKinematics(coordsH);
anglesV = InverseKinematics(coordsV);
% anglesDR = InverseKinematics(coordsDR);
% anglesDL = InverseKinematics(coordsDL);
% anglesRot = InverseKinematics(coordsRot);
anglesE = InverseKinematics(coordsE);

%% Draw path
DrawLegTrajectory(anglesH, coordsH, 'Horizontal Movement', "R2");
DrawLegTrajectory(anglesV, coordsV, 'Vertical Movement', "R2");
% DrawLegTrajectory(anglesDR, coordsDR, 'Diagonal Right Movement', "R1");
% DrawLegTrajectory(anglesDL, coordsDL, 'Diagonal Left Movement', "L2");
DrawLegTrajectory(anglesE, coordsE, 'Elevation Change', "R2");
% 
% anglesV(:, 1) = anglesV(:, 1) + 90 - 0;
% anglesV(:, 2) = anglesV(:, 2) + 90 - 20.5;
% anglesV(:, 3) = anglesV(:, 3) + 90 - 100.15;
