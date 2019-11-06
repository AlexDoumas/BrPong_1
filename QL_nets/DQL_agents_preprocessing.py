import numpy as np


def to_grayscale(img):
    return np.mean(img, axis=2).astype(np.uint8)


def downsample(img):
    return img[::2, ::2]


def preprocess(img):
    return to_grayscale(downsample(img))


def transform_reward(reward):
    return np.sign(reward)


def get_next_state(current, obs):
    # Next state is composed by the last 3 images of the previous state and the new observation
    # Add an extra axis to obs to append to the next state
    obs = obs[..., np.newaxis]
    return np.append(current[:, :, 1:], obs, axis=2)
