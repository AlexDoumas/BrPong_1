import numpy as np
import gym
from QL_agents import QLAgent


# Constants
MAX_EPISODES = 10000000  # 10000000
MAX_EPISODE_TIME   = 100000
RANDOM_STATES = 5000  # 50000
MAX_STATES = 10000000  # 10000000
SAVE_AFTER = 1000000  # 1000000
SAVE_TARGET_MODEL_AFTER = 10000  # 10000
MAX_NOOP = 30

# initialize gym environment and the agent
env = gym.make('BreakoutDeterministic-v4')
agent = QLAgent('breakout', recurrent=False)
agent.epsilon = 0.1

# counters
episode_return = 0
state_counter = 1
random_counter = 0
act_list = []
training_returns = []
# Iterate the game
for e in xrange(MAX_EPISODES):
    # Observe reward and initialize first state
    obs = agent.preprocessor.get_center_objects(env.reset())

    # Initialize the first state with the same 4 images, shape: (48,)
    current_state = np.concatenate((obs, obs, obs, obs))

    for time_step in xrange(MAX_EPISODE_TIME):

        # turn this on if you want to render
        # env.render()

        # Perform q-updates only after RANDOM_EPISODES frames
        if random_counter < RANDOM_STATES:
            # Play randomly and save experience (replace with nonrandom_play_and_save to continue training)
            next_state, reward, is_done, act_index = agent.random_play_and_save(env, current_state, act_list)
        else:
            # Perform q-updates (and save to memory)
            next_state, reward, is_done, act_index = agent.supervised_learning_iteration(env, current_state, act_list)

        # Append to act_indexes only until MAX_NOOP
        if time_step <= MAX_NOOP:
            act_list.append(act_index)

        # Make next_state the new current state for the next frame.
        current_state = next_state

        # Update return
        episode_return += reward

        # Update random counter
        random_counter += 1

        # Update episode counter and epsilon after RANDOM_FRAMES frames
        if random_counter >= RANDOM_STATES:
            state_counter += 1
            agent.update_epsilon()

        # Save and load target model
        if state_counter % SAVE_TARGET_MODEL_AFTER == 0:
            agent.copy_model()
            print "target model updated"

        # Save weights after SAVE_AFTER frames
        if state_counter % SAVE_AFTER == 0:
            print "saving weights"
            print ""
            agent.model.save_weights('supervised_breakout_weights_huber_target10000_hidden_150_100_'
                                     + str(state_counter) + '.hdf5')

            # Save returns every million iterations (to save RAM)
            a = np.array(training_returns)
            np.savetxt('supervised_breakout_returns_huber__target10000_hidden_150_100_'
                       + str(state_counter) + '.txt', a, fmt='%d')
            training_returns = []

        # is_done becomes True when the game ends
        if is_done:
            if random_counter < RANDOM_STATES:
                # print the score and break out of the loop
                print("episode: {}, tot replay memory size: {}, ep return: {}, epsilon: {}"
                      .format(e, random_counter, episode_return, agent.epsilon))

            else:
                # print the score and break out of the loop
                print("episode: {}, tot learning iterations: {}, ep return: {}, epsilon: {}"
                      .format(e, state_counter - 1, episode_return, agent.epsilon))

            # Append episode return and reset
            training_returns.append(episode_return)
            episode_return = 0

            break

    if state_counter >= MAX_STATES:
        break
