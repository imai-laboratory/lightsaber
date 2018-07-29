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
        fig, axs = plt.subplots(row, 1)
        self.fig = fig
        self.axs = axs
        x = np.arange(horizon)
        y = np.ones(horizon) * max_val
        self.lines = []
        fig.show()
        fig.canvas.draw()
        if row == 1:
            self.axs = axs = [axs]
        for i in range(row):
            self.lines.append(axs[i].plot(x, y, label=str(i), animated=True)[0])
        self.backgrounds = [fig.canvas.copy_from_bbox(ax.bbox) for ax in axs]

    def update(self, values):
        for i in range(self.row):
            self.fig.canvas.restore_region(self.backgrounds[i])
            self.axs[i].plot(np.arange((self.horizon)), values[i])
            self.lines[i].set_ydata(values[i])
            self.axs[i].draw_artist(self.lines[i])
            self.fig.canvas.blit(self.axs[i].bbox)
        self.fig.canvas.flush_events()
