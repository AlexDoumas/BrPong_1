import numpy as np


def dim_comparator(val1, val2, name1, name2, dim_string, tolerance=0):
    """
    Get the string representation of the relations.

    Args:
        val1: dimensional value of object 1 (int).
        val2: dimensional value of object 2 (int).
        name1: name of object 1 (str).
        name2: name of object 2 (str).
        dim_string: dimension being compared (str).
        tolerance: level of tolerance for the comparator (int).

    Return:
        A string representing the correct comparative relation between the objects
        in the dimension.

    """
    diff = val1 - val2

    if abs(diff) <= tolerance:  # val1 == val2
        return 's_' + dim_string + '(' + str(name1) + ',' + str(name2) + ')'
    elif diff > tolerance:   # val1 > val2
        return 'm_' + dim_string + '(' + str(name1) + ',' + str(name2) + ')'
    elif diff < -tolerance:   # val1 < val2
        return 'l_' + dim_string + '(' + str(name1) + ',' + str(name2) + ')'


def relational_states_breakout(f_vec1, f_vec2=None):
    """
    Builds a relational description of the breakout screen. When there is only
    a single screen available (1st time step) the description doesn't include
    relations across time.

    Args:
        f_vec1: vector with positional info of screen 1: x_placeholder,
            y_placeholder, x_ball, y_ball, x_paddle, y_paddle.
        f_vec2: same for screen 2.

    Returns:
        A string representing the relational description.
    """

    # Check if ball is present
    ball_present = False if np.all(f_vec2[2:4] == 0) else True
    # Paddle is always present, change to an actual check later
    # paddle_present = True

    # Append every relation to a list and generate the comparatives across objects only if there is a ball
    relations = []

    # Presence ball
    ball_presence = 'b_pre' if ball_present else 'b_abs'
    relations.append(ball_presence)

    # XY coordinates
    # Ball, time 1
    ball1_x = f_vec1[2]
    ball1_y = 210 - f_vec1[3]  # invert OpenCv y-coordinate

    # Paddle, time 1
    paddle1_x = f_vec1[4]
    paddle1_y = 210 - f_vec1[5]  # invert OpenCv y-coordinate

    # Calculate relations across time only if there is a second screen
    if f_vec2 is not None:
        # XY coordinates
        # Ball, time 2
        ball2_x = f_vec2[2]
        ball2_y = 210 - f_vec2[3]  # invert OpenCv y-coordinate

        # Paddle, time 2
        paddle2_x = f_vec2[4]
        paddle2_y = 210 - f_vec2[5]  # invert OpenCv y-coordinate

        # Calculate trajectories in x and y as relations between position in objects across time
        trajx_paddle = dim_comparator(paddle2_x, paddle1_x, 'p2', 'p1', 'trajx')
        relations.append(trajx_paddle)

        trajy_paddle = dim_comparator(paddle2_y, paddle1_y, 'p2', 'p1', 'trajy')
        relations.append(trajy_paddle)

        # Calculate trajectory for ball only if there is a ball in the first screen
        if ball_present:
            trajx_ball = dim_comparator(ball2_x, ball1_x, 'b2', 'b1', 'trajx')
            relations.append(trajx_ball)

            trajy_ball = dim_comparator(ball2_y, ball1_y, 'b2', 'b1', 'trajy')
            relations.append(trajy_ball)

        # Object relations (only available if there is a ball)
        if ball_present:
            x = dim_comparator(ball2_x, paddle2_x, 'b', 'p', 'x')
            relations.append(x)

            y = dim_comparator(ball2_y, paddle2_y, 'b', 'p', 'y')
            relations.append(y)

    # Build relational state
    relations.sort()
    rel_state = ' AND '.join(relations)

    return rel_state


