import numpy as np

def custom_avg(list_list):
  return map(lambda x : np.average(x), zip(*list_list))

