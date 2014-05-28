#!/usr/bin/env python
#-*-coding:utf-8-*-



from timer import Timer
from random import randint
import numpy

from neuron           import Neuron
from fake_neuron      import FakeNeuron
from synaps           import Synaps
from noise_generator  import NoiseGenerator
import math_tools


from numpy.random import normal, poisson


import matplotlib.pyplot as plt
import matplotlib.colors as clr
import matplotlib.cm


from __init__ import *


class Network():

  def __init__(self, time_window = 1000, save_data = True, noise_generator = None):

    #CONFIG VAR
    self._version    = 2
    self._mode      = "classic"
    self._save_data = save_data

    #CONSTANTS
    self._default_current_functions = []
    self._default_current_functions.append(lambda x : 9.5*pow(10,2))
    self._default_current_functions.append(lambda x : 9.5*pow(10,2) if x > 5 else 0)
    self._default_current_functions.append(lambda x : 10 if (x % 100 == 0) else 0)
    self._time_window   =  {"classic":time_window,"resting":time_window} # number of time step wich will be executed [step]
    
    #CLASS VARIABLES
    self.neuron_list  = []
    self.synaps_list  = []


    self.neuron_input_list  = {"classic":[],"resting":[]}
    self.neuron_noise_list = []

    if noise_generator is None:
      self.default_noise_generator = NoiseGenerator(0)
    else:
      self.default_noise_generator = noise_generator

    self._noisy           = True
    self.saves            = {}
    self._keeps           = {}
    self.neuron_flag_dict = {}     # This dictionary will contain several list of flaged neurons
    self.synaps_flag_dict = {}     # This dictionary will contain several list of flaged synaps

    self.experiment    = {     # default function
        "classic"  : self.run,
        "resting"  : self.run,
        }
    self._graph_dict  = {}     # This dictionary will contain all the graph functions the user will draw

    #DATA
    self.neuron_data   = []    # List of neuron_function dictionary. All the dictionary will contain every single data
    self.synaps_data   = []
    self.neuron_functions   = {
        "potential"                 : Neuron.get_potential,
        "leak_current"              : Neuron.get_leak_current,
        "threshold"                 : Neuron.get_threshold,
        "hyperpolarisation_current" : Neuron.get_hyperpolarization_current,
        "exponential_thing"         : Neuron.get_exponential_thing,
        "received_current"          : Neuron.get_received_current,
        "firing_rate"               : Neuron.get_firing_rate,
        "u_minus"                   : Neuron.get_u_minus,
        "u_plus"                    : Neuron.get_u_plus,
        "x"                         : Neuron.get_x,
        "u_barbar"                  : Neuron.get_u_barbar,
        }
    self.synaps_functions  = {
        "weight"          : Synaps.get_weight,
        "current"         : Synaps.get_current,
        "u_minus"         : Synaps.get_u_minus,
        "u_plus"          : Synaps.get_u_plus,
        "x"               : Synaps.get_x,
        "post_potential"  : Synaps.get_post_synaptic_potential,
        "dw_plus"         : Synaps.get_dw_plus,
        "dw_minus"        : Synaps.get_dw_minus,
        "u_barbar"        : Synaps.get_u_barbar,
      }
    self.spike_number  = []

    #ANALYTICS VAR
    self.time_spent = {
      "run_neuron"     : [],
      "run_synaps"     : [],
      "collect_data"   : [],
      }

  def run(self, time_window = None):
    if time_window is None:
      time_window = self._time_window[self._mode]
    #ti = Timer()
    for t in xrange(int(time_window)):

      #ti.pick()
      #Neurons update
      for neuron_id in xrange(self.get_neuron_number()):
        current = self.neuron_input_list[self._mode][neuron_id](t)    
        if self._noisy:
          current += self.neuron_noise_list[neuron_id].get_current(t)
        self.neuron_list[neuron_id].run(current = current)
      #ti.pick("neuron update")

      #Synaps update
      for synaps in self.synaps_list:
        synaps.run()
      #ti.pick("synaps_update")


      if self._save_data:
        self.collect_data()
      #ti.pick("collect data")
      #ti.save()
      #ti.clean()
    #ti.prnt(1)

  def launch(self, **kwargs):
    return self.experiment[self._mode](**kwargs)

  ##################################################################
  # SET FUNCTIONS
  def set_experiment(self, foo):
    self.experiment[self._mode] = foo

  def add_graph(self, graph, name=None):
    if name is None:
      name = "Graph number %s" % len(self._graph_dict.keys())
    if name in self._graph_dict.keys():
      raise Exception("the graph name already exists")
    self._graph_dict[name] = graph


  ##################################################################
  # MODE FUNCTIONS

  def add_mode(self, name=None, time_window = None):
    if time_window is None:
      time_window = self._time_window["classic"]
    if name is None:
      name = "Mode number %s" % len(self.neron_input_list.keys())
    if name in self.neuron_input_list.keys():
      raise Exception("the mode name already exists")

    self.neuron_input_list[name] = []
    for key in xrange(self.get_neuron_number()):
      self.neuron_input_list[name].append(lambda x : 0)

    self._time_window[name] = time_window

  def switch(self, name):
    if type(name) == int:
      name = self.neuron_input_list.keys()[name]
    self._mode = name
    if name not in self.neuron_input_list.keys():
      print "WARNING, name not known"

  def save_data(self,boule=None):
    if boule is not None:
      self._save_data =boule
    else:
      self._save_data = not self._save_data

  def set_noise(self, boule=True):
    self._noisy = boule
    

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
      return value_list[len(value_list)]
    elif item == 1:
      value_list = self.synaps_data[item_id][value_key]
      return value_list[len(value_list)]
    else:
      raise("Item value %s doesn't exist" % item)

  def get_current_mode(self):
    return self._mode

  def get_mode_list(self):
    for name in self._time_window.keys():
      print name

  def get_synaps_list(self):
    for synaps in self.synaps_list:
      print synaps.get_name()

  def get_uref(self):
    for synaps in self.synaps_list:
      print "%s : %s" % (synaps.get_name(), synaps.get_uref_square())

  def get_weight(self, flags=None):
    if flags is None:
      synaps_list = self.synaps_list
    else:
      synaps_list = self.get_synaps_from_flags(flags)
    weights = map(lambda x : x.get_weight(), synaps_list)
    return weights

  def get_neuron_from_flags(self, flags):
    if type(flags) != list:
      flags = [flags]
    boule = True 
    for flag in flags:
      temp_list = map(lambda x : self.neuron_list[x], self.neuron_flag_dict[flag])
      if boule:
        neuron_list = set(temp_list)
        boule = False
      else:
        neuron_list = set.intersection(neuron_list, temp_list)
    return list(set(neuron_list))

  def get_neuron_id_from_flags(self, flags):
    if type(flags) != list:
      flags = [flags]
    neuron_list = []
    boule = True
    for flag in flags:
      temp_list = self.neuron_flag_dict[flag]
      if boule:
        neuron_list = set(temp_list)
        boule = False
      else:
        neuron_list = set.intersection(neuron_list, temp_list)
    return list(set(neuron_list))


  def get_synaps_from_flags(self, flags):
    synaps_ids = self.get_synaps_id_from_flags(flags)
    return map(lambda x : self.synaps_list[x], synaps_ids)
    """
    if type(flags) != list:
      flags = [flags]
    synaps_list = set()
    boule = True
    for flag in flags:
      temp_list = map(lambda x : self.synaps_list[x], self.synaps_flag_dict[flag])
      if boule:
        boule = False
        synaps_list = set(temp_list)
      else:
        synaps_list = set.intersection(synaps_list, temp_list)
    return list(set(synaps_list))
    """

  def get_synaps_id_from_flags(self, flags):
    if type(flags) != list:
      flags = [flags]
    synaps_list = set()
    boule = True
    for flag in flags:
      temp_list = self.synaps_flag_dict[flag]
      if boule:
        boule = False
        synaps_list = set(temp_list)
      else:
        synaps_list = set.intersection(synaps_list, temp_list)
    return list(set(synaps_list))
    
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
    return not (neuron_id > self.get_neuron_number() or neuron_id < 0)


  ##################################################################
  # ADDING NEURONS AND SYNAPS TO THE NETWORK 

  @classmethod
  def connect_neurons(cls, post_neuron, pre_neuron,weight, name=None, synaps_multiplicator=1, plasticity = True):
    synaps     = Synaps(post_neuron, pre_neuron, version = 2, weight = weight, name=name, inhib=pre_neuron.get_inhib(), synaps_multiplicator=synaps_multiplicator, plasticity = plasticity)
    post_neuron.add_pre_synaps(synaps)
    pre_neuron.add_post_synaps(synaps)

    return synaps

  def link_neurons(self, id1, id2,
                  rand                  = False,
                  flags                  = None, 
                  bidirectional          = False,
                  weight                =  None,
                  synaps_multiplicator  = 1,
                  plasticity            = True
                  ):
    if bidirectional:
      s1 = self.link_neurons(id1, id2, rand=rand, flags=flags, weight=weight, plasticity=plasticity)
      s2 = self.link_neurons(id2, id1, rand=rand, flags=flags, weight=weight, plasticity=plasticity)
      return (s1,s2)
    else:
      nn = self.get_neuron_number()
      synaps_id = self.get_synaps_number()
      if not (self.valid_id(id1) or self.valid_id(id2)):
        self.print_error_message()
        return
      if rand:
        weight = normal(1500,1200)*0.5/1500 
      else:
        weight = weight
      synaps = Network.connect_neurons(self.neuron_list[id1],self.neuron_list[id2],weight=weight,name="Synaps number %s, connecting neuron %s and %s " % (synaps_id,id1,id2), synaps_multiplicator=synaps_multiplicator, plasticity = plasticity)
      self.synaps_list.append(synaps)
      dico = self.get_synaps_dict()
      self.synaps_data.append(dico)
      if flags is not None:
        if type(flags)!=list:
          flags = [flags]
        for flag in flags:
          if not flag in self.synaps_flag_dict.keys():
            self.synaps_flag_dict[flag] = []
          self.synaps_flag_dict[flag].append(synaps_id)
      return synaps_id

  def link_neuron_to_group(self, neuron_id, group_flag, rand=False, synaps_flags=None, bidirectional=False, weight=None, post=True, synaps_multiplicator=1, plasticity=True):
    for neuron in self.neuron_flag_dict[group_flag]:
      if post:
        post_neuron = neuron_id
        pre_neuron   = neuron
      else:
        post_neuron = neuron
        pre_neuron  = neuron_id
      if post_neuron != pre_neuron:
        self.link_neurons(post_neuron, pre_neuron, rand=rand, flags=synaps_flags, bidirectional=bidirectional, weight=weight, synaps_multiplicator=synaps_multiplicator, plasticity=plasticity)
  
  def connect_group(self, group_flag, rand=False, synaps_flag=None, weight=None):
    for neuron_1 in self.neuron_flag_dict[group_flag]:
      for neuron_2 in self.neuron_flag_dict[group_flag]:
        if neuron_1 < neuron_2:
          self.link_neurons(neuron_1,neuron_2,rand=rand,flags=synaps_flag,bidirectional=True, weight=weight)
      


  def add_neuron(self, passive = False, flags = None, neuron_number=1, inhib = False,fake=False):
    neuron_id = self.get_neuron_number()
    kwargs = {
      "version"         : 2,
      "name"            : ("Neuron number %s" % (neuron_id)),
      "passive"         : passive,
      "neuron_number"   : neuron_number,
      "identification"  : neuron_id,
      "inhib"           : inhib,
    }
    if fake:
      neuron = FakeNeuron(**kwargs)
    else:
      neuron = Neuron(**kwargs)

    #neuron = Neuron(version = 2, name = ("Neuron number %s" % (neuron_id)), passive = passive, neuron_number=neuron_number, identification = neuron_id, inhib = inhib)
    self.neuron_list.append(neuron)
    dico = self.get_neuron_dict()
    self.neuron_data.append(dico)
    self.spike_number.append(0)
    for mode in self.neuron_input_list.keys():
      self.neuron_input_list[mode].append(lambda x : 0)
    self.neuron_noise_list.append(self.default_noise_generator)
    if flags is not None:
      if type(flags)!=list:
        flags = [flags]
      for flag in flags:
        if not flag in self.neuron_flag_dict.keys():
          self.neuron_flag_dict[flag] = []
        self.neuron_flag_dict[flag].append(neuron_id)
    return neuron_id

  def impose_current(self, neuron_id, current_id = 1, current_function = None):
    if not self.valid_id(neuron_id): 
      self.print_error_message()
      return
    if current_function is None:
      current_function = self._default_current_functions[current_id]
    self.neuron_input_list[self._mode][neuron_id] = current_function
  
  def impose_current_to_group(self, flag, current_id = 1, current_function = None):
    for neuron_id in self.neuron_flag_dict[flag]:
      self.impose_current(neuron_id, current_id = current_id, current_function = current_function)

  ##################################################################
  # SAVING FUNCTIONS

  def save_weights(self, save_name=None, force=False, flags=None):
    if save_name is None:
      save_name = str(len(self.saves.keys()))
    if save_name in self.saves.keys():
      print "Waring, save name already used, please use force=True to overide current save"
      if not force:
        return
    self.saves[save_name] = {}
    if flags is None:
      synaps_ids = range(len(self.synaps_list))
    else:
      synaps_ids = self.get_synaps_id_from_flags(flags)
    for synaps_id in synaps_ids:
      self.saves[save_name][synaps_id] = self.synaps_list[synaps_id].get_weight()
    #self.saves[save_name] = map(lambda x : self.synaps_list[x].get_weight(), synaps_id)
    print self.saves

  def restaure_weights(self, save_name=None):
    if save_name is None:
      save_name = self.saves.keys()[0]
    save = self.saves[save_name]
    for synaps_id in save.keys():
      self.synaps_list[synaps_id].set_weight(save[synaps_id])
    
  def reinitialize_weights(self, synaps_id=None, flags=None):
    if synaps_id is not None:
      ids = [synaps_id]
    elif flags is not None:
      ids = self.get_synaps_id_from_flags(flags)
    else:
      print "you need to pick some synapses"
      return
    for synaps_id in ids:
      self.synaps_list[synaps_id].set_weight(0)

  def keep_connected(self, keep_name=None, force=True,flags=None):
    result = []
    if keep_name is None:
      keep_name = str(len(self._keeps.keys()))
    if keep_name in self._keeps.keys() and not force:
      print "name already used, please use force=True"
      return
    if flags is not None:
      synaps_list = self.get_synaps_from_flags(flags)
    else:
      synaps_list = self.synaps_list
    for synaps in synaps_list:
      if synaps.get_weight() > 0.5:
        result.append((synaps.get_post_neuron().get_id(),synaps.get_pre_neuron().get_id()))
    self._keeps[keep_name] = result


  def compare_keeps(self, name1, name2):
    try:
      keep1 = self._keeps[str(name1)]
    except:
      print "name1 unknown"
      print "list name : %s" % str(self._keeps.keys())
      return
    try:
      keep2 = self._keeps[str(name1)]
    except:
      print "name1 unknown"
      print "list name : %s" % str(self._keeps.keys())
      return
    count = 0
    for i in self._keeps[str(name1)]:
      count += int(i in self._keeps[str(name2)])
    avg = (len(self._keeps[str(name1)])+len(self._keeps[str(name2)]))/2.
    try:
      return count/avg
    except:
      return 0

  ##################################################################
  # BLOCKING FUNCTIONS

  def block_synaps(self, flag, block=True):
    for synaps_id in self.synaps_flag_dict[flag]:
      self.synaps_list[synaps_id].block(block)

  def block_plasticity(self, flag, block=True):
    for synaps_id in self.synaps_flag_dict[flag]:
      self.synaps_list[synaps_id].block_plasticity(block)

  ##################################################################
  # SET FUNCTIONS

  def set_uref_square(self, u_ref_square, flags=None):
    if flags is not None:
      synaps_list = self.get_synaps_from_flags(flags)
    else:
      #neuron_list = self.neuron_list
      synaps_list = self.synaps_list
    for synaps in synaps_list:
      #neuron.set_uref_square(u_ref_square)
      synaps.set_uref_square(u_ref_square)

  def set_max_weight(self, weight, flags=None):
    if flags is not None:
      synaps_list = self.get_synaps_from_flags(flags)
    else:
      synaps_list = self.synaps_list
    for synaps in synaps_list:
      synaps.set_max_weight(weight)


  ##################################################################
  # CLEANING FUNCTIONS

  def clean_current(self, flags=None):
    if flags is None:
      for key in xrange(len(self.neuron_input_list[self._mode])):
        self.neuron_input_list[self._mode][key] = (lambda x : 0) 
    else:
      neuron_list = self.get_neuron_id_from_flags(flags)
      for neuron in neuron_list:
        self.neuron_input_list[self._mode][neuron] = (lambda x : 0)

  def clean_data(self, neuron=True, synaps=True):
    if neuron:
      for i in xrange(self.get_neuron_number()):
        self.neuron_data[i] = self.get_neuron_dict()
    if synaps:
      for i in xrange(self.get_synaps_number()):
        self.synaps_data[i] = self.get_synaps_dict()


  ##################################################################
  # DRAWING FUNCTIONS

  def draw_synaps_graph(self, graph_key, synaps_id = None, flags = None, r_figure=True):
    data_list = []
    names = []
    if type(graph_key)==list:
      figure = True
    else:
      figure = False
      graph_key = [graph_key]
    if not r_figure:
      figure = False
    if synaps_id is not None:
      data_list = map(lambda x: self.synaps_data[synaps_id][x], graph_key)
      names.extend(map(lambda x: "%s for %s" % (x, self.synaps_list[synaps_id].get_name()), graph_key))
    else:
      if flags is not None:
        if type(flags) != list:
          flags = [flags]
        data = []
        synaps = []
        for flag in flags:  
          data.extend(map(lambda x : self.synaps_data[x], self.synaps_flag_dict[flag]))
          synaps.extend(map(lambda x : self.synaps_list[x], self.synaps_flag_dict[flag]))
      else:
        data   = self.synaps_data
        synaps   = self.synaps_list
      for key in graph_key:
        data_list.extend(map(lambda x: x[key], data))
        names.extend(map(lambda x : "%s for %s" % (key, x.get_name()), synaps))
    smart_plot(data_list, figure=figure,names=names)

  def draw_neuron_graph(self, graph_key, neuron_id = None, flags = None, r_figure=True,smooth=False):
    data_list = []
    names = []
    if type(graph_key)==list:
      figure = True
    else:
      figure = False
      graph_key = [graph_key]
    if not r_figure:
      figure=False
    if neuron_id is not None:
      data_list = map(lambda x: self.neuron_data[neuron_id][x], graph_key)
      names.extend(map(lambda x: "%s for %s" % (x, self.neuron_list[neuron_id].get_name()), graph_key))
    else:
      if flags is not None:
        if type(flags) != list:
          flags = [flags]
        data = []
        neurons = []
        for flag in flags:
          data.extend(map(lambda x: self.neuron_data[x], self.neuron_flag_dict[flag]))
          neurons.extend(map(lambda x: self.neuron_list[x], self.neuron_flag_dict[flag]))
      else:
        data = self.neuron_data
        neurons = self.neuron_list
      for key in graph_key:
        data_list.extend(map(lambda x: x[key], data))
        names.extend(map(lambda x: "%s for %s" % (key, x.get_name()), neurons))
    if smooth:
      data_list = map(lambda x : math_tools.gaussian_kernel(x, 200), data_list) 
    smart_plot(data_list, figure=figure, names=names)

  def draw(self, name):
    if type(name) == int:
      self._graph_dict[self._graph_dict.keys()[name]]()
    else:
      self._graph_dict[name]()

  def draw_weight(self, neuron_list = None, pre_list = None, post_list = None, flag=None, title=None,xlabel=None,ylabel=None,vmin=None,vmax=None,color_bar=True,color_bar_label=None): 
    X = []
    if neuron_list is not None:
      pre_list   = neuron_list
      post_list = neuron_list
    if flag is not None:
      pre_list   = self.neuron_flag_dict[flag]
      post_list = self.neuron_flag_dict[flag]

    
    for neuron_id1 in post_list:
      temp = []
      for neuron_id2 in pre_list:
        if neuron_id2==neuron_id1:
          n = 0
        else:
          try:
            n = min(self.neuron_list[neuron_id1].get_synaps_correspondence()[neuron_id2].get_weight(),30)
          except KeyError:
            n = 0
        temp.append(n)
      X.append(temp)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    cmap = clr.Colormap("lo",100) 
    img = ax.imshow(X, interpolation="nearest",vmax=vmax,vmin=vmin)
    if color_bar:
      color_bar = plt.colorbar(img)
      if color_bar_label is not None:
        color_bar.set_label(color_bar_label)
    if title is not None:
      ax.set_title(title)
    if xlabel is not None:
      ax.set_xlabel(xlabel)
    if ylabel is not None:
      ax.set_ylabel(ylabel)
    plt.show()

  def draw_correlation(self, graph_key, flags=None, smooth=False,reverse=False,name=None,xlabel=None,ylabel=None):
    # Gathering neurons
    if flags is None:
      neuron_list = xrange(len(self.neuron_list))
    else:
      neuron_list = self.get_neuron_id_from_flags(flags)
    if reverse:
      neuron_list.reverse()
    # Gathering datas
    data = map(lambda x : self.neuron_data[x][graph_key], neuron_list)
    if smooth:
      data = map(lambda x : math_tools.gaussian_kernel(x,200), data)
    data = numpy.array(data)
    correlation_matrix = numpy.corrcoef(data)
    # Drawing the graph
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.imshow(correlation_matrix, interpolation="nearest")
    if name is not None:
      plt.title(name)
    if xlabel is not None:
      plt.xlabel(xlabel)
    if ylabel is not None:
      plt.ylabel(ylabel)
    plt.show()

    


  # END OF CLASS
  ##################################################################


