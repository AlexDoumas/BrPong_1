import random
import numpy as np
import gym
from QL_agents import QLAgent
from QL_agents_preprocessing import get_next_state_features

# Initialize gym environment and the agent
# env = gym.make('PongDeterministic-v4')
# agent = QLAgent('pong', recurrent=False)
# agent.model.load_weights('QN_pong_weights_6000000.hdf5')

# To test transfer load Breakout weights
# agent.model.load_weights('QN_breakout_weights_6000000.hdf5')

# To test supervised fixed frame skipping load the supervised weights
# agent.model.load_weights('supervised_fixed_pong_weights_4000000.hdf5')

# To test supervised random frame skipping change the env and load the supervised weights
# env = gym.make('Pong-v0')
# agent = QLAgent('pong', recurrent=False)
# agent.model.load_weights('supervised_random_pong_weights_4000000.hdf5')

# To test supervised fixed transfer load supervised fixed pong weights
# agent.model.load_weights('supervised_fixed_breakout_weights_4000000.hdf5')

# To test supervised random frame skipping transfer change the env and load the supervised weights
env = gym.make('Pong-v0')
agent = QLAgent('pong', recurrent=False)
agent.model.load_weights('supervised_random_breakout_weights__4000000.hdf5')


returns = []
episode_return = 0

for episode in xrange(100):
    # Observe reward and initialize first state
    obs = agent.preprocessor.get_center_objects(env.reset())

    # Initialize the first state with the same 4 images
    current_state = np.concatenate((obs, obs, obs, obs))

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
        obs = agent.preprocessor.get_center_objects(raw_obs)
        next_state = get_next_state_features(current_state, obs)

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
# Save returns to file
# with open("supervised_random_generalization_to_Pong.txt", "w") as output:
#     output.write(str(returns))

# Test in 100 games:
# mean: -6.82, max: 5.0

# Transfer test in 100 games:
# mean: -21, max: -21.0

# Supervised fixed in 100 games:
# mean: -15.5, max: 8.0

# Supervised random in 100 games:
# mean: -13.81, max: -6.0

# Supervised random transfer test in 100 games:
# mean: -20.83, max: -20.0
