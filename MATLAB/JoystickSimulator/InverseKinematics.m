function angles = InverseKinematics(coords)
% Values are in radians and mm
%% Get coordinates
x = coords(:, 1);
y = coords(:, 2);
z = coords(:, 3);

%% Model parameters
d1 = -16.43;
a1 = 36.13;
a2 = 65.982;
a3 = 168.045;

theta_0 = [];
theta_1 = [];
theta_2 = [];

%% Calculate angles
for i = 1 : size(x, 1)
    r1 = sqrt(x(i)^2 + y(i)^2);
    r2 = z(i);
    r3 = sqrt((r2 - d1)^2 + (r1 - a1)^2);
    
    phi1 = atan((r2 - d1)/(r1 - a1));
    phi2 = acos((a3^2 - a2^2 - r3^2)/(-2 * a2 * r3));
    phi3 = acos((r3^2 - a2^2 - a3^2)/(-2 * a2 * a3));
    
    if x(i) < 0
        theta_0 = [theta_0, pi + atan(y(i)/x(i))];
    else
        theta_0 = [theta_0, atan(y(i)/x(i))];
    end 
    
    theta_1 = [theta_1, phi2 + phi1]; 
    theta_2 = [theta_2, pi - phi3]; 
end

angles = [theta_0', theta_1', theta_2'];
end