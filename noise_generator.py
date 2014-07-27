#!/usr/bin/env python


from current import Current

from math import *
from __init__ import *
from numpy.random import normal, poisson


class NoiseGenerator():

  def __init__(self, intensity = 8*pow(10,2), delta_t=None):
    self._delta_t = delta_t
    self._current_function = noisy_current_function(intensity)
    self._filtered = intensity

  def get_current(self, t):
    if self._delta_t is None:
      return self._current_function(t)
    else:
     delta = (-self._filtered+self._current_function(t))/float(self._delta_t)
     self._filtered += delta*DELTA_T
     return self._filtered





def noisy_current_function(intensity = 8*pow(10,2)):
  if intensity == 0:
    return Current(0,**{"intensity":0})
  return Current(2,**{"intensity":intensity})


