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

  
def histogram(list_list, confidence_list=None,witness=False,title=None,ylim=(0,1),xlim=(0,0.76),ylabel=None,stick_labels=None):
  fig, ax = plt.subplots()
  if title is not None:
    fig.suptitle(title)
  width = 0.25
  ind = np.arange(len(list_list[0]))*(len(list_list)+1)*(width)
  color = ((0,0,0), (1,1,0), (1,1,1), (1,0,1), (0,1,0), (0,1,1), (0,0.5,0.5), (0,0,1), (0.5,0,0), (0,0.5,0), (0,0,0.5),(1,0,0))

  ax.set_xticks(ind+width*len(list_list)/2.)
  #ax.set_xticklabels( ('N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW') )
  if stick_labels is not None:
    ax.set_xticklabels(stick_labels)
  ax.set_ylabel(ylabel)
  ax.set_autoscale_on(False)
  ax.set_xlim(xlim)
  ax.set_ylim(ylim)

  def autolabel(rects):
    # attach some text labels
    for rect in rects:
      height = rect.get_height()
      ax.text(rect.get_x()+rect.get_width()/2., 1.05*height, '%d'%int(height),
        ha='center', va='bottom')


  if confidence_list is None:
    confidence_list = map(lambda x : None, range(len(list_list)))
  for i in xrange(len(list_list)):
    rects = ax.bar(ind + i*width, list_list[i], width, color=color[i%(len(color))],yerr=confidence_list[i])
    #autolabel(rects)

  if witness:
    ax.bar(np.arange(1)+(len(list_list[0])*(len(list_list)+1)-1)*width, [1], width, color=(0,0,0))


  plt.show()

def custom_avg(list_list):
  return map(lambda x : np.average(x), zip(*list_list))

