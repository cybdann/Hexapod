function DrawPath(coords, t)
    x = coords(:, 1);
    y = coords(:, 2);
    z = coords(:, 3);

    figure('NumberTitle', 'off', 'Name', 'Path');
    plot3(x, y, z);
    title(t);
    grid on;
    xlabel('X');
    ylabel('Y');
    zlabel('Z');    
end