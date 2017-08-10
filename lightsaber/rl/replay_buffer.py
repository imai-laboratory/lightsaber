from collections import deque
import random


class ReplayBuffer:
    def __init__(self, buffer_size):
        self.buffer = deque(maxlen=buffer_size)

    def append(self, obs_t, action, reward, obs_tp1, done):
        if isinstance(done, bool):
            done = 1 if done else 0
        experience = dict(obs_t=obs_t, action=action,
                reward=reward, obs_tp1=obs_tp1, done=done)
        self.buffer.append(experience)

    def sample(self, batch_size):
        experiences = random.sample(self.buffer, batch_size)
        obs_t = []
        actions = []
        rewards = []
        obs_tp1 = []
        done = []
        for experience in experiences:
            obs_t.append(experience['obs_t'])
            actions.append(experience['action'])
            rewards.append(experience['reward'])
            obs_tp1.append(experience['obs_tp1'])
            done.append(experience['done'])
        return obs_t, actions, rewards, obs_tp1, done
