import numpy as np
import scipy.signal


def discount(x, gamma):
    return scipy.signal.lfilter([1], [1, -gamma], x[::-1], axis=0)[::-1]

def compute_v_and_adv(self, rewards, values, bootstrapped_value, gamma, lam=1.0):
    rewards = np.array(self.rewards)
    values = np.array(self.values + [bootstrapped_value])
    v = discount(np.array(self.rewards + [bootstrapped_value]), gamma)[:-1]
    delta = rewards + gamma * values[1:] - values[:-1]
    adv = discount(delta, gamma * lam)
    return v, adv

class Rollout:
    def __init__(self):
        self.flush()

    def add(self, state, action, reward, value, terminal=False, feature=None):
        self.states.append(state)
        self.actions.append(action)
        self.rewards.append(reward)
        self.values.append(value)
        self.terminal = terminal
        self.features.append(feature)

    def flush(self):
        self.states = []
        self.actions = []
        self.rewards = []
        self.values = []
        self.terminal = False
        self.features = []
