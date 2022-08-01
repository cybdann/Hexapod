function DrawLegDefaultPosition(leg)
% Default angles = [0, 45, 125]
%% Get legs points for default leg position
leg = ForwardKinematicsToBase([0, 45, 125], 0, leg);

P0 = [128.8, 0, -158.6, 1];
P1 = leg(:, 1);
P2 = leg(:, 2);
P3 = leg(:, 3);
P4 = leg(:, 4);
%% Draw legs
figure('NumberTitle', 'off', 'Name', 'Leg Default Position');
plot3([P0(1) P1(1)], [P0(2) P1(2)], [P0(3) P1(3)], 'r-', 'LineWidth', 4);


xlabel('X')
ylabel('Y')
zlabel('Z')

zlim([-200, 150]);

grid on;
hold on;

plot3([P1(1) P2(1)], [P1(2) P2(2)], [P1(3) P2(3)], '-b', 'LineWidth', 4);
plot3([P2(1) P3(1)], [P2(2) P3(2)], [P2(3) P3(3)], '-g', 'LineWidth', 4);
plot3([P3(1) P4(1)], [P3(2) P4(2)], [P3(3) P4(3)], '-y', 'LineWidth', 4);
plot3(P0(1), P0(2), P0(3), '*k', 'LineWidth', 4);

end