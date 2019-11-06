import gym
import itertools
import numpy as np
from collections import defaultdict, OrderedDict
from pre_processing import PongPreprocessor, BreakoutPreprocessor, transform_reward,\
    relational_states_breakout, relational_states_pong

np.set_printoptions(precision=3)

class RelationalQLearningAgent:
    """Implements an agent that learns through Q learning with relational (symbolic) states."""
    def __init__(self, env, game, num_episodes,
                 decay_steps_lr=None, decay_steps_epsilon=None,
                 discount_factor=1.0,
                 i_alpha=0.3, f_alpha=0.01,
                 i_epsilon=0.3, f_epsilon=0.01,
                 cross_compatible=False):
        self.env = env
        self.game = game
        self.action_size = 4  # env.action_space.n
        self.max_t = env._max_episode_steps
        self.num_episodes = num_episodes
        self.decay_steps_lr = decay_steps_lr
        self.decay_steps_epsilon = decay_steps_epsilon
        self.discount_factor = discount_factor
        self.i_alpha = i_alpha
        self.f_alpha = f_alpha
        self.i_epsilon = i_epsilon
        self.f_epsilon = f_epsilon
        self.cross_compatible = cross_compatible
        # Initialize epsilon and lr
        self.current_epsilon = i_epsilon
        self.current_alpha = i_alpha
        # Initialize relational action-value function. Dictionary that maps relational states to action values.
        if self.game == 'Pong':
            self.q_dic = defaultdict(lambda: np.zeros(self.action_size))
        elif self.game == 'Breakout':
            self.q_dic = defaultdict(lambda: np.zeros(self.action_size))
        # Keeps track of useful statistics
        self.episode_rewards = defaultdict(float)
        self.episode_lengths = defaultdict(float)
        # Initialize preprocessor and get_relation function
        if self.game == 'Pong':
            self.preprocessor = PongPreprocessor()
            self.get_relations = relational_states_pong
        elif self.game == 'Breakout':
            self.preprocessor = BreakoutPreprocessor()
            self.get_relations = relational_states_breakout

    def epsilon_greedy_policy(self, observation):
        """
        Epsilon-greedy policy based on the current Q-function and epsilon.

        Args:
            observation: A state (str).
            self.q_dic: A dictionary that maps from a state to an array of action-values.
            self.current_epsilon: The probability to select a random action. Can be updated during training.
            self.action_size: Number of actions in the environment.

        Returns:
            The probabilities for each action in the form of a numpy array of length action_size.
        """

        act_ps = np.ones(self.action_size, dtype=float) * self.current_epsilon / self.action_size
        best_action = np.argmax(self.q_dic[observation][0:4])
        act_ps[best_action] += (1.0 - self.current_epsilon)
        return act_ps

    def greedy_policy(self, observation):
        """
        Greedy policy based on the current Q-function and epsilon.
        """
        act_ps = np.zeros(self.action_size, dtype=float)
        best_action = np.argmax(self.q_dic[observation])
        act_ps[best_action] = 1.0
        return act_ps

    def epsilon_linear_decay(self):
        """Decais exploration rate linearly between self.i_epsilon and self.f_epsilon
        for self.decay_steps_epsilon steps"""
        if self.current_epsilon > self.f_epsilon:
            new = self.current_epsilon - float(self.i_epsilon - self.f_epsilon) / self.decay_steps_epsilon
            if new <= self.f_epsilon:
                return self.f_epsilon
            else:
                return new
        else:
            return self.f_epsilon

    def alpha_linear_decay(self):
        """Decais learning rate linearly between self.i_alpha and self.i_alpha
                for self.decay_steps_lr steps"""
        if self.current_alpha > self.f_alpha:
            new = self.current_alpha - float(self.i_alpha - self.f_alpha) / self.decay_steps_lr
            if new <= self.f_alpha:
                return self.f_alpha
            else:
                return new
        else:
            return self.f_alpha

    def exponential_decay_bounded(self, iteration, k=3000, low_lim=0.001):
        if self.current_alpha > low_lim:
            new_lr = float(k)/(k+iteration)
        else:
            new_lr = low_lim
        return new_lr

    def save_qdic(self, file_name):
        with open(file_name, 'w') as outfile:
            outfile.write(repr(dict(self.q_dic)))
        return

    def load_qdic(self, file_name):
        f = open(file_name, 'r')
        data = f.read()
        data = data.replace('array', 'np.array')
        q_dic = eval(data)
        # transform q_dic back into defaultdic to handle unseen states
        self.q_dic = defaultdict(lambda: np.zeros(self.action_size), q_dic)
        return

    def relational_q_learning(self, partial_results=False, render=True):
        """
        Q-Learning algorithm: Off-policy TD control. Finds the optimal greedy policy
        while following an epsilon-greedy policy

        Args:
            self.env: OpenAI environment.
            self.num_episodes: Number of episodes to run for.
            self.discount_factor: Gamma discount factor.
            self.alpha: TD learning rate.
            self.current_epsilon: Chance to sample a random action. Float between 0 and 1.
            partial_results: Show action values 5 times during training. Default False.

        Returns:
            q_dic, episode_lengths, episode_rewards.
            q_dic is the optimal action-value function, a dictionary mapping state to action values.
            episode_lengths and episode_rewards are numpy arrays.
        """
        session_rewards = []

        for i_episode in xrange(1, self.num_episodes+1):
            # Reset the environment and pick a random first action
            state = self.env.reset()
            features = self.preprocessor.get_center_objects(state)
            current_relation = self.get_relations(f_vec1=features, f_vec2=features,
                                                  cross_compatible=self.cross_compatible)

            for t in itertools.count():
                if render:
                    self.env.render()

                # Choose action at time t
                action_probs = self.epsilon_greedy_policy(current_relation)
                action = np.random.choice(len(action_probs), p=action_probs)

                # Get observation
                next_state, reward, done, info = self.env.step(action)
                session_rewards.append(reward)
                reward = transform_reward(reward)

                # Get relational state
                next_features = self.preprocessor.get_center_objects(next_state)
                next_relation = self.get_relations(features, next_features,
                                                   cross_compatible=self.cross_compatible)

                # TD Update
                best_next_action = np.argmax(self.q_dic[next_relation])
                td_target = reward + self.discount_factor * self.q_dic[next_relation][best_next_action]
                td_delta = td_target - self.q_dic[current_relation][action]

                # Perform q-update
                self.q_dic[current_relation][action] += self.current_alpha * td_delta

                # Update statistics
                self.episode_rewards[i_episode] += reward
                self.episode_lengths[i_episode] = len(self.q_dic)

                if done:
                    break

                # Reasign current to next
                current_relation = next_relation
                features = next_features
                state = next_state

            # Save q dictionary only if episode rewards is the higest so far
            if self.episode_rewards[i_episode] == max(self.episode_rewards.values()):
                self.save_qdic('q_dic_best_' + self.game + '.txt')

            # Update epsilon (and policy implicitly) after every episode
            if self.decay_steps_epsilon is not None:
                # self.current_epsilon = self.exponential_decay_bounded(i_episode)
                self.current_epsilon = self.epsilon_linear_decay()

            # Update lr
            if self.decay_steps_lr is not None:
                # self.current_alpha = self.exponential_decay_bounded(i_episode)
                self.current_alpha = self.alpha_linear_decay()

            # Print info optionaly
            if partial_results:
                print 'episode:', i_episode, 'epsilon:', round(self.current_epsilon, 3),\
                    'lr:', round(self.current_alpha, 3), 'return:',\
                    self.episode_rewards[i_episode], 'table length:', len(self.q_dic)

                if i_episode % (self.num_episodes / 10) == 0:

                    for state in self.q_dic:
                        print state, self.q_dic[state]
                    print ''

        # Save last q dictionary
        self.save_qdic('q_dic_last_' + self.game + '.txt')

        return self.q_dic, self.episode_rewards, self.episode_lengths, session_rewards

    def test_agent(self, n, render=True, cross_actions=False, cross_dict=False, rule_policy=None):
        # self.current_epsilon = 0.1
        """Test agent in n games"""

        for state in self.q_dic:
            print state, self.q_dic[state]
        print ''

        returns = []
        for i_episode in xrange(1, n+1):
            ep_return = 0
            # Reset the environment and pick a random first action
            state = self.env.reset()

            features = self.preprocessor.get_center_objects(state)
            current_relation = self.get_relations(f_vec1=features,
                                                  f_vec2=features,
                                                  cross_compatible=self.cross_compatible,
                                                  cross_dict=cross_dict)

            for t in itertools.count():
                if render:
                    self.env.render()

                # Choose action
                if rule_policy is not None:
                    action = rule_policy(current_relation)
                else:
                    action_probs = self.epsilon_greedy_policy(current_relation)  # greedy instead of epsilon greedy
                    action = np.random.choice(len(action_probs), p=action_probs)

                if cross_actions:
                    if action == 2:
                        action = 3
                    elif action == 3:
                        action = 2

                # Get state
                state, reward, done, info = self.env.step(action)

                # Get relational state
                next_features = self.preprocessor.get_center_objects(state)
                next_relation = self.get_relations(features, next_features,
                                                   cross_compatible=self.cross_compatible,
                                                   cross_dict=cross_dict)

                # Update statistics
                ep_return += reward

                if done:
                    break

                # Reasign current to next
                current_relation = next_relation
                features = next_features

            # Append episode return to get test mean
            returns.append(ep_return)

            print i_episode, ep_return
        print 'mean returns:', np.mean(returns)
        return
