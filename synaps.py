#!/usr/bin/env python


from __init__ import *


class Synaps():

	def __init__(self, post_neuron, pre_neuron, inhib = False, version = 1):

		#CONFIG VAR
		self._firing_multiplicator 	= 1
		self._x_firing_multiplicator 	= 1
		self._version 		   	= version 

		#CONSTANT
		self._delta_t = DELTA_T
		self._tau     = 10 	# time constant (ms) 
		self.IR       = 0 	# Resting intensity (mV)
		if inhib:
			self._inhib = -1
		else:
			self._inhib = 1

		self.R	= 1 	# Resistance (Ohm)
		self.w	= 0.5 	# Weitgh (No unit) 

		
		self.post_neuron = post_neuron
		self.pre_neuron  = pre_neuron


		#CLAUDIA CONSTANTS
		self._theta_minus	= -70.6		# low pass filtered threshold (mV)
		self._theta_plus	= -45.3		# potential threshold (mV)
		self._ALTD		= 14*pow(10,-5)	# amplitude parameter (mV-2)
		self._ALTP		= 8*pow(10,-5) 	# amplitude parameter(mV-1)
		self._tau_x		= 15		# x time constant (ms)
		self._tau_minus		= 10		# w_minus time constant (ms)
		self._tau_plus		= 7		# w_plus time constant (ms)
		self._w_min		= 0 			
		self._w_max		= 100
		self._C			= 281		# membrane capacitance (pF)
		self._tau_barbar 	= pow(10,3)	# u_barbar time constant (ms)
		self._u_ref_square	= 320.7 		# potential reference value (mV2) 

		#CLASS VARIABLES
		self.I      = self.IR # Potential (A)
		self._fired = 0 

		#CLAUDIA CLASS VARS
		self._u_minus	= self.post_neuron.get_resting_potential() # u LOW PASS FILTERED (mV)
		self._u_plus	= 0 # u LOW PASS FILTERED (mV)
		self._x		= 0 # spike low pass filtered
		self._dw_plus	= 0 
		self._dw_minus	= 0
		self._u_barbar  = self.post_neuron.get_resting_potential() # u LOW PASS FILTERED (mV)

	def run(self):
		self._fired = self.pre_neuron.get_fired()
		self._update_potential()
		if self._version == 2:
			self._update_other_functions()

	##################################################################
	#GET FUNCTIONS
	
	def get_current(self):
		return self._inhib*self.I 
	
	def get_weight(self):
		return self.w
	
	def get_post_synaptic_potential(self):
		return self.post_neuron.get_potential()

	def get_u_minus(self):
		return self._u_minus

	def get_u_plus(self):
		return self._u_plus

	def get_x(self):
		return self._x

	def get_dw_plus(self):
		return self._dw_plus
	
	def get_dw_minus(self):
		return self._dw_minus

	def get_u_barbar(self):
		return self._u_barbar

	##################################################################
	# UPDATE FUNCTIONS 

	def _update_other_functions(self):
		self._update_x()
		self._update_minus()
		self._update_plus()
		self._update_u_barbar()
		self._update_dw_minus()
		self._update_dw_plus()
		self._update_w()

	def _update_potential(self):
		if self._version == 1:
			delta_I = float((self.IR-self.I) + self._firing_multiplicator*self._fired)/float(self._tau)
			self.I  = max(self.I + delta_I*self._delta_t, self.IR)
		else:
			self.I = self.w*self._C*self._fired*100

	def _update_minus(self):
		delta_minus	 = float(-self._u_minus + self.get_post_synaptic_potential())/float(self._tau_minus)
		self._u_minus	 = self._u_minus + delta_minus*self._delta_t
		
	def _update_plus(self):
		delta_plus	= float(-self._u_plus + self.get_post_synaptic_potential())/float(self._tau_plus)
		self._u_plus	= self._u_plus + delta_plus*self._delta_t
	
	def _update_u_barbar(self):
		delta_u 	= float(-self._u_barbar + self.get_post_synaptic_potential())/float(self._tau_barbar)
		self._u_barbar = self._u_barbar +delta_u*self._delta_t

	def _update_x(self):
		delta_x		= float(-self._x +self._x_firing_multiplicator*self._fired)/float(self._tau_x)
		self._x 	= max(self._x + delta_x*self._delta_t, 0)

	def _update_dw_minus(self):
		self._dw_minus	= self._ALTD*self._fired*max(self._u_minus - self._theta_minus, 0)*self._u_barbar*self._u_barbar/self._u_ref_square

	def _update_dw_plus(self):
		self._dw_plus	= self._ALTP*self._x*max(self._u_plus - self._theta_minus, 0)*max(self.get_post_synaptic_potential() - self._theta_plus, 0)

	def _update_w(self):
		self.w = max(min(self.w + (self._dw_plus-self._dw_minus)*self._delta_t, self._w_max), self._w_min)
