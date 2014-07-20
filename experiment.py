#-*-coding:utf-8-*-


from network    import *
from visual     import *
import math_tools
from numpy      import *



class Experiment():

  ####################################################################################################################################
  ## BUILDING FUNCTIONS

  def __init__(self,exp,nb_trial=1,full_data=False,test=False):
    self._exp_dict = {
      "similarity" : { 
        "launch"  : self.similarity,
        "plot"    : self.plot_similarity,
      },
      "relearning": {
        "launch"  : self.relearning,
        "plot"    : self.plot_relearning,
      },
      "deep_learning" : {
        "launch"  : self.deep_learning,
        "plot"    : self.deep_plot,
      }
    }
    if exp not in self._exp_dict.keys():
      raise Exception("experiment unkown")
    self._test        = test
    self._exp         = exp
    self.nb_trial     = nb_trial
    self._full_data   = full_data
    self._full_result = []
    self._part_result = []


  ####################################################################################################################################
  ## TEMPLATE FUNCTIONS

  def launch(self,draw=False):
    for i in xrange(self.nb_trial):
      temp = self._exp_dict[self._exp]["launch"](draw)
      self._full_result.append(temp[0])
      self._part_result.append(temp[1])
      print "Trial %s up to %s" % (i+1,self.nb_trial)

  def plot(self):
    self._exp_dict[self._exp]["plot"]()


  ####################################################################################################################################
  ##  DEEP LEARNING FUNCTIONS

  DEEP_TRAIL_NUMBER = 100
  COUNT             = True

  def deep_launch(self, network):
    network.launch()
    network.switch("exp_time")
    return network.launch(trail_nb=self.DEEP_TRAIL_NUMBER,deep_keeps=True,count=self.COUNT)

  def part_deep(self, data):
    for i, e in enumerate(data):
      if e > 0.5:
        return i
    return self.DEEP_TRAIL_NUMBER
  
  def deep_learning(self,draw):
    #Gathering data on classic network
    classic_network = visual_network(draw=draw,test=self._test)
    classic_data    = self.deep_launch(classic_network)
    #Gathering data on inhib free network
    inhib_free_network  = visual_network(data="no_inhib",draw=draw,test=self._test)
    inhib_free_data     = self.deep_launch(inhib_free_network)
    #return
    if self._full_data:
      full_result = (classic_data, inhib_free_data)
    else:
      full_result = []
    part_result = (self.part_deep(classic_data),self.part_deep(inhib_free_data))
    return (full_result, part_result)

  def deep_plot(self,lim=10000):
    classic_data    = map(lambda x : x[0], self._part_result)
    inhib_free_data = map(lambda x : x[1], self._part_result)
    

    math_tools.histogram(
      [[average(inhib_free_data),average(classic_data)]],
      confidence_list=[[var(inhib_free_data),var(classic_data)]],
      title="Average Relearning time",
      ylim=(0,lim),
      ylabel="Time, ms",
      stick_labels=("Inhib Free Network", "Inhib Network")
    )

  ####################################################################################################################################
  ## RELEARNING FUNCTIONS

  RELEARNING_TRAIL_NUMBER = 200

  def relearning_launch(self, network):
    network.launch()
    network.switch("exp_time")
    kwargs = {
      "trail_nb" : self.RELEARNING_TRAIL_NUMBER,
    }
    return network.launch(trail_nb=self.RELEARNING_TRAIL_NUMBER)#**kwargs)


  def relearning(self,draw):
    #Gathering data on classic network
    classic_network = visual_network(draw=draw,test=self._test)
    classic_data    = self.relearning_launch(classic_network)
    #Gathering data on inhib free network
    inhib_free_network  = visual_network(data="no_inhib",draw=draw,test=self._test)
    inhib_free_data     = self.relearning_launch(inhib_free_network)
    #return
    if self._full_data:
      full_result = (classic_data, inhib_free_data)
    else:
      full_result = []
    part_result = []
    return (full_result, part_result)
  
  def plot_relearning(self):
    classic_data    = map(lambda x : x[0], self._full_result)
    classic_data    = math_tools.custom_avg(classic_data)
    inhib_free_data = map(lambda x : x[1], self._full_result)
    inhib_free_data = math_tools.custom_avg(inhib_free_data)
    smart_plot(
      [classic_data,inhib_free_data],
      names ="Relearning average Curves",
      xlabel="step",
      ylabel="Average Similarity", 
      legend=["Inhib Network", "Inhib Free Network"],
      legend_position=2,
    )
   
    #ùùùùùùùùùùùùùùùùùùùùù
  
  ####################################################################################################################################
  ## SIMILARITY FUNCTIONS

  def similarity_launch(self, network):
    network.launch()
    network.switch("similarity")
    return network.launch()

  def similarity(self,draw):
    #Gathering data on classic network
    classic_network = visual_network(draw=draw,test=self._test)
    classic_data    = self.similarity_launch(classic_network)
    #Gathering data on network with no inhib
    no_inhib_network  = visual_network(data="no_inhib",draw=draw,test=self._test)
    no_inhib_data     = self.similarity_launch(no_inhib_network)
    #return
    if self._full_data:
      full_result = (classic_data, no_inhib_data)
    else:
      full_result = []
    part_result = (
      {
        "avg" : average(classic_data),
        "var" : var(classic_data),
      },
      {
        "avg" : average(no_inhib_data),
        "var" : var(no_inhib_data),
      }
    )
    return (full_result, part_result)

  def plot_similarity(self):
    avg_inhib = map(lambda x : x[0]["avg"],self._part_result)
    var_inhib = map(lambda x : x[0]["var"],self._part_result)
    avg_no_inhib = map(lambda x : x[1]["avg"],self._part_result)
    var_no_inhib = map(lambda x : x[1]["var"],self._part_result)


    math_tools.histogram([[average(avg_no_inhib),average(avg_inhib)]],confidence_list=[[average(var_no_inhib),average(var_inhib)]],title="Average simalirity over 10 trials",ylim=(0,1),ylabel="Similarity, s",stick_labels=("Inhib Free Network", "Inhib Network"))
    math_tools.histogram([[average(var_no_inhib),average(var_inhib)]],title="Average simalirity variance over 10 trials",ylim=(0,0.04),ylabel="Similarity Variance",stick_labels=("Inhib Free Network", "Inhib Network"))
    smart_plot([avg_inhib,avg_no_inhib],xlabel="Trial number",ylabel="Similarity, s",names="Average similarity for both inhibs/inhibs_free networks",ylim=(0,1),legend=["With Inhibs Network","Inhibs free Network"],legend_position=2)
    smart_plot([var_no_inhib,var_inhib],xlabel="Trial number",ylabel="Similarity variance",names="Similarity variance for both inhibs/inhibs_free networks",ylim=(0,0.06),legend=["Inhibs Free Network","With Inhibs Network"],legend_position=1)

