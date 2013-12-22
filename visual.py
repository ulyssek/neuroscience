#!/usr/bin/env python

from network import *
from noise_generator import *
from random import randint

from time import time
from timer import Timer

from time import sleep


def visual_network(ex_nb=8, in_nb=2, nb_group = 8, save_data=False, nb_round=500, time_window=pow(10,2), data="classic"):
  
  constant = {
    "classic" :  {
      "ex_nb"             : 8,
      "in_bn"             : 2,
      "nb_group"          : 8,
      "neuron_per_group"  : 5.3,
      "noise_power"       : 5.5*pow(10,2),
      "uref_inter"        : 48,
      "uref_input"        : 48,
      "uref_inhib"        : 120,
    },
    "no_inhib" : {
      "ex_nb"             : 8,
      "in_bn"             : 0,
      "nb_group"          : 8,
      "neuron_per_group"  : 5.3,
      "noise_power"       : 5.5*pow(10,2),
      "uref_inter"        : 52,
      "uref_input"        : 52,
      "uref_inhib"        : 120,
    },
  }


  ##################################################################
  #Constant

  if data is not None:
    ex_neuron_number    = constant[data]["ex_nb"]
    inhib_neuron_number = constant[data]["in_bn"]
    nb_group            = constant[data]["nb_group"]
    neuron_per_group    = constant[data]["neuron_per_group"]
    noise_power         = constant[data]["noise_power"]
    uref_inter          = constant[data]["uref_inter"]
    uref_input          = constant[data]["uref_input"]
    uref_inhib          = constant[data]["uref_inhib"]


  """
  neuron_per_group    = 5.3 

  ex_neuron_number    = ex_nb 
  inhib_neuron_number  = in_nb
  """



  ##################################################################
  #Network creation

  noise_generator = NoiseGenerator(noise_power) 

  n = Network(time_window = time_window, save_data = save_data, noise_generator = noise_generator)


  for i in xrange(ex_neuron_number):
    n.add_neuron(flags=["receptive","exci"])
  if ex_neuron_number != 0:
    n.connect_group("receptive", synaps_flag=["inter neuron","plastic"], weight=0)

  for i in xrange(inhib_neuron_number):
    neuron_id = n.add_neuron(flags=["receptive","inhib"], inhib=True)
    n.link_neuron_to_group(neuron_id, "receptive",post=True,synaps_flags=["inter neuron","inhib","plastic"], weight = 5)
    n.link_neuron_to_group(neuron_id, "receptive",post=False,synaps_flags=["inter neuron","inhib","inhib_to_exci"], weight = 5, plasticity=False)

  for i in xrange(nb_group):
    neuron_id = n.add_neuron(flags=("activator %s" % i), neuron_number = neuron_per_group)
    if ex_neuron_number != 0:
      n.link_neuron_to_group(neuron_id,"exci", rand=True, post=False, synaps_flags=["input","exci"])
    """
    if inhib_neuron_number != 0:
      n.link_neuron_to_group(neuron_id,"inhib", rand=True, post=False, synaps_flags=["input","inhib"])
    """

  n.set_uref_square(uref_inter, "inter neuron")
  n.set_uref_square(uref_input, "input")
  n.set_max_weight(1, "inter neuron")
  try:
    n.set_uref_square(uref_inhib, ["inhib", "inter neuron"])
    n.set_max_weight(5, ["inhib", "inter neuron"])
  except KeyError:
    pass


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
  graph = lambda : n.draw_neuron_graph(["potential"], flags="receptive")
  n.add_graph(graph, name="stimulation")
  graph = lambda : n.draw_correlation("firing_rate", flags="receptive", smooth=True)
  n.add_graph(graph, name="correlation")

  ##################################################################
  #Experiment

  def experiment(trail_nb=nb_round):
    for i in xrange(trail_nb):
      neuron_set = randint(0,nb_group-1)
      n.impose_current_to_group(("activator %s" % (neuron_set)), current_function =  spike_function(10,random=True))

      n.run()
      n.clean_current()
    n.draw("all_weight")


  def learning():
    n.block_synaps("plastic")
    #n.set_noise(False)
    for i in xrange(int(4*nb_round)):
      neuron_set = randint(0,nb_group-1)
      n.impose_current_to_group(("activator %s" % (neuron_set)), current_function = spike_function(10))
      n.run()
      n.clean_current()
    n.block_synaps("plastic", block=False)
    n.draw("all_weight")
    n.switch("classic")
    #n.set_noise(True)
    n.launch()

  def stimulate(neuron_set=None):
    if neuron_set is None:
      for i in xrange(nb_group):
        stimulate(neuron_set=i)
    else:
      n.block_plasticity("plastic")
      n.impose_current_to_group(("activator %s" % (neuron_set)), current_function = spike_function(10))
      n.run()
      n.clean_current(flags=["activator %s" % (neuron_set)])
      n.block_plasticity("plastic", block=False)
    
  n.add_mode(name="learning")
  n.add_mode(name="stimulate")
  n.set_experiment(experiment)
  n.switch("stimulate")
  n.set_experiment(stimulate)
  n.switch("learning")
  n.set_experiment(learning)
    

  return n

n = visual_network()

#t.prnt()
#n.draw_synaps_graph("dw_plus")
#n.draw_synaps_graph(["weight"], flags="inter neuron")
#n.draw_synaps_graph(["weight"], flags=["neuron 1", "neuron 2", "neuron 3"])
#n.draw_synaps_graph("u_barbar")
#n.draw_neuron_graph("potential", 1)
#n.draw_neuron_graph("received_current", 1)
