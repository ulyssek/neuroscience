#!/usr/bin/env python



import time


class Timer():


	_STEP = 0.001

	def __init__(self):
		self._action_list = []

	def add_action(self, action):
		self._action_list.append(action)

	def add_action_list(self, action_list):
		self._action_list.extend(action_list)

	def print_action_list(self):
		print "number of action : %s " % len(self._action_list)
		for action in self._action_list:
			print "Action : %s " % action

	def run(self):
		while(True):
			for action in self._action_list:
				action()
			time.sleep(self._STEP)
			print "loop"

