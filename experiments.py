#!/usr/bin/env python


from network import *
from visual import visual_network
from math_tools import *


def visual_timer(inhib=True, iteration=5):
  if inhib:
    data = "classic"
  else:
    data = "no_inhib"
  result = []
  for i in xrange(iteration):
    n = visual_network(data=data,draw=False)
    n.launch()
    n.switch("exp_time")
    temp_result = []
    for j in xrange(iteration):
      temp_result.append(n.launch())
      print "step %s done" % j
    result.append(temp_result)
    print "big step %s done" % i
  new_result = map(lambda x : custom_avg(x), result)
  new_result = custom_avg(new_result)
  return new_result, result


