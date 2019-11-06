import os
import tensorflow as tf
import random
import numpy as np
from keras.layers import Dense, Input, multiply, Lambda, Conv2D, Flatten
from keras.models import Model, clone_model
from keras import optimizers
from DQL_agents_preprocessing import preprocess, transform_reward, get_next_state

# Disable tensorflow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


# Wrapper for tensorflow huber loss
def huber_loss(y_true, y_pred):
    return tf.losses.huber_loss(y_true, y_pred)


# Buffer
class RingBuf:
    def __init__(self, size):
        # Pro-tip: when implementing a ring buffer, always allocate one extra element,
        # this way, self.start == self.end always means the buffer is EMPTY, whereas
        # if you allocate exactly the right number of elements, it could also mean
        # the buffer is full. This greatly simplifies the rest of the code.
        self.data = [None] * (size + 1)
        self.start = 0
        self.end = 0

    def append(self, element):
        self.data[self.end] = element
        self.end = (self.end + 1) % len(self.data)
        # end == start and yet we just added one element. This means the buffer has one
        # too many element. Remove the first element by incrementing start.
        if self.end == self.start:
            self.start = (self.start + 1) % len(self.data)

    def sample_batch(self, sample_size):
        """Explanation:
        random.sample(xrange(len(mylist)), sample_size) generates a random sample of the indices of the original list.
        This sample then gets sorted to preserve the ordering of elements in the original list.
        """
        return [self.data[i] for i in sorted(random.sample(xrange(len(self)), sample_size))]

    def __getitem__(self, idx):
        return self.data[(self.start + idx) % len(self.data)]

    def __len__(self):
        if self.end < self.start:
            return self.end + len(self.data) - self.start
        else:
            return self.end - self.start

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]


