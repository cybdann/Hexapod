function angles = InverseKinematics(coords)
%% Get coordinates
x = coords(:, 1);
y = coords(:, 2);
z = coords(:, 3);

%% Model parameters
a1 = 36.13;
a2 = 65.98;
a3 = 178.03;

theta_0 = [];
theta_1 = [];
theta_2 = [];

%% Calculate angles
for i = 1 : size(x, 1)
    r1 = sqrt(x(i)^2 + y(i)^2) - a1;
    r2 = z(i);
    r3 = sqrt(r1^2 + r2^2);
    
    phi1 = rad2deg(atan(r2/r1));
    phi2 = rad2deg(acos((a3^2 - a2^2 - r3^2)/(-2 * a2 * r3)));
    phi3 = rad2deg(acos((r3^2 - a2^2 - a3^2)/(-2 * a2 * a3)));
    
    theta_0 = [theta_0, rad2deg(atan(y(i)/x(i)))];
    theta_1 = [theta_1, phi2 + phi1]; 
    theta_2 = [theta_2, 180 - phi3]; 
end

angles = [theta_0', theta_1', theta_2'];
end