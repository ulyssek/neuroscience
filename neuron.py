#!/usr/bin/env python


from __init__ import *

class Neuron():

	def __init__(self, version = 1, name = "Not named neuron", passive = False):
		#CONFIG VAR
		self.version = version
		self.name    = name
		self.passive = passive


		#CONSTANTS
		self._tau 		= 5 	# time constant [ms]
		self._firing_tau      	= 10 	# time constant [ms]
	
		#CLAUDIA CONSTANTS
		self.C		= 281  		# Membrane capacitance [pF]
		self.gL       	= 30    	# Leak conducatance [nS]
		self.EL       	= -70.6		# Resting Potential [mV]
		self.deltaT   	= 2     	# slope [mV]
		self.tau_wad  	= 144   	# wad time constant adaptation [ms]
		self.tau_z    	= 40    	# z time constant adaptation [ms]
		self.tau_VT   	= 50    	# VT time constant adaptation [ms]
		self.b        	= 0.805 	# wad increaser [pA]
		self.a        	= 4     	# wad parameter [nS]
		self.Isp      	= 400   	# after spike z current [pA]
		self.VTrest   	= -50.4  	# resting threshold [mV]
		self.VTmax    	= -30.4   	# maximum threshold [mV]
		self.Vf		= 100    	# firing potential [mV]
		self.th		= 20		# fix threshold [mV]

		self._nb_average      = 10

		#CLASS VARS
		self._fired         		= 0
		self._delta_t       		= DELTA_T
		self.potential      		= self.EL
		self.firing_rate    		= 0
		self._last_fired    		= []
		self._current_index 		= 0
		self.post_firing_potential 	= 0
		self._received_current 		= 0
		for i in xrange(self._nb_average):
			self._last_fired.append(0)

		self._post_synaps_list = []
		self._pre_synaps_list  = []

		#CLAUDIA CLASS VARS
		self.wad	= 0 	# hyperpolarization current [pA]
		self.z   	= 0 	# leak current [pA]
		self.VT  	= 10 	# threshold potential [mV]

	def run(self, current = 0, spike = False):
		self._fired = 0
		if self.potential == self.Vf:
			self.potential = self.EL
		if not self.passive:
			current += sum(map(lambda x : x.get_current(), self._pre_synaps_list))
		self._received_current = current 
		self._update_potential(current)
		if (self.potential >= self.th) or spike:
			#print "%s potential : %s, VT : %s, current : %s " % (self.name, self.potential, self.VT, current)
			self._spike()
		result = (self.potential, self._fired)
		if self.version == 2:
			self._update_others_functions(self._fired)
		self._update_fire()
		self._update_firing_potential()

		return result

	def add_pre_synaps(self, synaps):
		self._pre_synaps_list.append(synaps)
	
	def add_post_synaps(self, synaps):
		self._post_synaps_list.append(synaps)

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

	###################################################################
	#UPDATE FUNCTIONS

	def _update_others_functions(self, fired = False):
		self._update_hyperpolarization_current(fired)
		self._update_leak_current(fired)
		self._update_threshold(fired)

	def _update_fire(self):
		self._last_fired[self._current_index] = self._fired
		self._current_index = (self._current_index + 1) % 2 

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

	##################################################################
	#OTHERS
	def _spike(self):
		#print "%s spike ! " % self.name
		self._fired    = 1
		self.potential = self.EL + 22 # Claudia constant... what is this ?? [mV]

