from collections import deque
import tensorflow as tf
import numpy as np
import copy
import time
import threading
import copy


class AgentInterface:
    def act(self, state, reward, training):
        raise NotImplementedError()

    def stop_episode(state, reward, training):
        raise NotImplementedError()

class Trainer:
    def __init__(self,
                env,
                agent,
                state_shape=[84, 84],
                final_step=1e7,
                state_window=1,
                training=True,
                render=False,
                debug=True,
                before_action=None,
                after_action=None,
                end_episode=None):
        self.env = env
        self.final_step = final_step
        self.init_states = deque(
            np.zeros(
                [state_window] + state_shape,
                dtype=np.float32
            ).tolist(),
            maxlen=state_window
        )
        self.agent = agent
        self.training = training
        self.render = render
        self.debug = debug
        self.before_action = before_action
        self.after_action = after_action
        self.end_episode = end_episode

        # counters
        self.global_step = 0
        self.local_step = 0
        self.episode = 0
        self.sum_of_rewards = 0

    def move_to_next(self, states, reward):
        states = np.array(list(states))
        # take next action
        action = self.agent.act(
            states,
            reward,
            self.training
        )
        state, reward, done, info = self.env.step(action)
        # render environment
        if self.render:
            self.env.render()
        return state, reward, done, info

    def finish_episode(self, states, reward):
        states = np.array(list(states))
        self.agent.stop_episode(
            states,
            reward,
            self.training
        )
        if self.debug:
            self.print_info()

    def start(self):
        while True:
            self.local_step = 0
            self.sum_of_rewards = 0
            reward = 0
            done = False
            state = self.env.reset()
            states = copy.deepcopy(self.init_states)
            while True:
                states.append(state.tolist())
                # episode reaches the end
                if done:
                    self.episode += 1
                    # callback at the end of episode
                    if self.end_episode is not None:
                        self.end_episode(
                            self.sum_of_rewards,
                            self.global_step,
                            self.episode
                        )
                    self.finish_episode(states, reward)
                    break

                # callback before taking action
                if self.before_action is not None:
                    self.before_action(
                        states,
                        self.global_step,
                        self.local_step
                    )
                # take action and move to next state
                state, reward, done, info = self.move_to_next(states, reward)
                # callback after taking action
                if self.after_action is not None:
                    self.after_action(
                        states,
                        reward,
                        self.global_step,
                        self.local_step
                    )

                self.sum_of_rewards += reward
                self.global_step += 1
                self.local_step += 1

            if self.global_step > self.final_step:
                return

    def print_info(self):
        print('step: {}, episode: {}, reward: {}'.format(
            self.global_step,
            self.episode,
            self.sum_of_rewards
        ))

class BatchTrainer(Trainer):
    def __init__(self,
                env, # BatchEnvWrapper
                agent,
                state_shape=[84, 84],
                final_step=1e7,
                state_window=1,
                training=True,
                render=False,
                debug=True,
                before_action=None,
                after_action=None,
                end_episode=None):
        super().__init__(
            env=env,
            agent=agent,
            state_shape=state_shape,
            final_step=final_step,
            state_window=state_window,
            training=training,
            render=render,
            debug=debug,
            before_action=before_action,
            after_action=after_action,
            end_episode=end_episode
        )

        # overwrite global_step
        self.global_step = 0

    # overwrite
    def start(self):
        while True:
            # values for the number of n environment
            n_envs = self.env.get_num_of_envs()
            self.local_step = [0 for _ in range(n_envs)]
            self.sum_of_rewards = [0 for _ in range(n_envs)]
            rewards = [0 for _ in range(n_envs)]
            dones = [False for _ in range(n_envs)]
            states = self.env.reset()
            queue_states = [copy.deepcopy(self.init_states) for _ in range(n_envs)]
            while True:
                for i, state in enumerate(states):
                    queue_states[i].append(state.tolist())
                np_states = np.array(list(map(lambda s: list(s), queue_states)))

                # episode reaches the end
                if False not in dones:
                    self.finish_episode(np_states, rewards)
                    break

                # callback before taking action
                if self.before_action is not None:
                    for i in range(n_envs):
                        self.before_action(
                            states[i],
                            self.global_step,
                            self.local_step[i]
                        )
                # backup episode status
                prev_dones = dones
                states, rewards, dones, infos = self.move_to_next(np_states, rewards)

                # callback before taking action
                if self.after_action is not None:
                    for i in range(n_envs):
                        self.after_action(
                            states[i],
                            rewards[i],
                            self.global_step,
                            self.local_step[i]
                        )

                # check ended episodes
                for i in range(n_envs):
                    if not prev_dones[i] and dones[i]:
                        self.episode += 1
                        # callback at the end of episode
                        if self.end_episode is not None:
                            self.end_episode(
                                self.sum_of_rewards[i],
                                self.global_step,
                                self.episode
                            )

                for i in range(n_envs):
                    self.sum_of_rewards[i] += rewards[i]
                    if not dones[i]:
                        self.global_step += 1
                        self.local_step[i] += 1

            if self.global_step > self.final_step:
                return

    # overwrite
    def print_info(self):
        for i in range(self.env.get_num_of_envs()):
            print('step: {}, episode: {}, reward: {}'.format(
                self.global_step,
                self.episode + i + 1,
                self.sum_of_rewards[i]
            ))

class AsyncTrainer:
    def __init__(self,
                envs,
                agents,
                state_shape=[84, 84],
                final_step=1e7,
                state_window=1,
                training=True,
                render=False,
                debug=True,
                before_action=None,
                after_action=None,
                end_episode=None,
                n_threads=10):
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
                end_episode(
                    reward,
                    shared_step,
                    global_step,
                    shared_episode,
                    episode
                )

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
