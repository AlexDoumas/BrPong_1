import gym
from relational_Q_learning import RelationalQLearningAgent
import numpy as np
import matplotlib.pyplot as plt

# Initialize gym environment and the agent
env = gym.make('PongDeterministic-v4')  # Breakout-v0

# Instantiate QL agent
rel_ql_fox = RelationalQLearningAgent(env, 'Pong', num_episodes=1000,
                                      decay_steps_lr=1000, decay_steps_epsilon=1000,
                                      discount_factor=0.99,
                                      i_alpha=0.9, f_alpha=0.05,
                                      i_epsilon=0.9, f_epsilon=0.01)


# # Train and watch partial q-values
# q_values, returns_dic, lengths_dic, rewards = rel_ql_fox.relational_q_learning(partial_results=True, render=False)
#
# # make list of returns
# episode_returns = [returns_dic[x] for x in xrange(1, len(returns_dic)+1)]
# table_lengths = [lengths_dic[x] for x in xrange(1, len(returns_dic)+1)]
# cum_return = np.cumsum(episode_returns)
# cum_mean_return = [float(elem)/(count+1) for count, elem in enumerate(cum_return)]
#
# # Print returns
# fig = plt.figure(1)
#
# plt.subplot(311)
# plt.plot(cum_mean_return)
# plt.ylabel('Running Average')
# plt.xlabel('Episode')
#
# plt.subplot(312)
# plt.plot(episode_returns)
# plt.ylabel('Return')
# plt.xlabel('Episode')
# plt.plot()
#
# plt.subplot(313)
# plt.plot(table_lengths)
# plt.ylabel('Table Length')
# plt.xlabel('Episode')
# # plt.plot()
#
# fig.tight_layout()
# fig.savefig('tabular_RL_results_PONG_1000_e_1_to_0.05_1000_lr_0.1.pdf')
# # plt.show()

# Load q_dic
rel_ql_fox.load_qdic('q_dic_best_Pong.txt')


# Test agent
rel_ql_fox.current_epsilon = 0.01
rel_ql_fox.test_agent(100, render=True)


