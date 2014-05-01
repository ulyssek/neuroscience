#!/usr/bin/env python



def spike_function(frequency = 100, phase = 0):
	return lambda x : pow(10,7) if ( (x - (phase/DELTA_T)) % (frequency/DELTA_T) == 0 ) else 0

def constant_current_function(intensity = 9.5*pow(10,2), phase = 0):
	return lambda x : intensity if x > phase else 0


