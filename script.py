#!/usr/bin/env python


from network import Network
from network import spike_function
from time import time

time_1 = time()

n = Network()
n.add_neuron()
n.add_neuron()
n.link_neurons(2,1)

#n.impose_current(1)
#n.impose_current(2, current_id=2)
n.impose_current(2, current_function = spike_function(1000, 500))
n.impose_current(1, current_function = spike_function(1000, 0))

n.run()
print n.neuron_input_list
#print "input neuron 1 : %s " % n.neuron_input_list[1](1)
#print "input neuron 0 : %s " % n.neuron_input_list[0](1)
n.draw_synaps_graph("weight")
#n.draw_neuron_graph("potential")
print len(n.neuron_data[0]["potential"])
