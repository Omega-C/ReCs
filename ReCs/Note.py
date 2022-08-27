noteKey={'C':0,'C#':1,'D$':1,'D':2,'D#':3,'E$':3,'E':4,'F':5,'F#':6,'G$':6,'G':7,'G#':8,'A$':8,'A':9,'A#':10,'B$':10,'B':11}
keyNote={i:n for n,i in list(noteKey.items())[::-1]}
class Note:
	def __init__(self,time,tones,s=False,amp=1):
		self.time=time
		self.tones=tones
		self.slur=s
		self.amplitude=amp
		self.data=[time,tones,s]
	def __repr__(self):return(f"Note({self.time},{self.tones},s={self.slur},amp={self.amplitude})")
	def exchange(self,dictionary):return(Note(self.time,[dictionary[d%12]+d//12*12 if d%12 in dictionary else d for d in self.tones],self.slur,self.amplitude))
	def string(self,octave=0,resolution=5,inclAmp=True):
		toneStrings=[]
		times=[]
		for tone in self.tones:
			tone-=12*octave
			note=keyNote[tone%12]
			oshift=">"*max(tone//12,0)+"<"*-min(tone//12,0)
			toneStrings.append(f"{note}{oshift}")
		toneApp=bin(int(self.time*(1<<resolution)))[2:][::-1]
		for n,t in enumerate(toneApp):
			if t=="1":times.append("+"*max(n-resolution,0)+"-"*-min(n-resolution,0))
		initialTone="'".join(toneStrings)
		if len(toneStrings)==0:initialTone="~"
		slur="_" if self.slur else ""
		sequence=(f"Y{self.amplitude} " if inclAmp else "")+initialTone+f"_{initialTone}".join(times[::-1])+slur
		return(sequence)
	def condensed(self):
		alphaS=lambda x:"".join(b.upper() if n==0 else b for n,b in enumerate("abcdefghijklmnop"["0123456789abcdef".index(c)] for c in hex(x)[2:]))
		return(bytes("".join(alphaS(b) for b in self.tones)+"|"+alphaS(self.amplitude)+(lambda x:alphaS(x[0])+alphaS(x[1]))(float(self.time).as_integer_ratio())+("_" if self.slur else "")+"!","utf8"))
class Action:
	def __init__(self,code,payload):
		self.code=code
		self.payload=payload
	def __repr__(self):return(f"<{self.code}:{self.payload}>")
	def condensed(self):
		return(bytes(str(self.code)+"~"+(self.payload.condensed().decode("utf8") if hasattr(self.payload,"condensed") else self.payload)+"?","utf8"))
