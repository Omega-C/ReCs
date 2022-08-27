from numpy import exp,sin,cos,pi,floor;tau=2*pi
import numpy

sinusoid=lambda x:sin(x*tau)
square=lambda x:floor(sin(x*tau)*2)-1
saw=lambda x:x%1
triangle=lambda x:4*abs(x-floor(x+3/4)+1/4)-1
chip=lambda f,g:(lambda *args,**kwargs:((f(*args,**kwargs)*g)//1)/g)

def equalTone(note,a4=440):
	return((a4/16)*2**((note-9)/12))

def justTone(note,c=16):
	return((lambda x:1+(8*(x&1)+15*((x//2)&1)+1*((x//3)&1)+29*((x//4)&1)+2*((x//5)&1)+2*((x//6)&1)+4*((x//7)&1)+64*((x//8)&1)-1*((x//9)&1)+5*((x//10)&1)+7*((x//11)&1))/120)(note%12)*2**(note//12)*c)

def coefficentMap(values,f=sin):
	return(lambda x:sum([a*f(x*p) for p,a in values]))

def convolve(matrix,kernal=numpy.array([1/4,1/2,1/4])):return(numpy.convolve(matrix,kernal,mode="same"))
