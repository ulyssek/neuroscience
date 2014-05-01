def f(n):
  results = []
  for i in xrange(6):
    for j in xrange(6-i-1):
      try:
        results.append(n.compare_keeps(i,i+j+1))
      except:
        results.append(0)
  return results
