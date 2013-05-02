#!/usr/bin/env python

from __init__ import DELTA_T
from network import Network
from network import spike_function
from network import constant_current_function
from network import smart_plot
from time import time

time_1 = time()


nb_step = 50 
weight_array = [] 
time_window = 3*pow(10,2)
frequency_array = []


"""
for i in xrange(nb_step):
	#constant_current = (6 + 6*i/float(nb_step))*pow(10,2)
	Hz_frequency = float(i)/nb_step*50+1
	frequency = int(pow(10,3)/Hz_frequency)
	n = Network(time_window = time_window)
	n.add_neuron()
	n.add_neuron()
	n.link_neurons(2,1)
	#n.impose_current(2, current_function = constant_current_function(intensity = constant_current))
	#n.impose_current(1, current_function = constant_current_function(intensity = constant_current, phase = 50))
	n.impose_current(2, current_function = spike_function(frequency, 0))
	n.impose_current(1, current_function = spike_function(frequency, 10))

	frequency_array.append(frequency)

	n.run()



	weight_array.append(n.get_last_value(0, "weight", item=1))
	#frequency_array.append(n.spike_number[1]/(float(time_window)*DELTA_T)*pow(10,3))
weight_array_LTD = weight_array

weight_array = []

for i in xrange(nb_step):
	#constant_current = (6 + 6*i/float(nb_step))*pow(10,2)
	Hz_frequency = float(i)/nb_step*50+1
	frequency = int(pow(10,3)/Hz_frequency)
	n = Network(time_window = time_window)
	n.add_neuron()
	n.add_neuron()
	n.link_neurons(2,1)
	#n.impose_current(2, current_function = constant_current_function(intensity = constant_current))
	#n.impose_current(1, current_function = constant_current_function(intensity = constant_current, phase = 50))
	n.impose_current(1, current_function = spike_function(frequency, 0))
	n.impose_current(2, current_function = spike_function(frequency, 10))

	frequency_array.append(frequency)

	n.run()



	weight_array.append(n.get_last_value(0, "weight", item=1))

weight_array_LTP = weight_array

smart_plot([weight_array_LTD, weight_array_LTP])
"""

def one_neuron_network(neuron_number = 1, option = 0, link_neurons = []):
	n = Network(time_window = time_window)
	for i in xrange(neuron_number):
		n.add_neuron()
	for n1, n2 in link_neurons:
		n.link_neurons(n1, n2)
	if option == 0:
		n.impose_current(1, current_function = spike_function())
	else:
		n.impose_current(1, current_function = constant_current_function())
	n.run()
	n.draw_neuron_graph("potential")

one_neuron_network()
"""
for i in xrange(nb_step):
	n = Network(time_window = time_window)
	n.add_neuron()
	n.add_neuron()
	n.link_neurons(2,1)
	n.impose_current(1, current_function = spike_function())
	n.impose_current(2, current_function = spike_function(phase = 15))

	n.run()

	weight_array.append(n.get_last_value(0, "weight", item=1))

#smart_plot([weight_array])

#smart_plot(weight_array, x_list = frequency_array)
#print n.neuron_input_list
#print "input neuron 1 : %s " % n.neuron_input_list[1](1)
#print "input neuron 0 : %s " % n.neuron_input_list[0](1)
#print n.get_last_value(0, "weight", item=1)
n.draw_synaps_graph("weight")
#n.draw_neuron_graph("potential")
#print n.spike_number
#print len(n.neuron_data[0]["potential"])

"""
"""
"""
