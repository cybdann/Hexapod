clear all;
close all;
clc;

% Default position = [161.216, 0, -107]
% Default angles = [0, 51.4574, 113.9852]

% Coordinates for horizontal movement
coordsV = VerticalMovement(50, 50, 60, 40);
% Coordinates for vertical movement
coordsH = HorizontalMovement(50, 40); 
% Calculate angles for joints
anglesH = InverseKinematics(coordsH);
anglesV = InverseKinematics(coordsV);
% Calculate points for every joint
% points = ForwardKinematics(angles, zeros(1, size(angles(:, 1), 1)));

% DrawLegForEndEffector([161.216, 0, -107])
% DrawLegDefaultPosition();
% DrawLegsDefaultPosition();
% DrawPath(coordsH, 'Horizontal Movement Path');
% DrawPath(coordsV, 'Vertical Movement Path');
DrawLegTrajectory(anglesH, coordsH, 'Horizontal Movement');
% DrawLegTrajectory(anglesV, coordsV, 'Vertical Movement');
% AnimateLegs(anglesH);