def relational_states_breakout_vec(f_vec1, f_vec2=None):
    """
    Builds a relational description of the breakout screen. When there is only
    a single screen available (1st time step) the description doesn't include
    relations across time.

    Args:
        f_vec1: vector with positional info of screen 1: x_placeholder,
            y_placeholder, x_ball, y_ball, x_paddle, y_paddle.
        f_vec2: same for screen 2.

    Returns:
        A vector (np.array) representing the relational description.
        vector info ordering:

            rel_vec[0]: presence_ball

            rel_vec[1]: l_x(p2, p1)
            rel_vec[2]: s_x(p2, p1)
            rel_vec[3]: m_x(p2, p1)

            rel_vec[4]: l_y(p2, p1)
            rel_vec[5]: s_y(p2, p1)
            rel_vec[6]: m_y(p2, p1)

            rel_vec[7]: l_x(b2, b1)
            rel_vec[8]: s_x(b2, b1)
            rel_vec[9]: m_x(b2, b1)

            rel_vec[10]: l_y(b2, b1)
            rel_vec[11]: s_y(b2, b1)
            rel_vec[12]: m_y(b2, b1)

            rel_vec[13]: l_x(b, p)
            rel_vec[14]: s_x(b, p)
            rel_vec[15]: m_x(b, p)

            rel_vec[16]: l_y(b, p)
            rel_vec[17]: s_y(b, p)
            rel_vec[18]: m_y(b, p)
    """

    # Initialize output vector with zeros
    rel_vec = np.zeros(19)

    # Check if ball is present
    ball_present = False if np.all(f_vec2[2:4] == 0) else True
    # Write to vec
    if ball_present:
        rel_vec[0] = 1

    # XY coordinates
    # Ball, time 1
    ball1_x = f_vec1[2]
    ball1_y = 210 - f_vec1[3]  # invert OpenCv y-coordinate

    # Paddle, time 1
    paddle1_x = f_vec1[4]
    paddle1_y = 210 - f_vec1[5]  # invert OpenCv y-coordinate

    # Calculate relations across time only if there is a second screen
    if f_vec2 is not None:
        # XY coordinates
        # Ball, time 2
        ball2_x = f_vec2[2]
        ball2_y = 210 - f_vec2[3]  # invert OpenCv y-coordinate

        # Paddle, time 2
        paddle2_x = f_vec2[4]
        paddle2_y = 210 - f_vec2[5]  # invert OpenCv y-coordinate

        # Calculate trajectories in x as relations between position in objects across time
        trajx_paddle = dim_comparator(paddle2_x, paddle1_x, 'p2', 'p1', 'trajx')
        # Write to vec
        if trajx_paddle.startswith('l_'):
            rel_vec[1] = 1
        elif trajx_paddle.startswith('s_'):
            rel_vec[2] = 1
        elif trajx_paddle.startswith('m_'):
            rel_vec[3] = 1

        # Calculate trajectories in y as relations between position in objects across time
        trajy_paddle = dim_comparator(paddle2_y, paddle1_y, 'p2', 'p1', 'trajy')
        # Write to vec
        if trajy_paddle.startswith('l_'):
            rel_vec[4] = 1
        elif trajy_paddle.startswith('s_'):
            rel_vec[5] = 1
        elif trajy_paddle.startswith('m_'):
            rel_vec[6] = 1

        # Calculate trajectory for ball only if there is a ball in the first screen
        if ball_present:
            # Trajectory in x
            trajx_ball = dim_comparator(ball2_x, ball1_x, 'b2', 'b1', 'trajx')
            # Write to vec
            if trajx_ball.startswith('l_'):
                rel_vec[7] = 1
            elif trajx_ball.startswith('s_'):
                rel_vec[8] = 1
            elif trajx_ball.startswith('m_'):
                rel_vec[9] = 1

            # Trajectory in y
            trajy_ball = dim_comparator(ball2_y, ball1_y, 'b2', 'b1', 'trajy')
            # Write to vec
            if trajy_ball.startswith('l_'):
                rel_vec[10] = 1
            elif trajy_ball.startswith('s_'):
                rel_vec[11] = 1
            elif trajy_ball.startswith('m_'):
                rel_vec[12] = 1

        # Object relations (only available if there is a ball)
        if ball_present:
            x = dim_comparator(ball2_x, paddle2_x, 'b', 'p', 'x')
            # Write to vec
            if x.startswith('l_'):
                rel_vec[13] = 1
            elif x.startswith('s_'):
                rel_vec[14] = 1
            elif x.startswith('m_'):
                rel_vec[15] = 1

            y = dim_comparator(ball2_y, paddle2_y, 'b', 'p', 'y')
            # Write to vec
            if y.startswith('l_'):
                rel_vec[16] = 1
            elif y.startswith('s_'):
                rel_vec[17] = 1
            elif y.startswith('m_'):
                rel_vec[18] = 1

    return rel_vec
