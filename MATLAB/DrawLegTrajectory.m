function DrawLegTrajectory(angles, coords, t, leg)
%% Figure intialization
figure('NumberTitle', 'off', 'Name', 'Leg Trajectory');

x = coords(:, 1);
y = coords(:, 2);
z = coords(:, 3);

P0 = [0, 0, 0, 1];
joint_coords = [];

for i = 1 : size(angles, 1)
    % No leg offset if the angles are already calcualted
    points = ForwardKinematics(angles(i, :), zeros(1, size(angles(i, 1), 1)), "def");
    P1 = points(:, 1);
    P2 = points(:, 2);
    P3 = points(:, 3);
    P4 = points(:, 4);
    
    joint_coords = [joint_coords; P0(1) P0(2) P0(3) P1(1) P1(2) P1(3) P2(1) P2(2) P2(3) P3(1) P3(2) P3(3)];
    
    %% Leg movement
    plot3([P0(1) P1(1)], [P0(2) P1(2)], [P0(3) P1(3)], 'r-', 'LineWidth', 4);

    xlabel('X')
    ylabel('Y')
    zlabel('Z')

    zlim([-200, 150]);
    
    title(t);
    grid on;
    hold on;

    plot3([P1(1) P2(1)], [P1(2) P2(2)], [P1(3) P2(3)], '-b', 'LineWidth', 4);
    plot3([P2(1) P3(1)], [P2(2) P3(2)], [P2(3) P3(3)], '-g', 'LineWidth', 4);
    plot3([P3(1) P4(1)], [P3(2) P4(2)], [P3(3) P4(3)], '-y', 'LineWidth', 4);
    plot3(P4(1), P4(2), P4(3), '*k', 'LineWidth', 4);
    
    %% Joint path
    plot3(joint_coords(:, 1), joint_coords(:, 2), joint_coords(:, 3));
    plot3(joint_coords(:, 4), joint_coords(:, 5), joint_coords(:, 6));
    plot3(joint_coords(:, 7), joint_coords(:, 8), joint_coords(:, 9));
    plot3(joint_coords(:, 10), joint_coords(:, 11), joint_coords(:, 12));
    
    text(P0(1), P0(2), P0(3), 'P0','HorizontalAlignment','left','FontSize',10);
    text(P1(1), P1(2), P1(3), 'P1','HorizontalAlignment','left','FontSize',10);
    text(P2(1), P2(2), P2(3), 'P2','HorizontalAlignment','left','FontSize',10);
    text(P3(1), P3(2), P3(3), 'P3','HorizontalAlignment','left','FontSize',10);
    text(P4(1), P4(2), P4(3), 'P4','HorizontalAlignment','left','FontSize',10);
    
    %% Path
    plot3(x, y, z);
    
    %% Delay
    pause(0.01);
    hold off;
end

answer = menu('Return to default position?', 'Yes', 'No');

if answer == 1
        coordsR = ReturnMovement(size(angles, 1), [P4(1), P4(2), P4(3)], leg);
        angles = InverseKinematics(coordsR);
        
        for i = 1 : size(angles, 1)
            % No leg offset if the angles are already calcualted
            points = ForwardKinematics(angles(i, :), zeros(1, size(angles(i, 1), 1)), "def");
            P1 = points(:, 1);
            P2 = points(:, 2);
            P3 = points(:, 3);
            P4 = points(:, 4);
    
            joint_coords = [joint_coords; P0(1) P0(2) P0(3) P1(1) P1(2) P1(3) P2(1) P2(2) P2(3) P3(1) P3(2) P3(3)];
    
            %% Leg movement
            plot3([P0(1) P1(1)], [P0(2) P1(2)], [P0(3) P1(3)], 'r-', 'LineWidth', 4);

            xlabel('X')
            ylabel('Y')
            zlabel('Z')
            
            zlim([-200, 150]);
    
            title(t);
            grid on;
            hold on;

            plot3([P1(1) P2(1)], [P1(2) P2(2)], [P1(3) P2(3)], '-b', 'LineWidth', 4);
            plot3([P2(1) P3(1)], [P2(2) P3(2)], [P2(3) P3(3)], '-g', 'LineWidth', 4);
            plot3([P3(1) P4(1)], [P3(2) P4(2)], [P3(3) P4(3)], '-y', 'LineWidth', 4);
            plot3(P4(1), P4(2), P4(3), '*k', 'LineWidth', 4);
    
            %% Joint path
            plot3(joint_coords(:, 1), joint_coords(:, 2), joint_coords(:, 3));
            plot3(joint_coords(:, 4), joint_coords(:, 5), joint_coords(:, 6));
            plot3(joint_coords(:, 7), joint_coords(:, 8), joint_coords(:, 9));
            plot3(joint_coords(:, 10), joint_coords(:, 11), joint_coords(:, 12));
    
            text(P0(1), P0(2), P0(3), 'P0','HorizontalAlignment','left','FontSize',10);
            text(P1(1), P1(2), P1(3), 'P1','HorizontalAlignment','left','FontSize',10);
            text(P2(1), P2(2), P2(3), 'P2','HorizontalAlignment','left','FontSize',10);
            text(P3(1), P3(2), P3(3), 'P3','HorizontalAlignment','left','FontSize',10);
            text(P4(1), P4(2), P4(3), 'P4','HorizontalAlignment','left','FontSize',10);
    
            %% Path
            plot3(x, y, z);
            plot3(coords(:, 1), coords(:, 2), coords(:, 3));
    
            %% Delay
            pause(0.01);
            hold off;
        end
end
end