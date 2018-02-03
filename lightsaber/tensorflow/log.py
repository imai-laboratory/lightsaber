import tensorflow as tf


class TfBoardLogger:
    def __init__(self, writer):
        self.placeholders = {}
        self.summaries = {}
        self.writer = writer

    def register(self, name, dtype):
        placeholder = tf.placeholder(dtype, [], name=name)
        self.placeholders[name] = placeholder
        self.summaries[name] = tf.summary.scalar(name + '_summary', placeholder)

    def plot(self, name, value, step):
        sess = tf.get_default_session()
        placeholder = self.placeholders[name]
        summary = self.summaries[name]
        out, _ = sess.run(
            [summary, placeholder],
            feed_dict={placeholder: value}
        )
        self.writer(out, step)
