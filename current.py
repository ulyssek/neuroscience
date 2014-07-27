
import numpy
from numpy.random import normal, poisson
from random import randint
import json


from __init__ import *

class Current():
    
 
    ##################################################################
    ## INIT FUNCTIONS

    """
    def __init__(self, current_id=1):
      self.current_id = current_id
      self.current_function = self.CURRENT[str(current_id)]
    """

    def __init__(self, current_function=1,**kwargs):
      self.current_function_id = current_function
      self.kwargs_to_self(kwargs)
      self.current_function = self.CURRENT_FUNCTION[current_function](self,**kwargs)

    def kwargs_to_self(self,kwargs):
      for key in kwargs.keys():
        setattr(self, key, kwargs[key])

    ##################################################################
    ## RUNNING FUNCTIONS

    def run(self,x):
      return self.current_function(x)

    def __call__(self,x):
      return self.run(x)
      
    ##################################################################
    ## GET FUNCTIONS

    def get_id(self):
      return self.current_id

    def get_current_function(self):
      return self.current_function

    ##################################################################
    ## CUSTOM CURRENT FUNCTIONS

    def spiking_current(self, frequency = 100, phase = 0, random=False, intensity=pow(10,7)):
      params = {
        "frequency" : frequency,
        "phase"     : phase,
        "random"    : random,
        "intensity" : intensity,
      }
      self.kwargs_to_self(params)
      if random:
        return lambda x : intensity if (randint(1,frequency-1)==1) else 0 #Frequency-1 cause the neuron needs a DELTA_T to get back in a resting state
      else:
        return lambda x : intensity if ( (x - (phase/DELTA_T)) % (frequency/DELTA_T) == 0 ) else 0

    def constant_current(self, intensity = 9.5*pow(10,2), phase = 0):
      params = {
        "intensity" : intensity,
        "phase"     : phase,
      }
      self.kwargs_to_self(params)
      return lambda x : intensity if x > phase else 0

    def noisy_current(self, intensity = 8*pow(10,2)):
      params = {
        "intensity" : intensity,
      }
      self.kwargs_to_self(params)
      return lambda x : normal(intensity, intensity/2.)

   ##################################################################
    ## CLASS VARS

    """
    CURRENT = {
      "1" : constant_current(),                        #CONSTANT SMALL CURRENT
      "2" : constant_current(phase=5),                 #CONSTANT SMALL CURRENT, WAITING 5ms TO ACTIVATE
      "3" : spiking_current(intensity=10),              #SPIKING DEFAULT CURRENT
      "4" : constant_current(intensity=0),             #NULL CURRENT
      "5" : spiking_current(intensity=10,random=True), #RANDOM SPIKING CURRENT
      "6" : spiking_current(10),                        #HIGH SPIKING FUNCTION
      "7" : noisy_current(),                           #RANDOM CURRENT FOLLOWING NORMAL DISTRIBUTION
    }
    """

    CURRENT_FUNCTION = (
      constant_current,
      spiking_current,
      noisy_current,
    )



    ##################################################################
    ## DUMPING FUNCTIONS

    def to_dict(self):
      dico = dict(self.__dict__)
      dico.pop("current_function")
      return dico

    def to_json(self):
      return json.dumps(self.to_dict())

    def from_dict(self,dico):
      for key in dico.keys():
        setattr(self, key, dico[key])
      kwargs = dict(dico)
      kwargs.pop("current_function_id")
      print kwargs
      self.current_function = self.CURRENT_FUNCTION[self.current_function_id](self, **kwargs)

    def from_json(self,js):
      self.from_dict(json.loads(js))
