class EnvWrapper:
    def __init__(self, env, r_preprocess=None, s_preprocess=None):
        self.env = env
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
