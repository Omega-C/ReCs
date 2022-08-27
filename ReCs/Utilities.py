from .SynthBase import sinusoid, saw, square, triangle, exp
from .Note import Note, Action, noteKey, keyNote

class Synthetic:
	def __init__(self,function):
		self.function=function
	def __call__(self,*args,**kwargs):
		return(function(*args,**kwargs))
	def add(self,other):
		if type(other)==type(self):
			return(self.create(lambda *args,**kwargs:self.function(*args,**kwargs)+other.function(*args,**kwargs)))
		return(self.create(lambda *args,**kwargs:self.function(*args,**kwargs)+other))
	def negative(self):
		return(self.create(lambda *args,**kwargs:-self.function(*args,**kwargs)))
	def inverse(self):
		return(self.create(lambda *args,**kwargs:pow(self.function(*args,**kwargs),-1)))
	def multiply(self,other):
		if type(other)==type(self):
			return(self.create(lambda *args,**kwargs:self.function(*args,**kwargs)*other.function(*args,**kwargs)))
		return(self.create(lambda *args,**kwargs:self.function(*args,**kwargs)*other))
	def broadcast(self,other):
		if type(other)==type(self):
			return(self.create(lambda *args,**kwargs:self.function(other.function(*args,**kwargs))))
		raise(TypeError(f"cannot broadcast to type {other.__class__.__name__}"))
	@classmethod
	def create(cls,function):
		return(cls(function))
#do more tommorow

class Tone:
	def __init__(self,ID):
		self.octave=4
		self.ID=0
		if type(ID)==Action:ID=ID.payload
		if type(ID)==Note:ID=note.tones[0]
		if type(ID)==float:ID=int(ID)
		if type(ID)==int:
			self.ID=ID%12
			self.octave=ID//12
		if type(ID)==str:self.ID=noteKey[ID]
	def __add__(self,other):
		return(self.semiTone(other))
	def __repr__(self):
		return(f"{keyNote[self.ID]}:{self.octave}")
	def semiTone(self,toneID):
		return(self.__class__(self.ID+toneID))
	def chord(self,M=True):
		if M:return([self,self+4,self+7])
		if M==None:return([self,self+3,self+6])
		return([self,self+3,self+7])
class Scale:
	def __init__(self,note,M=True,P=False):
		self.note=note
		self.M=M
		self.P=P
	def __repr__(self):
		return(f"<{self.note}, M:{self.M}, P:{self.P}>")
	@property
	def notes(self):
		if self.P:
			if self.M:return([self.note+i for i in [0,2,4,7,9,12]])
			return([self.note+i for i in [0,3,5,7,10,12]])
		if self.M:return([self.note+i for i in [0,2,4,5,7,9,11,12]])
		return([self.note+i for i in [0,2,3,5,7,8,10,12]])
	@property
	def chords(self):
		if self.P:return()
		if self.M:return([self.notes[n].chord(v) for n,v in enumerate([True,False,False,True,True,False,None])])
		return([self.notes[n].chord(v) for n,v in enumerate([False,None,True,False,False,True,True])])