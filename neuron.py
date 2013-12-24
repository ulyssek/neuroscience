#!/usr/bin/env python


from __init__ import *
from timer import Timer
from time import sleep

class Neuron(object):

  def __init__(self, version = 1, name = "Not named neuron", passive = False, neuron_number = 1, identification = None, inhib = False):

    ###################################################################

    #WARNING, VERSION 2 ONLY COMPATIBLE WITH 1ms step

    ###################################################################
    #CONFIG VAR
    self.version          = version
    self.name             = name
    self.passive          = passive
    self._state           = 0
    self.identification   = identification
    self._inhib           = inhib


    #CONSTANTS
    self._tau           = 5               # time constant [ms]
    self._firing_tau    = 10              # time constant [ms]
    self.neuron_number  = neuron_number   # allow to modelize bunch of neurons
  
    #CLAUDIA CONSTANTS
    self.C              = 281     # Membrane capacitance [pF]
    self.gL             = 30      # Leak conducatance [nS]
    self.EL             = -70.6   # Resting Potential [mV]
    self.deltaT         = 2       # slope [mV]
    self.tau_wad        = 144     # wad time constant adaptation [ms]
    self.tau_z          = 40      # z time constant adaptation [ms]
    self.tau_VT         = 50      # VT time constant adaptation [ms]
    self.b              = 0.805   # wad increaser [pA]
    self.a              = 4       # wad parameter [nS]
    self.Isp            = 400     # after spike z current [pA]
    self.VTrest         = -50.4   # resting threshold [mV]
    self.VTmax          = -30.4   # maximum threshold [mV]
    self.Vf             = 29.4    # firing potential [mV] (Claudia constant)
    self.th             = 20      # fix threshold [mV]
    self._u_ref_square  = 20      # potential reference value [mV2]

    self._nb_average    = 100
    self._fire_count    = 0

    #SYNAPS CONSTANT
    self._tau_x         = 15            # x time constant (ms)
    self._tau_minus     = 10            # w_minus time constant (ms)
    self._tau_plus      = 7             # w_plus time constant (ms)
    self._tau_barbar    = pow(10,4)     # u_barbar time constant (ms)

    #CLASS VARS
    self._fired                 = 0
    self._delta_t               = DELTA_T
    self.potential              = self.EL
    self.firing_rate            = 0
    self._last_fired            = []
    self._firing_rate           = 0
    self._current_index         = 0
    self.post_firing_potential  = 0
    self._received_current      = 0
    for i in xrange(self._nb_average):
      self._last_fired.append(0)

    #SYNAPS VARS
    self._u_minus     = self.EL # u LOW PASS FILTERED (mV)
    self._u_plus      = 0       # u LOW PASS FILTERED (mV)
    self._x           = 0       # spike low pass filtered
    self._u_barbar    = 0       # u LOW PASS FILTERED (mV)

    self._post_synaps_list                 = []
    self._pre_synaps_list                  = []
    self._pre_synaps_correspondence_list   = {}
    

    #CLAUDIA CLASS VARS
    self.wad    = 0     # hyperpolarization current [pA]
    self.z      = 0     # leak current [pA]
    self.VT     = 10    # threshold potential [mV]

  def run(self, current = 0, spike = False):
    self._fired = 0
    if self._state == 1:
      self.potential   = self.Vf + 3.462 # Claudia magic numbers
      self._state   = 2
      self._update_synaptic_functions()
    else:
      if self._state == 2:
        self.potential   = self.EL + 15 + 6.0984 # Claudia magic numbers
        self._state   = 0
      if self.potential == self.Vf:
        self.potential = self.EL+22
      if not self.passive:
        current += sum(map(lambda x : x.get_current(), self._pre_synaps_list))
      self._received_current = current 
      self._update_potential(current)
      if (self.potential >= self.th) or spike:
        #print "%s potential : %s, VT : %s, current : %s " % (self.name, self.potential, self.VT, current)
        self._spike()
      if self.version == 2:
        self._update_others_functions(self._fired)
        self._update_synaptic_functions()
      self._update_firing_potential()

  def add_pre_synaps(self, synaps):
    self._pre_synaps_list.append(synaps)
    self._pre_synaps_correspondence_list[synaps.get_pre_neuron().get_id()] = synaps
  
  def add_post_synaps(self, synaps):
    self._post_synaps_list.append(synaps)

  def __str__(self):
    return self.name

  ###################################################################
  #GET FUNCTIONS

  def get_resting_potential(self):
    return self.EL

  def get_fired(self):
    return self._fired

  def get_potential(self):
    return self.potential

  def get_firing_potential(self):
    return self.post_firing_potential

  def get_average_firing_rate(self):
    return sum(self._last_fired)/len(self._last_fired)

  def get_leak_current(self):
    return self.z
  
  def get_threshold(self):
    return self.VT

  def get_hyperpolarization_current(self):
    return self.wad

  def get_exponential_thing(self):
    return self.gL*self.deltaT*math.exp(float(self.potential-self.VT)/float(self.deltaT))

  def get_received_current(self):
    return self._received_current

  def get_firing_rate(self):
    return self._firing_rate

  def get_neuron_number(self):
    return self.neuron_number

  def get_id(self):
    return self.identification

  def get_synaps_correspondence(self):
    return self._pre_synaps_correspondence_list

  def get_inhib(self):
    return self._inhib

  def get_name(self):
    return self.name

  def get_u_minus(self):
    return self._u_minus
  
  def get_u_plus(self):
    return self._u_plus
  
  def get_u_barbar(self):
    return self._u_barbar
  
  def get_x(self):
    return self._x

  def get_uref_square(self):
    return self._u_ref_square

  ###################################################################
  #SET FUNCTIONS

  def set_uref_square(self, u_ref_square):
      self._u_ref_square = u_ref_square

  ###################################################################
  #UPDATE FUNCTIONS

  def _update_others_functions(self, fired = False):
    self._update_hyperpolarization_current(fired)
    self._update_leak_current(fired)
    self._update_threshold(fired)
    self._update_last_fired()
    self._update_firing_rate()

  def _update_synaptic_functions(self):
    if len(self._pre_synaps_list) > 0:
      self._update_minus()
      self._update_plus()
      self._update_u_barbar()
    if len(self._post_synaps_list) > 0:
      self._update_x()

  def _update_last_fired(self):
    self._last_fired[self._fire_count] = self._fired
    self._fire_count = (self._fire_count + 1) % self._nb_average

  def _update_firing_rate(self):
    self._firing_rate = sum(self._last_fired)/float(self._nb_average)

  def _update_potential(self, current):
    if self.version == 1:
      delta_v = float(-self.potential + current*self._resistance)/float(self._tau)
    elif self.version == 2:
      delta_v = float(-self.gL*(self.potential - self.EL) + self.gL*self.deltaT*math.exp(float(self.potential-self.VT)/float(self.deltaT)) + self.z - self.wad + current)/float(self.C)
    self.potential = self.potential + delta_v*self._delta_t

  def _update_hyperpolarization_current(self, fired = False):
    if fired:
      self.wad += self.b
    else:
      delta_wad = float(self.a*(self.potential-self.EL)-self.wad)/float(self.tau_wad)
      self.wad = max(self.wad + delta_wad*self._delta_t, 0)

  def _update_leak_current(self, fired = False):
    if fired:
      self.z = self.Isp
    else:
      delta_z = float(-self.z)/float(self.tau_z)
      self.z = max(self.z + delta_z*self._delta_t, 0)

  def _update_threshold(self, fired = False):
    if fired:
      self.VT = self.VTmax
    else:
      delta_VT = float(self.VTrest - self.VT)/float(self.tau_VT)
      self.VT = max(self.VT + delta_VT*self._delta_t, self.VTrest)

  def _update_firing_potential(self):
    delta_v = float(-self.post_firing_potential + 100*self._fired)/float(self._firing_tau)
    self.post_firing_potential = max(self.post_firing_potential + delta_v*self._delta_t, 0)


  #SYNAPS UPDATE

  def _update_minus(self):
    delta_minus   = float(-self._u_minus + self.potential)/float(self._tau_minus)
    self._u_minus   = self._u_minus + delta_minus*self._delta_t

  def _update_plus(self):
    delta_plus  = float(-self._u_plus + self.potential)/float(self._tau_plus)
    self._u_plus  = self._u_plus + delta_plus*self._delta_t
  
  def _update_u_barbar(self):
    delta_u   = float(-self._u_barbar + (self.potential-self.EL))/float(self._tau_barbar)
    self._u_barbar = self._u_barbar +delta_u*self._delta_t

  def _update_x(self):
    delta_x    = float(-self._x +self._fired)/float(self._tau_x)
    self._x   = max(self._x + delta_x*self._delta_t, 0)

  ##################################################################
  #OTHERS
  def _spike(self):
    #print "%s spike ! " % self.name
    self._fired      = 1
    self.potential   = self.Vf # Claudia constant... what is this ?? [mV]
    self._state   = 1

