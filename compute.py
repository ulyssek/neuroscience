#-*-coding:utf-8-*-

from visual import *
from numpy  import *




class Compute():


  def __init__(self,nb_trail=10,test=False,whole_computation=True,inhib_free=False,draw=False):
    self._functions = {
      "firing_rate"             : lambda x : self.firing_rate_function(x),
      "connection_probability"  : lambda x : self.connection_probability(x),
      "connection_inhib"        : lambda x : self.connection_inhib(x),
      "group_selected"          : lambda x : self.group_selected(x),
    }

    self._keys        = self._functions.keys()
    self._var         = {}
    self._result      = {}
    self._nb_trail    = nb_trail
    self._kwargs      = {}
    if inhib_free:
      self._kwargs["data"] = "no_inhib"
    if test:
      self._kwargs["nb_round"] = 2
    self._kwargs["draw"] = draw

    for key in self._keys:
      self._var[key] = False
      self._result[key] = []

    if whole_computation:
      self.add_compute()




  def add_compute(self, compute=True,boule=True):
    if compute == True:
      for key in self._keys:
        self._var[key] = True
    else:
      if type(compute)==int:
        compute = self._var.keys()[compute]
      self._var[compute] = boule

  def launch(self,inhib_free=False,draw=False):
    for i in xrange(self._nb_trail):
      n = visual_network(**self._kwargs)
      n.launch()
      for key in self._keys:
        if self._var[key]:
          self._result[key].append(self._functions[key](n))
      self.n = n

  def av(self):
    result = {}
    for key in self._keys:
      result[key] = average(self._result[key])
      
  def var(self):
    result = {}
    for key in self._keys:
      result[key] = var(self._result[key])
      

  def connection_probability(self, n):
    flags  = ["inter neuron", "exci"]
    return n.get_nb_connection(flags=flags)/float(len(n.get_synaps_id_from_flags(flags=flags)))

  def firing_rate_function(self, n):
    n.switch("resting")
    n.save_data(True)
    n.launch()
    result =  n.get_firing_rate(flags=["receptive","exci"])
    return result

  def connection_inhib(self, n):
    flags = ["inter neuron", "inhib", "plastic"]
    try:
      return n.get_nb_connection(flags=flags)/float(len(n.get_synaps_id_from_flags(flags=flags)))
    except KeyError:
      return
      

  def group_selected(self, n):
    flags = ["input"]
    return n.get_nb_connection(flags=flags)/float(n.visual_constant["ex_nb"])
