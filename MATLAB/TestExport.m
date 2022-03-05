clear all;
close all;
clc;
%% Export angles for horizontal movement
coordsR1H = HorizontalMovement(50, 30, 30, "R1");
coordsR2H = HorizontalMovement(50, 30, 30, "R2");
coordsR3H = HorizontalMovement(50, 30, 30, "R3");

coordsL1H = HorizontalMovement(50, 30, 30, "L1");
coordsL2H = HorizontalMovement(50, 30, 30, "L2");
coordsL3H = HorizontalMovement(50, 30, 30, "L3");

anglesR1H = InverseKinematics(coordsR1H);
anglesR2H = InverseKinematics(coordsR2H);
anglesR3H = InverseKinematics(coordsR3H);

anglesL1H = InverseKinematics(coordsL1H);
anglesL2H = InverseKinematics(coordsL2H);
anglesL3H = InverseKinematics(coordsL3H);

anglesH = [anglesR1H, anglesR2H, anglesR3H, anglesL1H, anglesL2H, anglesL3H];

ExportLegAngles(anglesH, 'HorizontalMovement.txt', "hm");
%% Export angles for vertical movement
coordsR1V = VerticalMovement(50, 90, 80, 90, "R1");
coordsR2V = VerticalMovement(50, 90, 80, 90, "R2");
coordsR3V = VerticalMovement(50, 90, 80, 90, "R3");

coordsL1V = VerticalMovement(50, 90, 80, 90, "L1");
coordsL2V = VerticalMovement(50, 90, 80, 90, "L2");
coordsL3V = VerticalMovement(50, 90, 80, 90, "L3");

anglesR1V = InverseKinematics(coordsR1V);
anglesR2V = InverseKinematics(coordsR2V);
anglesR3V = InverseKinematics(coordsR3V);

anglesL1V = InverseKinematics(coordsL1V);
anglesL2V = InverseKinematics(coordsL2V);
anglesL3V = InverseKinematics(coordsL3V);

anglesV = [anglesR1V, anglesR2V, anglesR3V, anglesL1V, anglesL2V, anglesL3V];

ExportLegAngles(anglesV, 'VerticalMovement.txt', "vm");
%% Export angles for diagonal right movement
coordsR1DR = DiagonalMovementRight(50, 30, 40, 40, "R1");
coordsR2DR = DiagonalMovementRight(50, 30, 40, 40, "R2");
coordsR3DR = DiagonalMovementRight(50, 30, 40, 40, "R3");

coordsL1DR = DiagonalMovementRight(50, 30, 40, 40, "L1");
coordsL2DR = DiagonalMovementRight(50, 30, 40, 40, "L2");
coordsL3DR = DiagonalMovementRight(50, 30, 40, 40, "L3");

anglesR1DR = InverseKinematics(coordsR1DR);
anglesR2DR = InverseKinematics(coordsR2DR);
anglesR3DR = InverseKinematics(coordsR3DR);

anglesL1DR = InverseKinematics(coordsL1DR);
anglesL2DR = InverseKinematics(coordsL2DR);
anglesL3DR = InverseKinematics(coordsL3DR);

anglesDR = [anglesR1DR, anglesR2DR, anglesR3DR, anglesL1DR, anglesL2DR, anglesL3DR];

ExportLegAngles(anglesDR, 'DiagonalMovementRight.txt', "dr");
%% Export angles for diagonal left movement
coordsR1DL = DiagonalMovementLeft(50, 30, 40, 40, "R1");
coordsR2DL = DiagonalMovementLeft(50, 30, 40, 40, "R2");
coordsR3DL = DiagonalMovementLeft(50, 30, 40, 40, "R3");

coordsL1DL = DiagonalMovementLeft(50, 30, 40, 40, "L1");
coordsL2DL = DiagonalMovementLeft(50, 30, 40, 40, "L2");
coordsL3DL = DiagonalMovementLeft(50, 30, 40, 40, "L3");

anglesR1DL = InverseKinematics(coordsR1DL);
anglesR2DL = InverseKinematics(coordsR2DL);
anglesR3DL = InverseKinematics(coordsR3DL);

anglesL1DL = InverseKinematics(coordsL1DL);
anglesL2DL = InverseKinematics(coordsL2DL);
anglesL3DL = InverseKinematics(coordsL3DL);

anglesDL = [anglesR1DL, anglesR2DL, anglesR3DL, anglesL1DL, anglesL2DL, anglesL3DL];

ExportLegAngles(anglesDL, 'DiagonalMovementLeft.txt', "dl");
%% Export angles for rotate movement
coordsR1R = RotateMovement(50, 90, 80, 90, "R1");
coordsR2R = RotateMovement(50, 90, 80, 90, "R2");
coordsR3R = RotateMovement(50, 90, 80, 90, "R3");

coordsL1R = RotateMovement(50, 90, 80, 90, "L1");
coordsL2R = RotateMovement(50, 90, 80, 90, "L2");
coordsL3R = RotateMovement(50, 90, 80, 90, "L3");

anglesR1R = InverseKinematics(coordsR1R);
anglesR2R = InverseKinematics(coordsR2R);
anglesR3R = InverseKinematics(coordsR3R);

anglesL1R = InverseKinematics(coordsL1R);
anglesL2R = InverseKinematics(coordsL2R);
anglesL3R = InverseKinematics(coordsL3R);

anglesR = [anglesR1R, anglesR2R, anglesR3R, anglesL1R, anglesL2R, anglesL3R];

ExportLegAngles(anglesR, 'RotateMovement.txt', "rm");
%% Export angles for elevation movement
coordsR1E = ElevationMovement(50, 50, "R1");
coordsR2E = ElevationMovement(50, 50, "R2");
coordsR3E = ElevationMovement(50, 50, "R3");

coordsL1E = ElevationMovement(50, 50, "L1");
coordsL2E = ElevationMovement(50, 50, "L2");
coordsL3E = ElevationMovement(50, 50, "L3");

anglesR1E = InverseKinematics(coordsR1E);
anglesR2E = InverseKinematics(coordsR2E);
anglesR3E = InverseKinematics(coordsR3E);

anglesL1E = InverseKinematics(coordsL1E);
anglesL2E = InverseKinematics(coordsL2E);
anglesL3E = InverseKinematics(coordsL3E);

anglesE = [anglesR1E, anglesR2E, anglesR3E, anglesL1E, anglesL2E, anglesL3E];

ExportLegAngles(anglesE, 'ElevationMovement.txt', "em");