#!/usr/bin/env python


from random import random
from math import sqrt, exp, pi

def cum_law(x):
	if x==0:
		return 0.5
	if x>=7.56:
		return 1.0
	if x<=-7.56:
		return 0.0
	u=abs(x)
	n=int(u*2000)
	du=float(u)/n
	k=1/sqrt(2*pi)
	u1=0
	f1=k
	p=0.5
	for i in xrange(0,n):
		u2=u1+du
		f2=k*exp(-0.5*u2*u2)
		p=p+(f1+f2)*du*0.5
		u1=u2
		f1=f2
	if x>0:
		return p
	else:
		return 1.0-p

def law(x, m, s):
	return normal_cum_law((x-m)/s)

def xgaussred(p):
	if p==0.5:
		return 0.0
	if p==0.0:
		return -7.56
	if p==1.0:
		return +7.56
	if p>0.5:
		pc=p
	else:
		pc=1-p
	du=float(1)/2000
	eps=1.0E-15
	k=1/sqrt(2*pi)
	u1=0.0
	f1=k
	p1=0.5
	while True:
		u2=u1+du
		f2=k*exp(-0.5*u2*u2)
		s=(f1+f2)*0.5*du
		p2=p1+s
		if abs(p2-pc)<eps:
			break
		if ((p1<pc) and (p2<p1)) or  ((p1>pc) and (p2>p1)):
			du=-du/2
		u1=u2
		f1=f2
		p1=p2
	if p>0.5:
		return u2
	else:
		return -u2

def xgauss(p,m,s):
	return m+s*xgaussred(p)

def random_gaussian(m,s):
	return xgauss(random(),m,s) 
