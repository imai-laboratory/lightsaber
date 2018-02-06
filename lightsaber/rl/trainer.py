from collections import deque
import tensorflow as tf
import numpy as np
import copy
import time
import threading


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

class AsyncTrainer:
    def __init__(self, envs, agents, state_shape=[84, 84],
            final_step=1e7, state_window=1, preprocess=lambda s: s,
            training=True, render=False, debug=True, before_action=None,
            after_action=None, end_episode=None, n_threads=10):

        # meta data shared by all threads
        self.meta_data = {
            'shared_step': 0,
            'shared_episode': 0
        }

        # inserted callbacks
        def _before_action(state, global_step, local_step):
            shared_step = self.meta_data['shared_step']
            if before_action is not None:
                before_action(state, shared_step, global_step, local_step)

        def _after_action(state, reward, global_step, local_step):
            self.meta_data['shared_step'] += 1
            shared_step = self.meta_data['shared_step']
            if after_action is not None:
                after_action(state, reward, shared_step, global_step, local_step)

        def _end_episode(reward, global_step, episode):
            shared_step = self.meta_data['shared_step']
            self.meta_data['shared_episode'] += 1
            shared_episode = self.meta_data['shared_episode']
            if debug:
                msg = 'global_step: {}, local_step: {}, episode: {}, reward: {}'
                print(msg.format(
                    shared_step,
                    global_step,
                    episode,
                    reward
                ))
            if end_episode is not None:
                end_episode(reward, shared_step, global_step, shared_episode, episode)

        self.trainers = []
        for i in range(n_threads):
            env = envs[i]
            agent = agents[i]
            trainer = Trainer(
                env=env,
                agent=agent,
                state_shape=state_shape,
                final_step=final_step,
                state_window=state_window,
                preprocess=preprocess,
                training=training,
                render=i == 0 and render,
                debug=False,
                before_action=_before_action,
                after_action=_after_action,
                end_episode=_end_episode
            )
            self.trainers.append(trainer)

    def start(self):
        sess = tf.get_default_session()
        coord = tf.train.Coordinator()
        # gym renderer is only available on the main thread
        render_trainer = self.trainers.pop(0)
        threads = []
        for i in range(len(self.trainers)):
            def run(index):
                with sess.as_default():
                    self.trainers[index].start()
            thread = threading.Thread(target=run, args=(i,))
            thread.start()
            threads.append(thread)
            time.sleep(0.1)
        render_trainer.start()
        coord.join(threads)
