function DrawLegs()
%% Get legs' points for default leg position
L1 = ForwardKinematics([30, 45, 90, 0], 0);
L2 = ForwardKinematics([0, 45, 90, 0], 0);
L3 = ForwardKinematics([-30, 45, 90, 0], 0);
R1 = ForwardKinematics([150, 45, 90, 0], 0);
R2 = ForwardKinematics([180, 45, 90, 0], 0);
R3 = ForwardKinematics([210, 45, 90, 0], 0);

%% Draw legs
figure('NumberTitle', 'off', 'Name', 'Legs Default Position');

legs = {R1, L1, R2, L2, R3, L3};
titles = ["R1", "L1", "R2", "L2", "R3", "L3"];

for i = 1 : 6
     subplot(3, 2, i);
     
     leg = cell2mat(legs(i));
     
     for j = 2 : 4
        P1 = leg(:, j-1);
        P2 = leg(:, j);
        
        plot3([P1(1) P2(1)], [P1(2) P2(2)], [P1(3) P2(3)]);
        grid on;
        hold on;
        xlabel('X')
        ylabel('Y')
        zlabel('Z')
     end
     view(0, 0);    
     title(titles(i));
end

end