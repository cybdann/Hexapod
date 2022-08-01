clear all;
close all;
clc;
% For end-effector
% Current default position = [128.8, 128.8, -158.6]
% Current default angles = [0, 20.5, 99.5]
% DEPENDENCIES: x-Movement, ExportLegAngles

angles = InverseKinematics([128.8, 0, -158.6]);