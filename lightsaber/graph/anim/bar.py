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
        self.max_val = max_val
        self.bars = []
        x = np.arange(column)
        y = np.ones(column) * max_val
        fig.show()
        fig.canvas.draw()
        for i in range(row):
            axs[i].set_title('index: ' + str(i))
            self.bars.append(axs[i].bar(x, y, label=str(i), animated=True))
        self.backgrounds = [fig.canvas.copy_from_bbox(ax.bbox) for ax in axs]

    def update(self, values, hilights=[]):
        for i in range(self.row):
            self.fig.canvas.restore_region(self.backgrounds[i])
            value = values[i]
            for rect, v in zip(self.bars[i].patches, value):
                rect.set_height(v)
                self.axs[i].draw_artist(rect)
            colors = ['b' for j in range(self.column)]
            for hilight in hilights:
                row = hilight[0]
                column = hilight[1]
                if i == row:
                    colors[column] = 'r'
            for rect, color in zip(self.bars[i].patches, colors):
                rect.set_color(color)
            self.fig.canvas.blit(self.axs[i].bbox)
        self.fig.canvas.flush_events()
