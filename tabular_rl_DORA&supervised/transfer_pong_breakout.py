import gym
from relational_Q_learning import RelationalQLearningAgent
# import numpy as np
# import matplotlib.pyplot as plt
# import copy


# Initialize gym environment and the agent
env = gym.make('BreakoutDeterministic-v4')
print env.unwrapped.get_action_meanings()

# env2 = gym.make('BreakoutDeterministic-v4')
# print env2.unwrapped.get_action_meanings()

# Instantiate QL agent
rel_ql_fox = RelationalQLearningAgent(env, 'Breakout', num_episodes=20000,
                                      decay_steps_lr=20000, decay_steps_epsilon=20000,
                                      discount_factor=0.99,
                                      i_alpha=0.2, f_alpha=0.01,
                                      i_epsilon=0.2, f_epsilon=0.01,
                                      cross_compatible=True)  # Make dictionary compatible

# Load q_dic
rel_ql_fox.load_qdic('q_dic_best_Pong.txt')
# rel_ql_fox.load_qdic('q_dic_best_1000_a.txt')

# Test agent
rel_ql_fox.current_epsilon = 0.05
rel_ql_fox.test_agent(100, render=True, cross_actions=True, cross_dict=True)
