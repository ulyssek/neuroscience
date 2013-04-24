#!/usr/bin/env python


from network import Network
from network import smart_plot

tab = []
for y in xrange (40):
	print y
	n = Network()
	n.add_neuron()
	n.add_neuron()
	n.link_neurons(1,2)
	n.impose_current(2)
	n.impose_current(1, current_function = (lambda x : 5*pow(10,-9) if x > y else 0))
	n.run()
	nb = len(n.synaps_data[0]["weight"])
	result = n.synaps_data[0]["weight"][nb-1];
	tab.append(result)

smart_plot([tab])

