function DrawLegTrajectory(angles, coords, t, leg)
global ee_path;
global slider_x;
global slider_y;
global slider_view;

x = coords(1);
y = coords(2);
z = coords(3);

P0 = [0, 0, 0, 1];

for i = 1 : size(angles, 1)
    %% No leg offset if the angles are already calcualted
    points = ForwardKinematics(rad2deg(angles(i, :)), zeros(1, size(angles(i, 1), 1)), "def");
    P1 = points(:, 1);
    P2 = points(:, 2);
    P3 = points(:, 3);
    P4 = points(:, 4);
    ee_path = [ee_path; P4(1) P4(2) P4(3)];
    
    %% Leg movement
    plot3([P0(1) P1(1)], [P0(2) P1(2)], [P0(3) P1(3)], 'r-', 'LineWidth', 4);

    xlabel('X')
    ylabel('Y')
    zlabel('Z')
    
    if leg == "R2"
        xlim([0, 200]);
        ylim([-100, 100]);
    elseif leg == "R1"
        xlim([-50, 150]);
        ylim([-50, 150]);
    elseif leg == "R3"
        xlim([-50, 150]);
        ylim([-150, 50]);
    elseif leg == "L2"
        xlim([-200, 0]);
        ylim([-100, 100]);
    elseif leg == "L1"
        xlim([-250, 50]);
        ylim([0, 200]);
    elseif leg == "L3"
        xlim([-250, 50]);
        ylim([-200, 0]);
    end
    
    zlim([-200, 150]);
    view(slider_view, 30);
    
    title(t);
    grid on;
    hold on;

    plot3([P1(1) P2(1)], [P1(2) P2(2)], [P1(3) P2(3)], '-b', 'LineWidth', 4);
    plot3([P2(1) P3(1)], [P2(2) P3(2)], [P2(3) P3(3)], '-g', 'LineWidth', 4);
    plot3([P3(1) P4(1)], [P3(2) P4(2)], [P3(3) P4(3)], '-y', 'LineWidth', 4);
    plot3(P4(1), P4(2), P4(3), '*k', 'LineWidth', 4);
    
    plot3(ee_path(:, 1), ee_path(:, 2), ee_path(:, 3));
    
    text(P0(1), P0(2), P0(3), 'P0','HorizontalAlignment','left','FontSize',10);
    text(P1(1), P1(2), P1(3), 'P1','HorizontalAlignment','left','FontSize',10);
    text(P2(1), P2(2), P2(3), 'P2','HorizontalAlignment','left','FontSize',10);
    text(P3(1), P3(2), P3(3), 'P3','HorizontalAlignment','left','FontSize',10);
    text(P4(1), P4(2), P4(3), 'P4','HorizontalAlignment','left','FontSize',10);
    
    %% EE Path
    plot3(x, y, z);
    
    delay = 2 - max(abs(slider_x), abs(slider_y));
    pause(delay * 10^-2);
    hold off;
end
end