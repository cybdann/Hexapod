clear all;
close all;
clc;
% For end-effector
% Current default position = [128.8, 128.8, 158.6]
% Current default angles = [0, 20.5, 99.5]
% DEPENDENCIES: x-Movement, ExportLegAngles

%% Coordinates for movements
% coordsH = HorizontalMovement(50, 30, 30, "R1");
% coordsV = VerticalMovement(50, 90, 80, 90, "R2");
% coordsDR = DiagonalMovementRight(50, 30, 40, 40, "R1");
% coordsDL = DiagonalMovementLeft(50, 30, 40, 40, "L2");
coordsR = RotateMovement(50, 90, 80, 90, "L2");
% coordsE = ElevationMovement(50, 50, "R2");
%% Calculate angles for joints 
% anglesH = InverseKinematics(coordsH);
% anglesV = InverseKinematics(coordsV);
% anglesDR = InverseKinematics(coordsDR);
% anglesDL = InverseKinematics(coordsDL);
anglesR = InverseKinematics(coordsR);
% anglesE = InverseKinematics(coordsE);
% Calculate points for every joint
% points = ForwardKinematics(angles, zeros(1, size(angles(:, 1), 1)));

%% Draw path
% DrawLegForEndEffector([95, 95, -150], "R2")
% DrawLegDefaultPosition("R2");
% DrawLegsDefaultPosition();
% DrawPath(coordsH, 'Horizontal Movement Path');
% DrawPath(coordsV, 'Vertical Movement Path');
% DrawPath(coordsR, 'Rotate Movement Path');
% DrawLegTrajectory(anglesH, coordsH, 'Horizontal Movement', "R1");
% DrawLegTrajectory(anglesV, coordsV, 'Vertical Movement', "R2");
% DrawLegTrajectory(anglesDR, coordsDR, 'Diagonal Right Movement', "R1");
% DrawLegTrajectory(anglesDL, coordsDL, 'Diagonal Left Movement', "L2");
DrawLegTrajectory(anglesR, coordsR, 'Rotate Movement', "L2");
% DrawLegTrajectory(anglesE, coordsE, 'Elevation Movement', "R2");
% AnimateLegs(anglesH);

