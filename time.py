#!/usr/bin/env python




from network import Network


n = Network()

n.add_neuron(flags="z", neuron_number = 50)
n.add_neuron(flags="z")
n.add_neuron(flags="z")

n.connect_group("z")

n.impose_current(0)

n.launch()

#n.draw_neuron_graph("potential")
print map(lambda x: x.get_weight(), n.synaps_list)
#n.draw_synaps_graph("weight")

#n.draw_synaps_graph("u_minus")
#n.draw_neuron_graph("u_minus")
