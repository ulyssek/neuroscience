#!/usr/bin/env python

from network import *
from random import randint

from time import time
from timer import Timer

from time import sleep


def visual_network(ex_nb=3, in_nb=1, nb_group = 5, save_data=True, nb_round=100, time_window=5*pow(10,2)):

	##################################################################
	#Constant

	neuron_per_group		= 33

	ex_neuron_number		= ex_nb 
	inhib_neuron_number	= in_nb


	ex_nb_2	= 4


	##################################################################
	#Network creation

	n = Network(time_window = time_window, save_data = save_data)


	for i in xrange(ex_neuron_number):
		n.add_neuron(flags="receptive")
	n.connect_group("receptive", synaps_flag="inter neuron")

	for i in xrange(inhib_neuron_number):
		neuron_id = n.add_neuron(flags=["receptive","inhib"], inhib=True)
		n.link_neuron_to_group(neuron_id, "receptive",bidirectional=True,synaps_flags=["inter neuron","inhib"])


	for i in xrange(nb_group):
		neuron_id = n.add_neuron(flags=("activator %s" % i), neuron_number = neuron_per_group)
		n.link_neuron_to_group(neuron_id,"receptive", rand=True, post=False, synaps_flags="input")


	"""
	for i in xrange(ex_nb_2):
		neuron_id = n.add_neuron(flags="third line")
		n.link_neuron_to_group(neuron_id, "receptive", rand=True, post=True, synaps_flags="second wave", synaps_multiplicator=neuron_per_group)
	n.connect_group("third line", synaps_flag="third inter")
	"""
		


	


	##################################################################
	#Experiment

	def experiment():
		for i in xrange(nb_round):
			neuron_set = randint(0,nb_group-1)
			n.impose_current_to_group(("activator %s" % (neuron_set)), current_function =  spike_function(10))

			n.run()
			n.clean_current()
	n.set_experiment(experiment)
		
	##################################################################
	#Drawing

	graph = lambda : n.draw_synaps_graph(["weight"], flags="inter neuron")
	n.add_graph(graph, name="inter")
	graph = lambda : n.draw_synaps_graph(["weight"], flags="input")
	n.add_graph(graph, name="input")
	graph = lambda : n.draw_weight(flag="receptive")
	n.add_graph(graph, name="square")
	graph = lambda : n.draw_weight(range(n.get_neuron_number()))
	n.add_graph(graph, name="all_weight")

	return n


#t.prnt()
#n.draw_synaps_graph("dw_plus")
#n.draw_synaps_graph(["weight"], flags="inter neuron")
#n.draw_synaps_graph(["weight"], flags=["neuron 1", "neuron 2", "neuron 3"])
#n.draw_synaps_graph("u_barbar")
#n.draw_neuron_graph("potential", 1)
#n.draw_neuron_graph("received_current", 1)
