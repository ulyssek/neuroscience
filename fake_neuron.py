#!/usr/bin/env python


from __init__ import *
from neuron import Neuron



class FakeNeuron(Neuron):
  
  def __init__(self,**kwargs):
    self.ARGUMENTS = {
      "frequency":10,
      }
    self.OPTIONAL_ARGUMENTS = []
    self._count = 0

    kwargs = self.get_args(**kwargs)
    super(FakeNeuron, self).__init__(**kwargs)
    

  def get_args(self, **kwargs):
    for argument in self.ARGUMENTS:
      if argument in kwargs:
        setattr(self, "_"+argument, kwargs[argument])
        del kwargs[argument]
      else:
        setattr(self, "_"+argument, self.ARGUMENTS[argument])
    for argument in filter(lambda x : x in kwargs, self.OPTIONAL_ARGUMENTS):
      setattr(self, "_"+argument, kwargs[argument])
      del kwargs[argument]
    return kwargs

  def run(self,**kwargs):
    self._fired = 0
    self._received_current = kwargs["current"]
    #self._count = (self._count + 1) % self._frequency
    if kwargs["current"]>pow(10,6):
      self._fired = 1
      self._update_synaptic_functions()

  ###################################################################
  #GET FUNCTIONS

  def get_attr(self, var_name):
    return getattr(self, var_name)
