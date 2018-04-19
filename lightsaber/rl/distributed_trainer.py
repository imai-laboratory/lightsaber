import tensorflow as tf
import numpy as np

from multiprocessing import Process
from lightsaber.rl.trainer import Trainer


def create_cluster(n_workers):
    spec = {}

    host = '127.0.0.1'
    port = 12222

    # parameter server
    spec['ps'] = ['{}:{}'.format(host, port)]
    port += 1

    # worker server
    workers = []
    for i in range(n_workers):
        workers.append('{}:{}'.format(host, port))
        port += 1
    spec['worker'] = workers

    return tf.train.ClusterSpec(spec).as_cluster_def()


class DistributedTrainer:
    def __init__(self,
                 env_generator,
                 agent_generator,
                 logdir,
                 outdir,
                 render=False,
                 n_workers=8,
                 final_step=1e7,
                 state_window=1,
                 state_shape=[84, 84],
                 before_action=None,
                 after_action=None,
                 end_episode=None):
        self.render = render
        self.n_workers = n_workers
        self.cluster = create_cluster(n_workers)
        self.env_generator = env_generator
        self.agent_generator = agent_generator
        self.logdir = logdir
        self.outdir = outdir
        self.final_step = final_step
        self.state_window = state_window
        self.state_shape = state_shape
        self.before_action = before_action
        self.after_action = after_action
        self.end_episode = end_episode

    def _create_hooks(self):
        return [
            tf.train.StopAtStepHook(last_step=self.final_step)
        ]

    def create_parameter_server(self):
        server = tf.train.Server(
            self.cluster, job_name="ps", task_index=0,
            config=tf.ConfigProto(device_filters=["/job:ps"]))
        server.join()

    def create_worker_server(self, index):
        config = tf.ConfigProto(
            intra_op_parallelism_threads=1, inter_op_parallelism_threads=2)
        server = tf.train.Server(
            self.cluster, job_name="worker", task_index=index, config=config)

        # shared step counter and episode counter
        with tf.device(tf.train.replica_device_setter(cluster=self.cluster)):
            shared_step = tf.train.create_global_step()
            inc_step_op = shared_step.assign_add(1)
            shared_episode = tf.get_variable(
                'global_episode', [], tf.int32,
                initializer=tf.constant_initializer(0, dtype=tf.int32),
                trainable=False)
            inc_episode_op = shared_episode.assign_add(1)

        def _before_action(state, global_step, local_step):
            shared_step_val = shared_step.eval(session=self.sess)
            if self.before_action is not None:
                self.before_action(
                    state, shared_step_val, global_step, local_step)

        def _after_action(state, reward, global_step, local_step):
            shared_step_val = inc_episode_op.eval(session=self.sess)
            if self.after_action is not None:
                self.after_action(
                    state, reward, shared_step_val, global_step, local_step)

        def _end_episode(reward, global_step, episode):
            shared_step_val = shared_step.eval(session=self.sess)
            shared_episode_val = inc_episode_op.eval(session=self.sess)
            msg = 'worker: {}, global_step: {}, local_step: {}, episode: {}, reward: {}'
            print(msg.format(
                index, shared_step_val, global_step, shared_episode_val, reward))
            if self.end_episode is not None:
                self.end_episode(
                    reward, shared_step_val, global_step,
                    shared_episode_val, episode)

        trainer = Trainer(
            env=self.env_generator(index, self.cluster),
            agent=self.agent_generator(index, self.cluster),
            state_shape=self.state_shape,
            final_step=self.final_step,
            state_window=self.state_window,
            render=index == 0 and self.render,
            debug=False,
            before_action=_before_action,
            after_action=_after_action,
            end_episode=_end_episode,
            is_finished=lambda s: False
        )

        # create session
        sess_config = tf.ConfigProto(
            device_filters=['/job:ps', '/job:worker/task:{}/cpu:0'.format(index)])
        self.sess = tf.train.MonitoredTrainingSession(
            master=server.target,
            is_chief=index == 0,
            checkpoint_dir=self.outdir,
            config=sess_config
        )
        self.sess.__enter__()

        #sess.run(tf.initialize_all_variables())

        trainer.start()

    def start(self):
        # parameter server process
        ps = Process(target=self.create_parameter_server)
        ps.start()

        # worker server processes
        workers = []
        for i in range(self.n_workers):
            ws = Process(target=self.create_worker_server, args=(i,))
            ws.start()
            workers.append(ws)

        for ws in workers:
            ws.join()
        ps.join()
