#!/usr/bin/env python

from network import *
from random import randint

from time import time
from timer import Timer

from time import sleep

##################################################################
#Constant

time_window 	= 5*pow(10,5)
ex_neuron_nb	= 2 
nb_group	= 2 

nb_round 	= 5 

##################################################################
#Network creation

n = Network(time_window = time_window)


n.add_neuron(flag="receptive")
for i in xrange(ex_neuron_nb):
	n.add_neuron(flag=("activator_%s" % (i/(ex_neuron_nb/nb_group))))
	n.link_neurons(1,i+2)

##################################################################
#Experiment

t = Timer()
for i in xrange(nb_round):
	t.pick()
	neuron_set = randint(0,nb_group-1)
	n.impose_current_to_group(("activator_%s" % (neuron_set)), current_function =  spike_function(10))

	n.run()
	n.clean_current()
t.pick()
#t.prnt()
#n.draw_synaps_graph("dw_plus")
n.draw_synaps_graph("weight")
#n.draw_synaps_graph("u_barbar")
#n.draw_neuron_graph("potential")
#n.draw_neuron_graph("received_current", 1)
