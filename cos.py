#!/usr/bin/env python


from network import smart_plot
from math import cos

cos_factor 	= 5.
tau					= 50.


g = []
for i in xrange(500):
	g.append(cos(i/cos_factor))

f = [0]
for i in xrange(500):
	f.append(f[i] + (cos((i+1)/cos_factor)-f[i])/tau)


smart_plot([f,g])
