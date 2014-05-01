#!/usr/bin/env python



"""
Show how to modify the coordinate formatter to report the image "z"
value of the nearest pixel given x and y
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

X = np.random.rand(5,3)
X = ([[1,2,3],[3,4,5],[4,5,6],[1,2,3],[1,4,5]])

fig = plt.figure()
ax = fig.add_subplot(111)
ax.imshow(X, interpolation="nearest")

plt.show()

