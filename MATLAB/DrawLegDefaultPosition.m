function DrawLegDefaultPosition()
% Default angles = [0, 51.4574, 113.9852]
%% Get legs points for default leg position
leg = ForwardKinematics([0, 51.4574, 113.9852, 0], 0);

%% Draw legs
figure('NumberTitle', 'off', 'Name', 'Leg Default Position');

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
end