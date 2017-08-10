import numpy as np
import random

class LinearDecayExplorer:
    def __init__(self, final_exploration_step=10**6,
                start_epsilon=1.0, final_epsilon=0.1):
        self.final_exploration_step = final_exploration_step
        self.start_epsilon = start_epsilon
        self.final_epsilon = final_epsilon
        self.base_epsilon = self.start_epsilon - self.final_epsilon

    def select_action(self, t, greedy_action, num_actions):
        if t > self.final_exploration_step:
            return self.final_epsilon
        factor = 1 - float(t) / self.final_exploration_step
        eps = self.base_epsilon * factor + self.final_epsilon
        if random.random() < eps: 
            return np.random.choice(num_actions)
        return greedy_action
