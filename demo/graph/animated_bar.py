import numpy as np
from lightsaber.graph.anim import AnimatedBarGraph

bar = AnimatedBarGraph(3, 6)
for i in range(1000):
    data = np.random.rand(3, 6)
    bar.update(data.tolist())
