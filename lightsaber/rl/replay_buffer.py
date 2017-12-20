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

class EpisodeReplayBuffer:
    def __init__(self, episode_size):
        self.buffer = deque(maxlen=episode_size)
        self.tmp_obs_t_buffer = []
        self.tmp_action_buffer = []
        self.tmp_reward_buffer = []
        self.tmp_obs_tp1_buffer = []
        self.tmp_done_buffer = []

    def append(self, obs_t, action, reward, obs_tp1, done):
        if isinstance(done, bool):
            done = 1 if done else 0
        self.tmp_obs_t_buffer.append(obs_t)
        self.tmp_action_buffer.append(action)
        self.tmp_reward_buffer.append(reward)
        self.tmp_obs_tp1_buffer.append(obs_tp1)
        self.tmp_done_buffer.append(done)

    def end_episode(self):
        episode = dict(
            obs_t=self.tmp_obs_t_buffer,
            action=self.tmp_action_buffer,
            reward=self.tmp_reward_buffer,
            obs_tp1=self.tmp_obs_tp1_buffer,
            done=self.tmp_done_buffer
        )
        self.buffer.append(episode)
        self.reset_tmp_buffer()

    def reset_tmp_buffer(self):
        self.tmp_obs_t_buffer = []
        self.tmp_action_buffer = []
        self.tmp_reward_buffer = []
        self.tmp_obs_tp1_buffer = []
        self.tmp_done_buffer = []

    def sample(self, batch_size):
        episodes = random.sample(self.buffer, batch_size)
        obs_t = []
        actions = []
        rewards = []
        obs_tp1 = []
        done = []
        for episode in episodes:
            obs_t.append(episode['obs_t'])
            actions.append(episode['action'])
            rewards.append(episode['reward'])
            obs_tp1.append(episode['obs_tp1'])
            done.append(episode['done'])
        return obs_t, actions, rewards, obs_tp1, done 

class NECReplayBuffer:
    def __init__(self, buffer_size):
        self.buffer = deque(maxlen=buffer_size)

    def append(self, obs_t, action, value):
        experience = dict(obs_t=obs_t, action=action, value=value)
        self.buffer.append(experience)

    def sample(self, batch_size):
        experiences = random.sample(self.buffer, batch_size)
        obs_t = []
        actions = []
        values = []
        for experience in experiences:
            obs_t.append(experience['obs_t'])
            actions.append(experience['action'])
            values.append(experience['value'])
        return obs_t, actions, values
