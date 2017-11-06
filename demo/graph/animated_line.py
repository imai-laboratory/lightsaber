import numpy as np
from lightsaber.graph.anim import AnimatedLineGraph

line = AnimatedLineGraph(3, 50)
for i in range(1000):
    data = np.random.rand(3, 50)
    line.update(data.tolist())
