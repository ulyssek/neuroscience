#!/usr/bin/env python



from random import randint
from time import time
import numpy

from neuron import Neuron
from synaps import Synaps

import matplotlib.pyplot as plt


from __init__ import *


class Network():

	def __init__(self, time_window = 1000):

		#CONFIG VAR
		self._version = 2

		#CONSTANTS
		self._default_current_functions = []
		self._default_current_functions.append(lambda x : 9.5*pow(10,2))
		self._default_current_functions.append(lambda x : 9.5*pow(10,2) if x > 5 else 0)
		self._default_current_functions.append(lambda x : 10 if (x % 100 == 0) else 0)
		self._time_window = time_window # number of time step wich will be executed [step]
		
		#CLASS VARIABLES
		self.neuron_list 	= []
		self.synaps_list 	= []


		self.neuron_input_list 	= []

		self.flag_dict		= {} # This dictionary will contain several list of flaged neurons

		#DATA
		self.neuron_data 	= []
		self.synaps_data 	= []
		self.neuron_functions 	= {
				"potential"  		    	: Neuron.get_potential,
				"leak_current"              	: Neuron.get_leak_current,
				"threshold"                 	: Neuron.get_threshold,
				"hyperpolarisation_current" 	: Neuron.get_hyperpolarization_current,
				"exponential_thing"         	: Neuron.get_exponential_thing,
				"received_current"		: Neuron.get_received_current,
				}
		self.synaps_functions	= {
				"weight"		: Synaps.get_weight,
				"current"		: Synaps.get_current,
				"u_minus"		: Synaps.get_u_minus,
				"u_plus"		: Synaps.get_u_plus,
				"x"			: Synaps.get_x,
				"post_potential" 	: Synaps.get_post_synaptic_potential,
				"dw_plus" 		: Synaps.get_dw_plus,
				"dw_minus" 		: Synaps.get_dw_minus,
			}
		self.spike_number	= []

		#ANALYTICS VAR
		self.time_spent = {
			"run_neuron" 	: [],
			"run_synaps" 	: [],
			"collect_data" 	: [],
			}

	def run(self):
		for t in xrange(self._time_window):

			#Neurons update
			for neuron_id in xrange(self.get_neuron_number()):
				current = self.neuron_input_list[neuron_id](t)		
				self.neuron_list[neuron_id].run(current = current)

			#Synaps update
			for synaps in self.synaps_list:
				synaps.run()


			self.collect_data()


	##################################################################
	# GET FUNCTIONS
	def get_neuron_number(self):
		return len(self.neuron_list)
	
	def get_synaps_number(self):
		return len(self.synaps_list)

	def get_time_window(self):
		return self._time_window

	def get_last_value(self, item_id, value_key, item = 0):
		#item is either a neuron(0) or a synaps(1)
		if item == 0:
			value_list = self.neuron_data[item_id][value_key]
			return value_list[len(value_list)-1]
		elif item == 1:
			value_list = self.synaps_data[item_id][value_key]
			return value_list[len(value_list)-1]
		else:
			raise("Item value %s doesn't exist" % item)
		
		
	##################################################################
	# OTHER FUNCTIONS

	def get_neuron_dict(self):
		standard_neuron_dict = {}
		for key in self.neuron_functions.keys():
			standard_neuron_dict[key] = []
		return standard_neuron_dict
	
	def get_synaps_dict(self):
		standard_synaps_dict = {}
		for key in self.synaps_functions.keys():
			standard_synaps_dict[key] = []
		return standard_synaps_dict

	def collect_data(self):
		for neuron_id in xrange(self.get_neuron_number()):
			for key in self.neuron_functions.keys():
				foo = self.neuron_functions[key]
				self.neuron_data[neuron_id][key].append(foo(self.neuron_list[neuron_id]))
			if self.neuron_list[neuron_id].get_fired():
				self.spike_number[neuron_id] += 1
		for synaps_id in xrange(self.get_synaps_number()):
			for key in self.synaps_functions.keys():
				foo = self.synaps_functions[key]
				self.synaps_data[synaps_id][key].append(foo(self.synaps_list[synaps_id]))
			

	def print_error_message(self):
		print "Error, the neuron doesn't exist (number of neurons (%s))" % (self.get_neuron_number())

	def valid_id(self, neuron_id):
		return not (neuron_id > self.get_neuron_number() or neuron_id < 1)

	@classmethod
	def connect_neurons(cls, post_neuron, pre_neuron):
		synaps = Synaps(post_neuron, pre_neuron, version = 2)
		post_neuron.add_pre_synaps(synaps)
		pre_neuron.add_post_synaps(synaps)

		return synaps

	def link_neurons(self, id1, id2):
		nn = self.get_neuron_number()
		if not (self.valid_id(id1) or self.valid_id(id2)):
			self.print_error_message()
			return
		synaps = Network.connect_neurons(self.neuron_list[id1-1],self.neuron_list[id2-1])
		self.synaps_list.append(synaps)
		dico = self.get_synaps_dict()
		self.synaps_data.append(dico)

	def add_neuron(self, passive = False, flag = None):
		neuron_id = self.get_neuron_number()
		neuron = Neuron(version = 2, name = ("Neuron number %s" % (neuron_id+1)), passive = passive)
		self.neuron_list.append(neuron)
		dico = self.get_neuron_dict()
		self.neuron_data.append(dico)
		self.spike_number.append(0)
		self.neuron_input_list.append(lambda x : 0)
		if flag is not None:
			if not flag in self.flag_dict.keys():
				self.flag_dict[flag] = []
			self.flag_dict[flag].append(neuron_id)

	def impose_current(self, neuron_id, current_id = 1, current_function = None):
		if not self.valid_id(neuron_id): 
			self.print_error_message()
			return
		if current_function is None:
			current_function = self._default_current_functions[current_id-1]
		self.neuron_input_list[neuron_id-1] = current_function


	##################################################################
	# DRAWING FUNCTIONS

	def draw_synaps_graph(self, graph_key, synaps_id = None):
		if synaps_id is not None:
			smart_plot([self.synaps_data[synaps_id-1][graph_key]])
		else:
			smart_plot(map(lambda x : x[graph_key], self.synaps_data))

	def draw_neuron_graph(self, graph_key, neuron_id = None):
		if neuron_id is not None:
			smart_plot([self.neuron_data[neuron_id-1][graph_key]])
		else:
			smart_plot(map(lambda x : x[graph_key], self.neuron_data))



	# END OF CLASS
	##################################################################


def smart_plot(liste, x_list = None):
	color = ("r--", "b--", "g--", "y--", "o--")
	if x_list is None:
		args = ()
		for key in xrange(len(liste)):
			args += (range(len(liste[key])), liste[key], color[key])
		plt.plot(*args)
		plt.show()
	else:
		args = (x_list, liste, color[0])
		plt.plot(*args)
		plt.show()

def spike_function(frequency = 100, phase = 0):
	return lambda x : pow(10,7) if ( (x - (phase/DELTA_T)) % (frequency/DELTA_T) == 0 ) else 0

def constant_current_function(intensity = 9.5*pow(10,2), phase = 0):
	return lambda x : intensity if x > phase else 0

