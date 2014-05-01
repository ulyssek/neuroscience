#!/usr/bin/env python


from network import Network, spike_function


def net():
  n = Network()
  n.add_neuron(flags=["receptive","temoin"])
  n.add_neuron(flags=["receptive","test"])
  n.add_neuron(flags=["receptive","inhib"], inhib=True)
  n.add_neuron(flags=["input"])
  n.link_neurons(1,2,bidirectional=True)
  n.link_neuron_to_group(3, "receptive", post=False, weight=33)
  n.impose_current(3, current_function = spike_function(10))

  return n
