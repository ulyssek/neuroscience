#!/usr/bin/env python



from time import time
import matplotlib.pyplot as plt



class Timer():
	
	def __init__(self):
		self._time_list = []
		self._last_time = None
		self._time_dict = {}


	def clean(self):
		self._time_list = []

	def pick(self, flag=None):
		if self._last_time is not None:
			current_time = time()-self._last_time
			self._time_list.append((current_time,flag))
		self._last_time = time()


	def save(self):
		for t, flag in self._time_list:
			if flag is not None:
				if flag not in self._time_dict.keys():
					self._time_dict[flag] = []
				self._time_dict[flag].append(t)

	def prnt(self,average=0):
		print "printing Timer : "
		if not average:
			for t, flag in self._time_list:
				if flag is not None:
					print "%s : %s" % (flag, t)
				else:
					print "%s" % t
		else:
			for flag in self._time_dict.keys():
				_sum = sum(self._time_dict[flag])
				avg = _sum/len(self._time_dict[flag])
				print "avg %s : %s" % (flag, avg)
				print "sum %s : %s" % (flag, _sum)

	def draw(self):
		color = "r--"
		time_list = []
		for t, flag in self._time_list:
			time_list.append(t)
		args = (range(len(time_list)), time_list, color)
		plt.plot(*args)
		plt.show()
