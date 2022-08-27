import numpy
from .Synth import *
class CompilerError(Exception):pass
class Compiler:
	def __init__(self,dInstrument=lambda t,f:sinusoid(t*f),dTempo=120,dOctave=4,noteConversion=equalTone,instruments={},envelopes={"0":constantEnvelope,"1":ADSR()},functions={"GL":gausean,"RV":reverb,"LP":lowPassC,"WB":warble,"RS":lambda x:x[::-1]}):
		self.instruments=instruments
		self.envelopes=envelopes
		self.functions=functions
		self.dInstrument=dInstrument
		self.dTempo=dTempo
		self.dOctave=dOctave
		self.noteConversion=noteConversion
	def compileNote(self,instrument,envelope,time,tones,pTimestep,FPS=44100):
		if len(tones)==0:return(numpy.zeros(time))
		try:
			return(sum([envelope(self,frequency,time,pTimestep,instrument,FPS) for frequency in tones]))
		except Exception as e:
			raise(CompilerError(f"Error compiling note \"{str(e)}\""))
	def compileVoice(self,voice,FPS=44100,amplitude=5000,prms=None):
		tape=numpy.array([])
		if prms==None:
			instrument=self.dInstrument
			envelope=self.envelopes[tuple(self.envelopes)[0]]
			octave=self.dOctave
			tempo=self.dTempo
			amplitudeCoeff=1
			pTimestep=0
		else:
			instrument,envelope,octave,tempo,amplitudeCoeff,pTimestep=prms
		tTimestep=0
		for action in voice:
			if action.code==0:
				time,tones,slur=action.payload.data
				time=int(time*FPS*60/tempo)
				tones=[tone+octave*12 for tone in tones]
				line=self.compileNote(instrument,envelope,time,tones,pTimestep,FPS=FPS)*amplitude*amplitudeCoeff
				tape=numpy.pad(tape,(0,max(0,tTimestep+len(line)-len(tape))),"constant")
				tape[tTimestep:tTimestep+len(line)]+=line
				if slur:pTimestep+=time
				else:pTimestep=0
				tTimestep+=time
			if action.code==1:
				instrument=self.instruments[int(action.payload)]
			if action.code==2:
				octave=int(action.payload)
			if action.code==3:
				tempo=int(action.payload)
			if action.code==4:
				amplitudeCoeff=float(action.payload)
			if action.code==5:
				prms=(instrument,envelope,octave,tempo,amplitudeCoeff,pTimestep)
				line=((tape,self.functions[action.payload[0]](self.compileVoice(action.payload[2],FPS=FPS,amplitude=amplitude*amplitudeCoeff,prms=prms),*(eval(a) for a in action.payload[1] if a!=""))))[1]
				tape=numpy.pad(tape,(0,max(0,tTimestep+len(line)-len(tape))),"constant")
				tape[tTimestep:tTimestep+len(line)]+=line
			if action.code==6:
				envelope=self.envelopes[action.payload]
		return(tape)
	def compileVoices(self,voices,FPS=44100,amplitude=5000,correctAmp=True):
		if type(amplitude) in (int,float):
			compiledVoices=[self.compileVoice(voice,FPS=FPS,amplitude=amplitude) for voice in voices]
		else:
			compiledVoices=[self.compileVoice(voice,FPS=FPS,amplitude=amplitude[n]) for n,voice in enumerate(voices)]
		if len(compiledVoices)==0:return(numpy.array([]))
		maxLength=len(max(compiledVoices,key=len))
		if correctAmp:
			return(self.correctAmplitude(sum([numpy.pad(voice,(0,maxLength-len(voice)),"constant") for voice in compiledVoices])))
		return(sum([numpy.pad(voice,(0,maxLength-len(voice)),"constant") for voice in compiledVoices]))
	def correctAmplitude(self,tape,audioMax=3276):
		if len(tape)==0:return(tape)
		modifier=abs(max(tape,key=abs))
		return(tape*audioMax/modifier)
