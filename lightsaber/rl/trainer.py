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
            before_action=None, after_action=None):
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

    def start(self):
        step = 0
        episode = 0
        while True:
            reward = 0
            sum_of_rewards = 0
            done = False
            state = self.preprocess(self.env.reset())

            while True:
                self.states.append(state.tolist())
                states = np.array(list(self.states))

                # episode reaches the end
                if done:
                    self.agent.stop_episode(
                        states,
                        reward,
                        self.training
                    )
                    episode += 1
                    if self.debug:
                        print('step: {}, episode: {}, reward: {}'.format(
                            step,
                            episode,
                            sum_of_rewards
                        ))
                    break

                # callback before taking action
                if self.before_action is not None:
                    self.before_action(states, step)

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
                    self.after_action(states, reward, step)

                if self.render:
                    self.env.render()

                step += 1

                if step > self.final_step:
                    return
