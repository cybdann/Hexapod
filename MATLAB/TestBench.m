clear all;
close all;
clc;
% For end-effector
% Current default position = [95, 95, -150]
% Current default angles = [0, 25, 115]
% DEPENDENCIES: x-Movement, ExportLegAngles

%% Coordinates for movements
% coordsH = HorizontalMovement(50, 30, 30, "R1");
% coordsV = VerticalMovement(50, 90, 80, 90, "R2");
% coordsDR = DiagonalMovementRight(50, 30, 40, 40, "R1");
% coordsDL = DiagonalMovementLeft(50, 30, 40, 40, "L2");
% coordsR = RotateMovement(50, 90, 80, 90, "R2");
% coordsE = ElevationMovement(50, 50, "R2");
%% Calculate angles for joints 
% anglesH = InverseKinematics(coordsH);
% anglesV = InverseKinematics(coordsV);
% anglesDR = InverseKinematics(coordsDR);
% anglesDL = InverseKinematics(coordsDL);
% anglesR = InverseKinematics(coordsR);
% anglesE = InverseKinematics(coordsE);
% Calculate points for every joint
% points = ForwardKinematics(angles, zeros(1, size(angles(:, 1), 1)));

%% Draw path
% DrawLegForEndEffector([161.216, 0, -107], "L1")
% DrawLegDefaultPosition("L1");
% DrawLegsDefaultPosition();
% DrawPath(coordsH, 'Horizontal Movement Path');
% DrawPath(coordsV, 'Vertical Movement Path');
% DrawPath(coordsR, 'Rotate Movement Path');
% DrawLegTrajectory(anglesH, coordsH, 'Horizontal Movement', "R1");
% DrawLegTrajectory(anglesV, coordsV, 'Vertical Movement', "R2");
% DrawLegTrajectory(anglesDR, coordsDR, 'Diagonal Right Movement', "R1");
% DrawLegTrajectory(anglesDL, coordsDL, 'Diagonal Left Movement', "L2");
% DrawLegTrajectory(anglesR, coordsR, 'Rotate Movement', "R2");
% DrawLegTrajectory(anglesE, coordsE, 'Elevation Movement', "R2");
% AnimateLegs(anglesH);

