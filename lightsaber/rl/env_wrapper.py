import numpy as np
import copy


class EnvWrapper:
    def __init__(self, env, r_preprocess=None, s_preprocess=None):
        self.env = env
        self.observation_space = env.observation_space
        self.action_space = env.action_space
        self.r_preprocess = r_preprocess
        self.s_preprocess = s_preprocess

    def step(self, action):
        state, reward, done, info = self.env.step(action)
        # preprocess reward
        if self.r_preprocess is not None:
            reward = self.r_preprocess(reward)
        # preprocess state
        if self.s_preprocess is not None:
            state = self.s_preprocess(state)
        return state, reward, done, info

    def reset(self):
        state = self.env.reset()
        # preprocess state
        if self.s_preprocess is not None:
            state = self.s_preprocess(state)
        return state

    def render(self):
        self.env.render()

class BatchEnvWrapper:
    def __init__(self, envs, r_preprocess=None, s_preprocess=None):
        self.envs = []
        for env in envs:
            env = EnvWrapper(
                env,
                r_preprocess=r_preprocess,
                s_preprocess=s_preprocess
            )
            self.envs.append(env)
        self.running = [False for _ in range(len(envs))]
        state_shape = envs[0].observation_space.shape
        self.zero_state = np.zeros(state_shape, dtype=np.float32)

    def step(self, actions):
        states = []
        rewards = []
        dones = []
        infos = []
        for i, env in enumerate(self.envs):
            if self.running[i]:
                state, reward, done, info = env.step(actions[i])
            else:
                state = copy.deepcopy(self.zero_state)
                reward = 0
                done = True
                info = None
            states.append(state)
            rewards.append(reward)
            dones.append(done)
            infos.append(info)
            self.running[i] = not done
        return states, rewards, dones, infos

    def reset(self):
        self.running = [True for _ in range(len(self.envs))]
        states = []
        for env in self.envs:
            state = env.reset()
            states.append(state)
        return states

    def render(self):
        self.envs[0].render()

    def get_num_of_envs(self):
        return len(self.envs)