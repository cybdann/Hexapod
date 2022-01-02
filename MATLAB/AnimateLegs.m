function AnimateLegs(angles)
%% Get angles from generated path
theta0 = angles(:, 1);
theta1 = angles(:, 2);
theta2 = angles(:, 3);
d = zeros(1, size(angles(:, 1), 1));

%% Calculate leg poisitions
L1 = ForwardKinematics([(theta0 + 30), theta1, theta2], d);
L2 = ForwardKinematics([theta0, theta1, theta2], d);
L3 = ForwardKinematics([(theta0 - 30), theta1, theta2], d);
R1 = ForwardKinematics([(theta0 + 150), theta1, theta2], d);
R2 = ForwardKinematics([(theta0 + 180), theta1, theta2], d);
R3 = ForwardKinematics([(theta0 + 210), theta1, theta2], d);

%% Animate legs
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

cycle1 = {R1, L2, R3};
cycle2 = {L1, R2, L3};

titles1 = ["R1", "L2", "R3"];
titles2 = ["L1", "R2", "L3"];

ax1 = subplot(3, 2, 1);
ax2 = subplot(3, 2, 2);
ax3 = subplot(3, 2, 3);
ax4 = subplot(3, 2, 4);
ax5 = subplot(3, 2, 5);
ax6 = subplot(3, 2, 6);

frames1 = [ax1, ax4, ax5];
frames2 = [ax2, ax3, ax6];

subplts1 = [1, 4, 5];
subplts2 = [2, 3, 6];

for full_cycle = 1 : 10
    
    for p = 1 : 4 : size(R1, 1)
        
        for i = 1 : 3
            leg = cell2mat(cycle1(i));
            
            for j = 2 : 4
                P1 = leg(p : p+3, j-1);
                P2 = leg(p : p+3, j);
                
                subplot(3, 2, subplts1(i));
                plot3([P1(1) P2(1)], [P1(2) P2(2)], [P1(3) P2(3)]);
                
                if rem(i, 2) == 0
                    xlim([0, 200]);
                else
                    xlim([-200, 0]);
                end
                ylim([-150, 100]);
                zlim([-150, 80]);
                
                xlabel('X')
                ylabel('Y')
                zlabel('Z')
                
                title(titles1(i));
                grid on;
                
                hold(frames1(i), 'on');
              
            end
            hold(frames1(i), 'off');
            
            view(0, 0);
            pause(0.001);
        end
        
    end
    
    for p = 1 : 4 : size(R2, 1)
        
        for i = 1 : 3
            leg = cell2mat(cycle2(i));
            
            for j = 2 : 4
                P1 = leg(p : p+3, j-1);
                P2 = leg(p : p+3, j);
                
                subplot(3, 2, subplts2(i));
                plot3([P1(1) P2(1)], [P1(2) P2(2)], [P1(3) P2(3)]);
                
                if rem(i, 2) == 0
                    xlim([0, 200]);
                else
                    xlim([-200, 0]);
                end
                ylim([-150, 100]);
                zlim([-150, 80]);
                
                xlabel('X')
                ylabel('Y')
                zlabel('Z')
                
                title(titles2(i));
                grid on;
                
                hold(frames2(i), 'on');
              
            end
            hold(frames2(i), 'off');
            
            view(0, 0);
            pause(0.001);
        end
        
    end
end
end