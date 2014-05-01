#!/usr/bin/env python


from math	import factorial
from math 	import exp
from math 	import e
from random 	import random


def law(k,l):
	p=exp(-l)*l**k/factorial(k)
	return p
	

def cum_law(k,m):
	pk=e**(-m)
	p=pk
	for i in xrange(1,k+1):
		pk *= m/float(i)
		p += pk
	return p


def random_poisson(l,nb=0):
	ph=random()
	k=0
	pc=law(k,l)
	while ph>pc:
		k+=1
		pc+=law(k,l)
	return k
