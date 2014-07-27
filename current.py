
import numpy
from numpy.random import normal, poisson
from random import randint


from __init__ import *


##################################################################
## CUSTOM CURRENT FUNCTIONS

def spiking_current(frequency = 100, phase = 0, random=False, intensity=pow(10,7)):
  if random:
    return lambda x : intensity if (randint(1,frequency-1)==1) else 0 #Frequency-1 cause the neuron needs a DELTA_T to get back in a resting state
  else:
    return lambda x : intensity if ( (x - (phase/DELTA_T)) % (frequency/DELTA_T) == 0 ) else 0

def constant_current(intensity = 9.5*pow(10,2), phase = 0):
  return lambda x : intensity if x > phase else 0

def noisy_current(intensity = 8*pow(10,2)):
  return lambda x : normal(intensity, intensity/2.)



class Current():
    
    ##################################################################
    ## CLASS VARS

    CURRENT = {
      "1" : constant_current(),                        #CONSTANT SMALL CURRENT
      "2" : constant_current(phase=5),                 #CONSTANT SMALL CURRENT, WAITING 5ms TO ACTIVATE
      "3" : spiking_current(intensity=10),              #SPIKING DEFAULT CURRENT
      "4" : constant_current(intensity=0),             #NULL CURRENT
      "5" : spiking_current(intensity=10,random=True), #RANDOM SPIKING CURRENT
      "6" : spiking_current(10)                        #HIGH SPIKING FUNCTION
    }

    ##################################################################
    ## INIT FUNCTIONS

    def __init__(self, current_id=1):
      self.current_id = current_id
      self.current_function = self.CURRENT[str(current_id)]

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

