clear all;
close all;
clc;
% For end-effector
% Current default position = [128.8, 128.8, -158.6]
% Current default angles = [0, 20.5, 99.5]
% DEPENDENCIES: x-Movement, ExportLegAngles

%% Coordinates for movements
% coordsRoll = RollRotation(50, 40, 40, "L3");
% coordsP = PitchRotation(50, 40, 40, "L3");
coordsY = YawRotation(50, 40, 40, "R2");
%% Calculate angles for joints 
% anglesRoll = InverseKinematics(coordsRoll);
% anglesP = InverseKinematics(coordsP);
anglesY = InverseKinematics(coordsY);

%% Draw path
% DrawLegTrajectory(anglesRoll, coordsRoll, 'Roll Rotation', "L3");
% DrawLegTrajectory(anglesP, coordsP, 'Pitch Rotation', "L3");
% DrawLegTrajectory(anglesY, coordsY, 'Yaw Rotation', "R2");
DrawPath(coordsY, "Yaw");