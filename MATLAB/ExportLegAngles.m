function ExportLegAngles(angles, file_name, func_name)
% Current default angles = [0, 20.5, 99.5]
%% Ceil values for Python int format
angles = ceil(angles);

%% Physical offset for given leg
%R1 => COXA offset -45
anglesR1 = angles(:, 1:3) + 90;
anglesR1(:, 1) = anglesR1(:, 1) - 45;
anglesR1(:, 2) = anglesR1(:, 2) - 20.5;
anglesR1(:, 3) = anglesR1(:, 3) - 99.5;

%R2 - point of reference => COXA offset -0
anglesR2 = angles(:, 4:6) + 90;
anglesR2(:, 1) = anglesR2(:, 1) - 0;
anglesR2(:, 2) = anglesR2(:, 2) - 20.5;
anglesR2(:, 3) = anglesR2(:, 3) - 99.5;

%R3 => COXA offset +45
anglesR3 = angles(:, 7:9) + 90;
anglesR3(:, 1) = anglesR3(:, 1) + 45;
anglesR3(:, 2) = anglesR3(:, 2) - 20.5;
anglesR3(:, 3) = anglesR3(:, 3) - 99.5;

%L1
anglesL1 = angles(:, 10:12) - 90;
anglesL1(:, 1) = anglesL1(:, 1) + 45;
anglesL1(:, 2) = 20.5 - anglesL1(:, 2);
anglesL1(:, 3) = 99.5 - anglesL1(:, 3);

%L2
anglesL2 = angles(:, 13:15) - 90;
anglesL2(:, 1) = anglesL2(:, 1) + 0;
anglesL2(:, 2) = 20.5 - anglesL2(:, 2);
anglesL2(:, 3) = 99.5 - anglesL2(:, 3);

%L3
anglesL3 = angles(:, 16:18) - 90;
anglesL3(:, 1) = anglesL3(:, 1) - 45;
anglesL3(:, 2) = 20.5 - anglesL3(:, 2);
anglesL3(:, 3) = 99.5 - anglesL3(:, 3);

%% Python file formating
strR1C = func_name + "_R1C = (";
strR1F = func_name + "_R1F = (";
strR1T = func_name + "_R1T = (";

strR2C = func_name + "_R2C = (";
strR2F = func_name + "_R2F = (";
strR2T = func_name + "_R2T = (";

strR3C = func_name + "_R3C = (";
strR3F = func_name + "_R3F = (";
strR3T = func_name + "_R3T = (";

strL1C = func_name + "_L1C = (";
strL1F = func_name + "_L1F = (";
strL1T = func_name + "_L1T = (";

strL2C = func_name + "_L2C = (";
strL2F = func_name + "_L2F = (";
strL2T = func_name + "_L2T = (";

strL3C = func_name + "_L3C = (";
strL3F = func_name + "_L3F = (";
strL3T = func_name + "_L3T = (";

for i = 1 : size(angles, 1)
    if i == size(angles, 1)
        strR1C = sprintf("%s%d)", strR1C, anglesR1(i, 1));
        strR1F = sprintf("%s%d)", strR1F, anglesR1(i, 2));
        strR1T = sprintf("%s%d)", strR1T, anglesR1(i, 3));
        
        strR2C = sprintf("%s%d)", strR2C, anglesR2(i, 1));
        strR2F = sprintf("%s%d)", strR2F, anglesR2(i, 2));
        strR2T = sprintf("%s%d)", strR2T, anglesR2(i, 3));
        
        strR3C = sprintf("%s%d)", strR3C, anglesR3(i, 1));
        strR3F = sprintf("%s%d)", strR3F, anglesR3(i, 2));
        strR3T = sprintf("%s%d)", strR3T, anglesR3(i, 3));
        
        strL1C = sprintf("%s%d)", strL1C, anglesL1(i, 1));
        strL1F = sprintf("%s%d)", strL1F, anglesL1(i, 2));
        strL1T = sprintf("%s%d)", strL1T, anglesL1(i, 3));
        
        strL2C = sprintf("%s%d)", strL2C, anglesL2(i, 1));
        strL2F = sprintf("%s%d)", strL2F, anglesL2(i, 2));
        strL2T = sprintf("%s%d)", strL2T, anglesL2(i, 3));
        
        strL3C = sprintf("%s%d)", strL3C, anglesL3(i, 1));
        strL3F = sprintf("%s%d)", strL3F, anglesL3(i, 2));
        strL3T = sprintf("%s%d)", strL3T, anglesL3(i, 3));
    else
        strR1C = sprintf("%s%d, ", strR1C, anglesR1(i, 1));
        strR1F = sprintf("%s%d, ", strR1F, anglesR1(i, 2));
        strR1T = sprintf("%s%d, ", strR1T, anglesR1(i, 3));
        
        strR2C = sprintf("%s%d, ", strR2C, anglesR2(i, 1));
        strR2F = sprintf("%s%d, ", strR2F, anglesR2(i, 2));
        strR2T = sprintf("%s%d, ", strR2T, anglesR2(i, 3));
        
        strR3C = sprintf("%s%d, ", strR3C, anglesR3(i, 1));
        strR3F = sprintf("%s%d, ", strR3F, anglesR3(i, 2));
        strR3T = sprintf("%s%d, ", strR3T, anglesR3(i, 3));
        
        strL1C = sprintf("%s%d, ", strL1C, anglesL1(i, 1));
        strL1F = sprintf("%s%d, ", strL1F, anglesL1(i, 2));
        strL1T = sprintf("%s%d, ", strL1T, anglesL1(i, 3));
        
        strL2C = sprintf("%s%d, ", strL2C, anglesL2(i, 1));
        strL2F = sprintf("%s%d, ", strL2F, anglesL2(i, 2));
        strL2T = sprintf("%s%d, ", strL2T, anglesL2(i, 3));
        
        strL3C = sprintf("%s%d, ", strL3C, anglesL3(i, 1));
        strL3F = sprintf("%s%d, ", strL3F, anglesL3(i, 2));
        strL3T = sprintf("%s%d, ", strL3T, anglesL3(i, 3));
    end
end

R1 = sprintf("%s\n%s\n%s\n", strR1C, strR1F, strR1T);
R2 = sprintf("%s\n%s\n%s\n", strR2C, strR2F, strR2T);
R3 = sprintf("%s\n%s\n%s\n", strR3C, strR3F, strR3T);

L1 = sprintf("%s\n%s\n%s\n", strL1C, strL1F, strL1T);
L2 = sprintf("%s\n%s\n%s\n", strL2C, strL2F, strL2T);
L3 = sprintf("%s\n%s\n%s\n", strL3C, strL3F, strL3T);

all_legs = sprintf("%s\n%s\n%s\n%s\n%s\n%s\n", R1, R2, R3, L1, L2, L3);

file = fopen("angles/" + file_name, 'w');
fprintf(file, all_legs);
end