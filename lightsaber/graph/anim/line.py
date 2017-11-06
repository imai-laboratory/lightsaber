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

    def update(self, values):
        for i in range(self.row):
            self.axs[i].cla()
            self.axs[i].plot(np.arange((self.horizon)), values[i])
        plt.pause(0.001)
        plt.draw()
