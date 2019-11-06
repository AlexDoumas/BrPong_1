import random
import numpy as np
from DQL_agents import DQLAgent
import gym
from DQL_agents_preprocessing import preprocess, transform_reward, get_next_state
import matplotlib.image as mpimg
import matplotlib.pyplot as plt

# initialize gym environment and the agent
env = gym.make('PongDeterministic-v4')
agent = DQLAgent('pong')
agent.model.load_weights('DQN_pong_weights_13000000.hdf5')
# To test transfer just change the weights
# agent.model.load_weights('DQN_breakout_weights_20000000.hdf5')

returns = []
episode_return = 0
for episode in xrange(100):
    # Observe reward and initialize first state
    obs = preprocess(env.reset())

    # Initialize the first state with the same 4 images
    current_state = np.array([[obs, obs, obs, obs]], dtype=np.uint8).reshape((105, 80, 4))

    for time_step in xrange(20000):
        # print "episode:", e, "time_step:", time_step

        # turn this on if you want to render
        # env.render()

        # Choose the action according to the behaviour policy
        if random.random() < 0.05:
            action_index = env.action_space.sample()
        else:
            action_index = agent.choose_best_action(current_state)

        # Play one game iteration
        raw_obs, reward, is_done, _ = env.step(action_index)
        obs = preprocess(raw_obs)
        next_state = get_next_state(current_state, obs)

        # make next_state the new current state for the next frame.
        current_state = next_state

        # Update return
        episode_return += reward
        # episode_return += transform_reward(reward)

        # imgplot = plt.imshow(raw_obs)
        # plt.show()
        # raw_input("Press Enter to continue...")

        # is_done becomes True when the game ends
        if is_done:
            # print the score and break out of the loop
            print("episode: {}/{}, return: {}"
                  .format(episode, 10, episode_return))

            # Reset episode return
            returns.append(episode_return)
            episode_return = 0

            break

print np.mean(returns), max(returns)

# Write returns to file
# with open("DQN_test_generalization_to_Pong.txt", "w") as output:
#     output.write(str(returns))

# Test with a 100 games in Pong:
# mean: 14.46, max: 21.0

# Generalization: 100 games of Pong with Breakout weights.
# mean: , max:
