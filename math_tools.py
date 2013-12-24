#!/usr/bin/env python

import matplotlib.pyplot as plt
import numpy as np
from numpy.random import normal
from math import exp
import math


def distribution(liste,name=None, lenght=None):
  if lenght is None:
    lenght = max(int(len(liste)/10),10)
  plt.hist(liste, bins=lenght)
  if name is None:
    name = "Histogram"
  plt.title(name)
  plt.xlabel("Value")
  plt.ylabel("Frequency")
  plt.show()


def gen(i, lenght, scale):
  count = max(0, i-scale/2)
  while count <= min(lenght-1, i+scale/2):
    yield count
    count += 1


def gaussian_kernel(liste, scale=None):
  if scale is None:
    scale = int(len(liste)/10)
  result = []
  def smart_gen(i):
    return gen(i, len(liste), scale) 
  for i in xrange(len(liste)):
    result.append(sum(map(lambda x : exp(-2.3*abs(i-x)/scale)*liste[x], smart_gen(i)))/sum(map(lambda x : 1,smart_gen(i))))
  return result


def correlation(list1, list2):
  l1 = len(list1)
  l2 = len(list2)
  if l1 != l2:
    raise Exception("the lists should have the same lenght")
  m1 = float(sum(list1))/l1
  m2 = float(sum(list2))/l2

  
def histogram(list_list):
  fig, ax = plt.subplots()
  width = 0.35
  ind = np.arange(len(list_list[0]))*(len(list_list) -1)*(width*(1.+2./len(list_list)))
  color = ("r", "b", "g", "y", "c", "m", "k", "w")

  ax.set_xticks(ind+width)
  ax.set_xticklabels( ('G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8') )

  def autolabel(rects):
    # attach some text labels
    for rect in rects:
      height = rect.get_height()
      ax.text(rect.get_x()+rect.get_width()/2., 1.05*height, '%d'%int(height),
        ha='center', va='bottom')


  for i in xrange(len(list_list)):
    rects = ax.bar(ind + i*width, list_list[i], width, color=color[i%(len(color))])
    autolabel(rects)


  plt.show()
