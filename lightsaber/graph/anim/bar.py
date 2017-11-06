from builtins import input
import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import subprocess
import argparse

class AnimatedBarGraph:
    def __init__(self, row, column, max_val=1.0):
        self.row = row
        self.column = column
        fig, axs = plt.subplots(row, 1)
        self.fig = fig
        self.axs = axs
        self.bars = []
        x = np.arange(column)
        y = np.zeros(column)
        for i in range(row):
            axs[i].set_title('index: ' + str(i))
            self.bars.append(axs[i].bar(x, y, label=str(i)))

    def update(self, values, hilights=[]):
        for i in range(self.row):
            value = values[i]
            self.axs[i].cla()
            bars = self.axs[i].bar(np.arange(self.column), value)
            colors = ['b' for j in range(self.column)]
            for hilight in hilights:
                row = hilight[0]
                column = hilight[1]
                if i == row:
                    colors[column] = 'r'
            for bar, color in zip(bars, colors):
                bar.set_color(color)
        plt.pause(0.0001)
        plt.draw()
