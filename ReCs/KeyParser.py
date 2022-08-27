from .Note import Action, Note
from .Waveform import save
import pygame, datetime, time
import pygame.midi as midi
midi.init()
now=lambda:datetime.datetime.now().timestamp()
closest=lambda v,mi,r=False:(lambda x:1 if x==0 and r else x)(int(v/mi+0.5))*mi

def init():
	pygame.display.set_mode((1,1))

def quit():
	pygame.quit()

def eventParse(event):
	if event.type in [midi.MIDIIN]:
		if event.status in [144,128]:
			return((True,event.status==144,event.data1,False))
	if event.type in [pygame.KEYDOWN]:
		return((False,True,event.key,False))
	if event.type in [pygame.KEYUP]:
		return((False,False,event.key,False))

def events(identifier=midi.get_default_input_id(),stop=lambda arg:False,done=lambda:time.sleep(0.1)):
	midiIn=midi.Input(identifier)
	while True:
		events=pygame.event.get()+midi.midis2events(midiIn.read(10),identifier)
		for event in events:
			if stop(event):break
			elif event.type==pygame.QUIT:break
			parsed=eventParse(event)
			if parsed!=None:yield(parsed)
		else:
			continue
		break
		done()

def generate(actions,compiler,time,FPS=44100,amplitude=2500,fileP="S"):
	for action in actions:
		U=f"{fileP}{action.id}.wav"
		save(compiler.compileVoice(action.action(time),FPS=FPS,amplitude=amplitude),FPS,U)

class Act:
	ident=0
	def __init__(self,action,keys=set(),keysNot=set(),down=lambda *args:None,up=lambda *args:None):
		self.id=self.__class__.ident
		self.__class__.ident+=1
		self.action=action#function that takes time and  returns a note sequence
		self.keys=keys
		self.keysNot=keysNot
		self.up=up
		self.down=down
		self.recording=[0]
		self.past=False
	def isIn(self,s):
		return(all(k in s for k in self.keys) and not any(k in s for k in self.keysNot))
	def read(self,keys,timestamp):
		if self.past!=self.isIn(keys):
			self.past=not self.past
			if self.past:self.down(self)
			else:self.up(self)
			self.recording.append(timestamp)
	def flush(self):
		self.past=False
		self.recording=[0]
	def end(self,timestamp):
		if self.past:self.recording.append(timestamp)
	@property
	def tape(self):
		return([(self.recording[t+1]-self.recording[t],t%2!=0) for t in range(len(self.recording)-1)])

class Parser:
	def __init__(self,actions,silence=lambda t:[Action(0,Note(t,[],False))],stop=lambda e:e.type in [pygame.KEYDOWN] and e.key in [13,27],**kwargs):
		self.actions=actions
		self.kwargs=kwargs
		self.kwargs["stop"]=stop
		self.silence=silence
	def listen(self):
		pool=set()
		modifier=0
		STimestep=now()
		for M,S,D,A in events(**self.kwargs):
			timestep=now()-STimestep
			if A:modifier=D
			else:
				if M:D+=128
				D+=modifier
				if S:pool.add(D)
				elif D in pool:pool.remove(D)
				for action in self.actions:
					action.read(pool,timestep)
		timestep=now()-STimestep
		for action in self.actions:
			action.end(timestep)
		return(True)
	def toVoices(self,minimum=1/16):
		voices=[]
		for action in self.actions:
			voice=[]
			for timestamp,n in action.tape:
				timestamp=closest(timestamp,minimum,n)
				if n:voice+=action.action(timestamp)
				else:voice+=self.silence(timestamp)
			voices.append(voice)
		return(voices)
	def flush(self):
		for action in self.actions:
			action.flush()
