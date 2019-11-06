import numpy as np
import gym
from QL_agents import QLAgent
from QL_agents_preprocessing import PongPreprocessor, get_screen_features_pong
# Constants
MAX_EPISODES = 1000000
MAX_EPISODE_TIME = 100000
RANDOM_FRAMES = 50000  # 20 percent of DQL agent (50000)
MAX_STATES = 10000000  # 20 percent of DQL agent (10000000)
SAVE_AFTER = 1000000  # 20 percent of DQL agent (1000000)
SAVE_TARGET_MODEL_AFTER = 10000  # 20 percent of DQL agent (10000)
MAX_NOOP = 30

# Initialize gym environment and the agent
env = gym.make('PongDeterministic-v4')
agent = QLAgent(6, 'pong')

episode_return = 0
frame_counter = 1
random_counter = 0
act_list = []

# Iterate the game
for e in xrange(MAX_EPISODES):
    # Initialize first state
    raw_obs = env.reset()
    obs = get_screen_features_pong(raw_obs)

    # Initialize the first state with the same 4 images, shape: (48,)
    current_state = np.concatenate((obs, obs, obs, obs))

    for time_step in xrange(MAX_EPISODE_TIME):

        # turn this on if you want to render
        # env.render()

        # Perform q-updates only after RANDOM_EPISODES frames
        if random_counter < RANDOM_FRAMES:
            # Play randomly and save experience
            next_state, reward, is_done, act_index = agent.random_play_and_save(env, current_state, act_list)
        else:
            # Perform q-updates (and save to memory)
            next_state, reward, is_done, act_index = agent.q_iteration(env, current_state, act_list)

        # Append to act_indexes only until MAX_NOOP
        if random_counter <= MAX_NOOP:
            act_list.append(act_index)

        # Make next_state the new current state for the next frame.
        current_state = next_state

        # Update return
        episode_return += reward

        # Update random counter
        random_counter += 1

        # Update episode counter and epsilon after RANDOM_FRAMES frames
        if random_counter >= RANDOM_FRAMES:
            frame_counter += 1
            agent.update_epsilon()

        # Save and load target model
        if frame_counter % SAVE_TARGET_MODEL_AFTER == 0:
            agent.copy_model()
            print "target model updated"

        # Save weights after SAVE_AFTER frames
        if frame_counter % SAVE_AFTER == 0:
            print "saving weights"
            print ""
            agent.model.save_weights('QLA_weights' + str(frame_counter) + '.hdf5')

        # is_done becomes True when the game ends
        if is_done:
            if random_counter < RANDOM_FRAMES:
                # print the score and break out of the loop
                print("episode: {}, tot replay memory size: {}, ep return: {}, epsilon: {}"
                      .format(e, random_counter, episode_return, agent.epsilon))

            else:
                # print the score and break out of the loop
                print("episode: {}, tot q-learning iterations: {}, ep return: {}, epsilon: {}"
                      .format(e, frame_counter-1, episode_return, agent.epsilon))

            # Reset episode return
            episode_return = 0

            break

    if frame_counter >= MAX_STATES:
        break
