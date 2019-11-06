import gym
import numpy as np
from collections import defaultdict
from relational_Q_learning import RelationalQLearningAgent


def follow_ball(rel_state):
    """Hand-coded policy to follow the ball. Useful for debugging.
    Args:
        rel_state: relational representation of the screen (str).
    Returns:
        An action (int).
    """

    # Transform rel_state string into separate variables

    # Split into individual relational mini states
    rel_list = rel_state.split(" AND ")

    # Check whether the ball is present
    ball_present = True if 'b_pre' in rel_list else False

    # Check which object is more to the right
    if 'l_x(b,p)' in rel_list:
        right_obj = 'p'
    elif 's_x(b,p)' in rel_list:
        right_obj = 'none'
    elif 'm_x(b,p)' in rel_list:
        right_obj = 'b'

    # Check x trajectory of ball
    if 'l_trajx(b2,b1)' in rel_list:
        ball_trajx = 'l'
    elif 's_trajx(b2,b1)' in rel_list:
        ball_trajx = 's'
    elif 'm_trajx(b2,b1)' in rel_list:
        ball_trajx = 'm'

    # Implement minimal rule (ignore paddle_traj x and y completely)
    if ball_present:
        if right_obj == 'b':
            if ball_trajx == 'l':
                action = 0
            elif ball_trajx == 's':
                action = 2
            elif ball_trajx == 'm':
                action = 2
        elif right_obj == 'none':
            if ball_trajx == 'l':
                action = 3
            elif ball_trajx == 's':
                action = 0
            elif ball_trajx == 'm':
                action = 2
        elif right_obj == 'p':
            if ball_trajx == 'l':
                action = 3
            elif ball_trajx == 's':
                action = 3
            elif ball_trajx == 'm':
                action = 0
    else:
        action = np.random.choice(range(4))

    return action


def load_qdic(file_name):
    f = open(file_name, 'r')
    data = f.read()
    data = data.replace('array', 'np.array')
    q_dic = eval(data)
    # transform q_dic back into defaultdic to handle unseen states
    q_dic = defaultdict(lambda: np.zeros(6), q_dic)
    return q_dic


# Initialize gym environment and the agent
env = gym.make('BreakoutDeterministic-v4')  # Breakout-v0
print env.unwrapped.get_action_meanings()

# Instantiate QL agent
rel_ql_fox = RelationalQLearningAgent(env, 'Breakout', num_episodes=100,
                                      decay_steps_lr=100, decay_steps_epsilon=100,
                                      discount_factor=0.99,
                                      i_alpha=0.2, f_alpha=0.01,
                                      i_epsilon=0.2, f_epsilon=0.01)

# Test agent
rel_ql_fox.current_epsilon = 0.01
rel_ql_fox.test_agent(50, render=False, rule_policy=follow_ball)
