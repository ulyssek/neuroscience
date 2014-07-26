#!/usr/bin/env python


from __init__ import *

import json


class Synaps():

  def __init__(self, post_neuron, pre_neuron, inhib = False, version = 1, weight=None, name = "Unamed synaps", synaps_multiplicator=1, plasticity = True, identification = None):

    #CONFIG VAR
    self._firing_multiplicator     = 1
    self._x_firing_multiplicator   = 1
    self._version                  = version 
    self.name                      = name
    self._blocked                  = False
    self._synaps_multiplicator     = synaps_multiplicator
    self._plasticity               = plasticity
    self.identification            = identification

    #CONSTANT
    self._delta_t = DELTA_T
    self._tau     = 10   # time constant (ms) 
    self.IR       = 0   # Resting intensity (mV)
    if inhib:
      self._inhib = -1
    else:
      self._inhib = 1

    self.R  = 1       # Resistance (Ohm)
    if weight is None:
      self.w  = 0.5   # Weitgh (No unit) 
    else:
      self.w   = weight

    
    self.post_neuron = post_neuron
    self.pre_neuron  = pre_neuron


    #CLAUDIA CONSTANTS
    self._theta_minus   = -70.6          # low pass filtered threshold (mV)
    self._theta_plus    = -45.3          # potential threshold (mV)
    self._ALTD          = 14*pow(10,-5)  # amplitude parameter (mV-2)
    self._ALTP          = 8*pow(10,-5)   # amplitude parameter(mV-1)
    self._w_min         = 0       
    self._w_max         = 10
    self._C             = 281            # membrane capacitance (pF)
    self._u_ref_square  = 20             # potential reference value (mV2) 

    #CLASS VARIABLES
    self.I      = self.IR # Potential (A)
    self._fired = 0 

    #CLAUDIA CLASS VARS
    self._dw_plus    = 0 
    self._dw_minus  = 0

  def run(self):
    self._fired = self.pre_neuron.get_fired()
    if self._blocked:
      self.potential = 0
    else:
      self._update_potential()
      if self._version == 2 and self._plasticity:
        self._update_other_functions()

  def __str__(self):
    print self.name

  ##################################################################
  #SET FUNCTIONS

  def set_uref_square(self, u_ref_square):
    self._u_ref_square = u_ref_square

  def set_max_weight(self, weight):
    self._w_max = weight

  def set_weight(self, weight):
    self.w = weight

  ##################################################################
  #GET FUNCTIONS
  
  def get_current(self):
    return self.I 
  
  def get_weight(self):
    return self.w
  
  def get_post_synaptic_potential(self):
    return self.post_neuron.get_potential()

  def get_u_minus(self):
    return self.post_neuron.get_u_minus()

  def get_u_plus(self):
    return self.post_neuron.get_u_plus()

  def get_x(self):
    return self.pre_neuron.get_x()

  def get_u_barbar(self):
    return self.post_neuron.get_u_barbar()

  def get_dw_plus(self):
    return self._dw_plus
  
  def get_dw_minus(self):
    return self._dw_minus
  
  def get_name(self):
    return self.name

  def get_pre_neuron(self):
    return self.pre_neuron
 
  def get_post_neuron(self):
    return self.post_neuron

  def get_uref_square(self):
    return self._u_ref_square

  def get_id(self):
    return self.identification

  ##################################################################
  # UPDATE FUNCTIONS 

  def _update_other_functions(self):
    self._update_dw_minus()
    self._update_dw_plus()
    self._update_w()

  def _update_potential(self):
    if self._version == 1:
      delta_I = float((self.IR-self.I) + self._firing_multiplicator*self._fired)/float(self._tau)
      self.I  = max(self.I + delta_I*self._delta_t, self.IR)
    else:
      self.I = self.w*self._C*self._fired*self.pre_neuron.get_neuron_number()*self._synaps_multiplicator*self._inhib

  def _update_dw_minus(self):
    self._dw_minus  = self._ALTD*self._fired*max(self.get_u_minus() - self._theta_minus, 0)*self.get_u_barbar()*self.get_u_barbar()/self._u_ref_square

  def _update_dw_plus(self):
    self._dw_plus  = self._ALTP*self.get_x()*max(self.get_u_plus() - self._theta_minus, 0)*max(self.get_post_synaptic_potential() - self._theta_plus, 0)

  def _update_w(self):
    self.w = max(min(self.w + (self._dw_plus-self._dw_minus)*self._delta_t, self._w_max), self._w_min)

  ##################################################################
  # OTHER FUNCTIONS

  def block(self, block=True):
    self._blocked = block

  def block_plasticity(self, block=True):
    self._plasticity = block

  ##################################################################
  ## DUMPING FUNCTION

  def to_dict(self):
    dico = dict(self.__dict__)
    dico["pre_neuron"]  = self.pre_neuron.get_id()
    dico["post_neuron"] = self.post_neuron.get_id()
    return dico

  def to_json(self):
    return json.dumps(self.to_dict())


  def from_dict(self,dico):
    for key in dico:
      setattr(self,key,dico[key])
    """
    BE CAREFULL, the Network needs to finish the job by connecting neurons and synapses
    """
      
  def from_json(self,js):
    self.from_dict(json.loads(js))

