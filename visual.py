#!/usr/bin/env python

from network import *
from noise_generator import *
from random import randint
from math_tools import *

from time import time
from timer import Timer

from time import sleep

from radar_chart import *


def visual_network(save_data=False, nb_round=500, time_window=pow(10,2), data="classic",draw=True,test=False):
  """
  mods list : resting, classic, learning, stimulate, exp_time 
  drawings : 
    0 : connection matrice inter neuron
    1 : connection matrice
    2 : stimulation graph
    3 : correlation matrice
  """
  if test:
    nb_round = 3

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
      "max_w_inhib"       : 5,
      "max_w_exci"        : 1,
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
      "max_w_inhib"       : 5,
      "max_w_exci"        : 1,
    },
  }

  CARD = ["l","N","NE","E","SE","S","SW","W","NW"]

  ##################################################################
  #Constants

  if data is not None:
    ex_neuron_number    = constant[data]["ex_nb"]
    inhib_neuron_number = constant[data]["in_bn"]
    nb_group            = constant[data]["nb_group"]
    neuron_per_group    = constant[data]["neuron_per_group"]
    noise_power         = constant[data]["noise_power"]
    uref_inter          = constant[data]["uref_inter"]
    uref_input          = constant[data]["uref_input"]
    uref_inhib          = constant[data]["uref_inhib"]
    max_w_inhib         = constant[data]["max_w_inhib"]
    max_w_exci          = constant[data]["max_w_exci"]


  ##################################################################
  #Network creation

  noise_generator = NoiseGenerator(noise_power) 

  n = Network(time_window = time_window, save_data = save_data, noise_generator = noise_generator)

  n.visual_constant = constant[data]

  for i in xrange(ex_neuron_number):
    n.add_neuron(flags=["receptive","exci"])
  if ex_neuron_number != 0:
    n.connect_group("receptive", synaps_flag=["inter neuron","plastic","exci"], weight=0)

  for i in xrange(inhib_neuron_number):
    neuron_id = n.add_neuron(flags=["receptive","inhib"], inhib=True)
    n.link_neuron_to_group(neuron_id, "receptive",post=True,synaps_flags=["inter neuron","inhib","plastic"], weight = 5)
    n.link_neuron_to_group(neuron_id, "receptive",post=False,synaps_flags=["inter neuron","inhib","inhib_to_exci"], weight = 5, plasticity=False)

  for i in xrange(nb_group):
    neuron_id = n.add_neuron(flags=[("activator %s" % i),"activator"], neuron_number = neuron_per_group)
    if ex_neuron_number != 0:
      n.link_neuron_to_group(neuron_id,"exci", rand=True, post=False, synaps_flags=["input","exci"])
    """
    if inhib_neuron_number != 0:
      n.link_neuron_to_group(neuron_id,"inhib", rand=True, post=False, synaps_flags=["input","inhib"])
    """

  n.set_uref_square(uref_inter, "inter neuron")
  n.set_uref_square(uref_input, "input")
  n.set_max_weight(max_w_exci, "inter neuron")
  try:
    n.set_uref_square(uref_inhib, ["inhib", "inter neuron"])
    n.set_max_weight(max_w_inhib, ["inhib", "inter neuron"])
  except KeyError:
    pass


  ##################################################################
  #Drawings

  graph = lambda : n.draw_synaps_graph(["weight"], flags="inter neuron")
  n.add_graph(graph, name="inter")
  graph = lambda : n.draw_synaps_graph(["weight"], flags="input")
  n.add_graph(graph, name="input")
  graph = lambda : n.draw_weight(flag="receptive")
  n.add_graph(graph, name="square")
  graph = lambda : n.draw_weight(range(n.get_neuron_number()),title="Connectivity Matrix : Whole Network",xlabel="Neuron number", ylabel="Neuron number",vmin=0,vmax=10,color_bar_label="Connection strength")
  n.add_graph(graph, name="all_weight")
  graph = lambda : n.draw_neuron_graph(["potential"], flags="receptive")
  n.add_graph(graph, name="stimulation")
  graph = lambda : n.draw_correlation("firing_rate", flags="receptive", smooth=True, reverse=True,name="Correlation matrix",xlabel="Cell number",ylabel="Cell number",vmax=0.4,vmin=0)
  n.add_graph(graph, name="correlation")
  graph = lambda : n.draw_weight(pre_list=n.get_neuron_id_from_flags("activator"),post_list=n.get_neuron_id_from_flags("receptive"),xlabel="Activator Neurons",ylabel="Inter Neurons",vmin=0,vmax=10,title="Connectivity Matrix : Activator Neurons to Inter Neurons",color_bar_label="Connection strength",x_stick_labels=CARD)
  n.add_graph(graph, name="activator_connectivity")
  graph = lambda : n.draw_weight(neuron_list=n.get_neuron_id_from_flags("receptive"),xlabel="Inter Neurons",ylabel="Inter Neurons",vmin=0,vmax=5,title="Connectivity Matrix : Inter Neurons",color_bar_label="Connection strengh")
  n.add_graph(graph, name="receptive_connectivity")

  ##################################################################
  #Experiments

  def experiment(trail_nb=nb_round,print_keeps=False,keep_flags=None,thr=0.5,draw=draw,**kwargs):
    time_array = []
    for i in xrange(trail_nb):
      neuron_set = randint(0,nb_group-1)
      n.impose_current_to_group(("activator %s" % (neuron_set)), current_function =  spike_function(10,random=True))

      n.run(**kwargs)
      if print_keeps:
        n.keep_connected("relearning",True,flags=keep_flags)
        s = n.compare_keeps("relearning","stable")
        time_array.append(s)
      n.clean_current()
    if draw:
      n.draw("all_weight")
    if print_keeps:
      return time_array


  def similarity():
    n.keep_connected("stable",flags=["inter neuron","exci"])
    n.switch("classic")
    result = n.launch(print_keeps=True,keep_flags=["inter neuron","exci"])
    return result

  def learning(draw=draw):
    n.block_synaps("plastic")
    #n.set_noise(False)
    for i in xrange(int(4*nb_round)):
      neuron_set = randint(0,nb_group-1)
      n.impose_current_to_group(("activator %s" % (neuron_set)), current_function = spike_function(10))
      n.run()
      n.clean_current()
    n.block_synaps("plastic", block=False)
    if draw:
      n.draw("all_weight")
    n.switch("classic")
    #n.set_noise(True)
    n.launch()

  def stimulate(neuron_set=None, neuron_id=None, flags=None):
    if neuron_set is None:
      if neuron_id is not None:
        result  = [[]]
      elif flags is not None:
        result  = map(lambda x : [], range(len(n.get_neuron_id_from_flags(flags))))
      for i in xrange(nb_group):
        stimulate(neuron_set=i)
        if neuron_id is not None:
          result[0].append(n.neuron_data[neuron_id]["firing_rate"][-1])
        elif flags is not None:
          count = 0
          for j in n.get_neuron_id_from_flags(flags):
            result[count].append(n.neuron_data[j]["firing_rate"][-1])
            count += 1
      try:
        result = map(lambda x : map(lambda y : max(y,0.005),x),result)
        return result
      except:
        pass
    else:
      n.block_plasticity("plastic")
      n.impose_current_to_group(("activator %s" % (neuron_set)), current_function = spike_function(10))
      n.run()
      n.clean_current(flags=["activator %s" % (neuron_set)])
      n.block_plasticity("plastic", block=False)

  def exp_timer():#**kwargs):
    n.switch("classic")
    n.keep_connected(keep_name="stable", flags=["inter neuron","exci"])
    n.reinitialize_weights(flags=["inter neuron","exci"])
    time_array = n.launch(print_keeps=True,keep_flags=["inter neuron", "exci"])#,**kwargs)
    n.switch("exp_time")
    return time_array
    

  def stimulation_radar():
    #Preparing the experiment
    n.switch("stimulate")
    n.save_data(True)
    n.clean_data()
    #Gathering Data
    exci_data = n.launch(flags="exci")
    n.clean_data()
    inhib_data = n.launch(flags="inhib")
    #building radars  
    radars = Radar.RadarsFromList(exci_data)
    i_radars = Radar.RadarsFromList(inhib_data)
    #ploting radars
    for radar in radars:
      radar.plot(legend=False,fig_title="Connectivity Graphic")
    for radar in i_radars:
      radar.plot(legend=False,fig_title="Connectivity Inhib")


  def correlation():
    n.switch("stimulate")
    n.save_data(True)
    n.clean_data()
    n.launch()
    n.draw("correlation")
    n.switch("resting")
    n.clean_data()
    for i in xrange(100):
      n.launch()
    n.draw("correlation")

    

  n.add_mode(name="learning")
  n.add_mode(name="stimulate")
  n.add_mode(name="exp_time")
  n.add_mode(name="stim_radar")
  n.add_mode(name="similarity")
  n.add_mode(name="correlation")
  n.set_experiment(experiment)
  n.switch("stimulate")
  n.set_experiment(stimulate)
  n.switch("stim_radar")
  n.set_experiment(stimulation_radar)
  n.switch("exp_time")
  n.set_experiment(exp_timer)
  n.switch("similarity")
  n.set_experiment(similarity)
  n.switch("correlation")
  n.set_experiment(correlation)
  n.switch("learning")
  n.set_experiment(learning)
    

  return n

n = visual_network()

#n.draw_synaps_graph("dw_plus")
#n.draw_synaps_graph(["weight"], flags="inter neuron")
#n.draw_synaps_graph(["weight"], flags=["neuron 1", "neuron 2", "neuron 3"])
#n.draw_synaps_graph("u_barbar")
#n.draw_neuron_graph("potential", 1)
#n.draw_neuron_graph("received_current", 1)
