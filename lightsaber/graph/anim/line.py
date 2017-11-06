from builtins import input
import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import subprocess
import argparse

class AnimatedLineGraph:
    def __init__(self, row, horizon, max_val=1.0):
        self.row = row
        self.horizon = horizon
        self.proc = subprocess.Popen(
            [
                'python', '-u', __file__,
                '--row', str(row),
                '--horizon', str(horizon),
                '--max', str(max_val)
            ],
            stdin=subprocess.PIPE)

    def update(self, values):
        data = {
            'values': values
        }
        self.proc.stdin.write(bytearray(json.dumps(data) + '\n', 'utf-8'))
        self.proc.stdin.flush()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--row', type=int, default=1)
    parser.add_argument('--horizon', type=int, default=1)
    parser.add_argument('--max', type=float, default=1.0)
    args = parser.parse_args()

    # initialize graph space
    x = np.arange(args.horizon)
    y = np.zeros((args.horizon), dtype=np.float32)
    y += args.max
    fig, axs = plt.subplots(args.row, 1)
    graphs = []
    for i in range(args.row):
        axs[i].set_title('index: ' + str(i))
        graphs.append(axs[i].plot(x, y, label=str(i)))

    def draw(i):
        data = json.loads(input())
        values = data['values']
        for i in range(args.row):
            value = values[i]
            colors = ['b' for j in range(args.horizon)]
            axs[i].cla()
            axs[i].plot(x, value, label=str(i))

    ani = animation.FuncAnimation(fig, draw, interval=1)
    plt.show()
