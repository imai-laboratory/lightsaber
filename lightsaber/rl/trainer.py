from collections import deque
import tensorflow as tf
import numpy as np
import copy


class AgentInterface:
    def act(self, state, reward, training):
        raise NotImplementedError()

    def stop_episode(state, reward, training):
        raise NotImplementedError()

class Trainer:
    def __init__(self, env, agent, state_shape=[84, 84],
            final_step=1e7, state_window=1, preprocess=lambda s: s,
            training=True, render=False, debug=True,
            before_action=None, after_action=None, end_episode=None):
        self.env = env
        self.final_step = final_step
        self.states = deque(
            np.zeros(
                [state_window] + state_shape,
                dtype=np.float32
            ).tolist(),
            maxlen=state_window
        )
        self.agent = agent
        self.preprocess = preprocess
        self.training = training
        self.render = render
        self.debug = debug
        self.before_action = before_action
        self.after_action = after_action
        self.end_episode = end_episode

    def start(self):
        global_step = 0
        episode = 0
        while True:
            local_step = 0
            reward = 0
            sum_of_rewards = 0
            done = False
            state = self.preprocess(self.env.reset())

            while True:
                self.states.append(state.tolist())
                states = np.array(list(self.states))

                # episode reaches the end
                if done:
                    episode += 1

                    # callback at the end of episode
                    if self.end_episode is not None:
                        self.end_episode(sum_of_rewards, global_step, episode)

                    self.agent.stop_episode(
                        states,
                        reward,
                        self.training
                    )
                    if self.debug:
                        print('step: {}, episode: {}, reward: {}'.format(
                            global_step,
                            episode,
                            sum_of_rewards
                        ))
                    break

                # callback before taking action
                if self.before_action is not None:
                    self.before_action(states, global_step, local_step)

                # take next action
                action = self.agent.act(
                    states,
                    reward,
                    self.training
                )
                state, reward, done, info = self.env.step(action)
                state = self.preprocess(state)
                sum_of_rewards += reward

                # callback after taking action
                if self.after_action is not None:
                    self.after_action(states, reward, global_step, local_step)

                if self.render:
                    self.env.render()

                global_step += 1
                local_step += 1

                if global_step > self.final_step:
                    return
