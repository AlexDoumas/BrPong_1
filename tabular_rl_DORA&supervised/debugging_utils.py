import numpy as np


def get_bricks(img):
    """Returns number of bricks present in the screen
    """

    # Wall corners: (8, 57), (152, 93), so: 152-8=144 wide; 93-57=36 tall
    # Bricks are 8 pixels wide and 6 pixels tall, so grid is 18x6

    # Iterate over wall in steps
    # If there is any black pixel, append brick index (counter)
    counter = 0
    for col_ind in xrange(8, 153-8*2, 8*2):
        # counter = 0
        for raw_ind in xrange(57, 94-6, 6):
            brick = img[raw_ind:raw_ind+6, col_ind:col_ind+8*2, :]
            if np.all(brick == 0):
                counter += 1
    # Transform list of deleted bricks into an integer identifier and return
    # return str(counter)
    # return ''.join(map(str, deleted_bricks))
    return counter


def get_wall_state(img):
    """Builds a state representation of the wall of bricks in Breakout
    by checking for black pixels inside.

    Args:
        img: np.array of the entire screen.
    Returns:
        a tuple of integers, with each inner tuple indicating a deleted brick
    """

    # Wall corners: (8, 57), (152, 93), so: 152-8=144 wide; 93-57=36 tall
    # Bricks are 8 pixels wide and 6 pixels tall, so grid is 18x6

    # Iterate over wall in steps
    # If there is any black pixel, append brick index (counter)
    deleted_bricks = []
    counter = 0
    for col_ind in xrange(8, 153-8*2, 8*2):
        # counter = 0
        for raw_ind in xrange(57, 94-6, 6):
            brick = img[raw_ind:raw_ind+6, col_ind:col_ind+8*2, :]
            if np.all(brick == 0):
                deleted_bricks.append(counter)
            counter += 1
    # Transform list of deleted bricks into an integer identifier and return
    # return str(counter)
    # return ''.join(map(str, deleted_bricks))
    return str(-1) if not deleted_bricks else ''.join(map(str, deleted_bricks))


def is_there_ball(feature_vec):
    """Returns True if there is a ball on the screen.
    Arg:
        feature_vec: a np.array of size 6. Indexes 2 and 3 refer to the x y coordinates of the center of the ball.
    Returns:
        True if both numbers are different from zero. False otherwise.
    """
    if feature_vec[2] == 0 and feature_vec[3] == 0:
        return False
    else:
        return True


def get_next_state_features(current, obs):
    # Next state is composed by the last 3 feature vectors of the previous state and the new observation
    return np.append(current[6:], obs, axis=0)