class DQLAgent:
    def __init__(self, game):  # Should I take env as input?
        self.action_size = 6  # to play more atari games set to max (18) and update the choose_best_action method
        self.batch_size = 32
        self.atari_shape = (105, 80, 4)  # Tensorflow backend, so the "channels" are last
        self.memory_size = 1000000
        self.memory = RingBuf(self.memory_size)
        self.gamma = 0.99  # discount rate
        self.epsilon = 1.0  # exploration rate
        self.epsilon_min = 0.1
        self.learning_rate = 0.00025
        self.model = self.atari_model()
        self.target_model = clone_model(self.model)
        self.target_model.set_weights(self.model.get_weights())
        self.game = game  # necessary to define action space

    def atari_model(self):
        """Defines a deep neural network model"""

        # With the functional API we need to define the inputs.
        frames_input = Input(self.atari_shape, name='frames')
        actions_input = Input((self.action_size,), name='mask')

        # Assuming that the input frames are still encoded from 0 to 255. Transforming to [0, 1].
        normalized = Lambda(lambda x: x / 255.0)(frames_input)

        # "The first hidden layer convolves 16 8x8 filters with stride 4 and applies a rectifier non-linearity"
        conv_1 = Conv2D(16, (8, 8), strides=(4, 4), activation='relu')(normalized)

        # "The second hidden layer convolves 32 4x4 filters with stride 2, again followed by a rectifier non-linearity"
        conv_2 = Conv2D(32, (4, 4), strides=(2, 2), activation='relu')(conv_1)

        # Flattening the second convolutional layer.
        conv_flattened = Flatten()(conv_2)

        # "The final hidden layer is fully-connected and consists of 256 rectifier units."
        hidden = Dense(256, activation='relu')(conv_flattened)

        # "The output layer is a fully-connected linear layer with a single output for each valid action."
        output = Dense(self.action_size, activation='linear')(hidden)

        # Finally, multiply the output by the mask!
        filtered_output = multiply([output, actions_input])

        # Define model
        self.model = Model(inputs=[frames_input, actions_input], outputs=filtered_output)

        # Compile model
        optimizer = optimizers.RMSprop(lr=self.learning_rate, rho=0.95, epsilon=0.01)
        self.model.compile(optimizer, loss=huber_loss)

        # Return the model
        return self.model

    def copy_model(self):
        """Returns a copy of a keras model."""

        self.target_model = clone_model(self.model)
        self.target_model.set_weights(self.model.get_weights())

        return self.target_model

    def fit_batch(self, batch):
        """Do one deep Q learning iteration.

        Params:
        - self.model: The DQN
        - self.gamma: Discount factor (should be 0.99)
        - start_states: numpy array of starting states
        - actions: numpy array of one-hot encoded actions corresponding to the start states
        - rewards: numpy array of rewards corresponding to the start states and actions
        - next_states: numpy array of the resulting states corresponding to the start states and actions
        - is_terminal: numpy boolean array of whether the resulting state is terminal
        """

        # 32 TUPLES (start_states, actions, rewards, next_states, is_terminal)
        start_states = np.array([my_tuple[0] for my_tuple in batch])
        actions = np.array([my_tuple[1] for my_tuple in batch])
        rewards = np.array([my_tuple[2] for my_tuple in batch])
        next_states = np.array([my_tuple[3] for my_tuple in batch])
        is_terminal = np.array([my_tuple[4] for my_tuple in batch])

        # First, predict the Q values of the next states. Note how we are passing ones as the mask.
        next_q_values = self.target_model.predict([next_states, np.ones(actions.shape)])

        # The Q values of the terminal states is 0 by definition, so override them
        next_q_values[is_terminal] = 0

        # The Q values of each start state is the reward + gamma * the max next state Q value
        q_values = rewards + self.gamma * np.max(next_q_values, axis=1)

        # Fit the keras model. Note how we are passing the actions as the mask and multiplying
        # the targets by the actions
        self.model.train_on_batch([start_states, actions],
                                  actions * q_values[:, None])

    def update_epsilon(self):
        """Update epsilon until reaching epsilon_min"""

        if self.epsilon > 0.1:
            self.epsilon -= (1 - 0.1) / 1000000
        else:
            self.epsilon = 0.1

        return self.epsilon

    def choose_best_action(self, state):
        # Get action values
        # Note that I add an extra dimension to the state because the keras model expects batches of data
        act_values = self.model.predict([state[np.newaxis, ...], np.ones((1, self.action_size))])

        # Return action index
        if self.game == 'breakout':
            # Because the last 2 values are not going to be chosen, they will be always masked during training
            return np.argmax(act_values[0][:4])
        elif self.game == 'pong':
            return np.argmax(act_values[0][:6])

    def q_iteration(self, env, current_state, act_list):

        # Choose the action
        if random.random() < self.epsilon:
            action_index = env.action_space.sample()

        else:
            action_index = self.choose_best_action(current_state)

        # Check if all previous actions are NOOP
        all_zeros = all(p == 0 for p in act_list)

        # Change action if all previous actions are NOOP and current is NOOP
        if all_zeros and action_index == 0:
            action_index = random.randint(1, env.action_space.n - 1)

        # Build action vector
        action = np.eye(self.action_size, dtype=np.int8)[action_index]

        # Play one game iteration
        obs, reward, is_done, _ = env.step(action_index)

        # Pre-process observation
        obs = preprocess(obs)

        # Build next state
        next_state = get_next_state(current_state, obs)

        # Pre-process reward
        transformed_reward = transform_reward(reward)

        # Remember the previous state, action, reward, and done
        self.memory.append((current_state, action, transformed_reward, next_state, is_done))

        # Sample and fit
        batch = self.memory.sample_batch(self.batch_size)
        self.fit_batch(batch)

        return next_state, reward, is_done, action_index

    def random_play_and_save(self, env, current_state, act_list):

        # Decide action
        action_index = env.action_space.sample()

        # Check if all previous actions are NOOP
        all_zeros = all(p == 0 for p in act_list)

        # Change action if all previous actions are NOOP and current is NOOP
        if all_zeros and action_index == 0:
            action_index = random.randint(1, env.action_space.n - 1)

        # Build action vector
        action = np.eye(self.action_size, dtype=np.int8)[action_index]

        # Advance the game to the next state based on the action.
        obs, reward, is_done, _ = env.step(action_index)

        # Pre-process observation
        obs = preprocess(obs)

        # Build next state
        next_state = get_next_state(current_state, obs)

        # Pre-process reward
        transformed_reward = transform_reward(reward)

        # Remember the previous state, action, reward, and done
        self.memory.append((current_state, action, transformed_reward, next_state, is_done))

        return next_state, reward, is_done, action_index

    def nonrandom_play_and_save(self, env, current_state, act_list):
        """This method is designed to be used when you need to continue training after a (initial)training session is
        finished.
        I have found that initializing the memory with random play in that situation can make the agent to diverge."""

        # Choose the action according to the behaviour policy
        if random.random() < 0.05:
            action_index = env.action_space.sample()
        else:
            action_index = self.choose_best_action(current_state)

        # Check if all previous actions are NOOP
        all_zeros = all(p == 0 for p in act_list)

        # Change action if all previous actions are NOOP and current is NOOP
        if all_zeros and action_index == 0:
            action_index = random.randint(1, env.action_space.n - 1)

        # Build action vector
        action = np.eye(self.action_size, dtype=np.int8)[action_index]

        # Advance the game to the next state based on the action.
        obs, reward, is_done, _ = env.step(action_index)

        # Pre-process observation
        obs = preprocess(obs)

        # Build next state
        next_state = get_next_state(current_state, obs)

        # Pre-process reward
        transformed_reward = transform_reward(reward)

        # Remember the previous state, action, reward, and done
        self.memory.append((current_state, action, transformed_reward, next_state, is_done))

        return next_state, reward, is_done, action_index

