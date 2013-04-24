#!/usr/bin/env python

from neuron import Neuron


import matplotlib.pyplot as plt
import math



def main():

	TAU = 20
	current_function = lambda x : 1 if x % TAU == 0 else 0

	T_max = 50

	pre_neuron  = Neuron(0.001)

	final_tab = []
	tab = []

	for shift in xrange(20):
		result_array = []

		for t in xrange(T_max):
			pre_neuron.run(0, spike = current_function(t))
			if current_function(t+shift):
				result_array.append(-pre_neuron.get_firing_potential())
		final_tab.append(sum(result_array)/(len(result_array)+1))


	for shift in xrange(20):
		result_array = []

		for t in xrange(T_max):
			pre_neuron.run(0, spike = current_function(t))
			tab.append(pre_neuron.get_firing_potential())
			if current_function(t-shift):
				result_array.append(pre_neuron.get_firing_potential())


		final_tab.append(sum(result_array)/(len(result_array))+1)

	plt.plot(final_tab)
	plt.ylabel("percent potentiation")
	plt.show()
			
		

if __name__ == "__main__":
	main()