def smart_plot(liste, x_list = None, figure = False, names = None,xlabel=None,ylabel=None,xlim=None,ylim=None, legend=None, legend_position=1):
  color = ("r--", "b--", "g--", "y--", "o--")
  if figure:
    plt.figure(1)
    nb_figure = len(liste)
    for key in xrange(len(liste)):
      plt.subplot(nb_figure, 1, key)
      plt.plot(range(len(liste[key])), liste[key], color[0])
      if names is not None:
        plt.title(names[key])
  else:
    ax = plt.gca()
    if x_list is None:
      args = ()
      kwargs = {}
      label = None
      for key in xrange(len(liste)):
        if legend is not None:
          kwargs = {"label":legend[key]}
        args = (range(len(liste[key])), liste[key], color[key % len(color)])
        plt.plot(*args,**kwargs)
    else:
      args = (x_list, liste, color[0])
      plt.plot(*args)
    if names is not None:
      plt.title(names)
    if xlabel is not None:
      ax.set_xlabel(xlabel)
    if ylabel is not None:
      ax.set_ylabel(ylabel)
    if xlim is not None:
      ax.set_xlim(xlim)
    if ylim is not None:
      ax.set_ylim(ylim)
    if legend is not None:
      if legend_position==1:
        loc = "upper right"
      elif legend_position==2:
        loc = "lower right"
      elif legend_position==3:
        loc = "lower left"
      else:
        loc = "upper left"
      plt.legend(loc=loc)


  plt.show()
  return plt

def spike_function(frequency = 100, phase = 0, random=False):
  if random:
    return lambda x : pow(10,7) if (randint(1,frequency-1)==1) else 0 #Frequency-1 cause the neuron needs a DELTA_T to get back in a resting state
  else:
    return lambda x : pow(10,7) if ( (x - (phase/DELTA_T)) % (frequency/DELTA_T) == 0 ) else 0

def constant_current_function(intensity = 9.5*pow(10,2), phase = 0):
  return lambda x : intensity if x > phase else 0

def noisy_current_function(intensity = 8*pow(10,2)):
  return lambda x : normal(intensity, intensity/2.)

