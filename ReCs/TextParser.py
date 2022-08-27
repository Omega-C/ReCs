import re
from .Note import Note, Action, noteKey
"""
{x}       - a new voice containing x, can be escaped with backslash
![x]      - appends x to every voice, only the last is used
()        - intra voice comment
:         - signals the start of a repitition (WIP)
;         - signals the end of a repitition (WIP)
,         - ignored characters

[n]       - a note [n], a-g/A-G/integer (code 0)
~         - rest note, no sound is played

I[x]      - sets instrument to code [x] (code 1)
O[x]      - sets octave to [x] (code 2)
T[x]      - sets tempo to [x] (code 3)
Y[x]      - sets the amplitude coefficent to [x] (code 4)
R[x|*p][l]- applies a function code x with parameters p to l (code 5)
N[x]			- sets envelope to code [x] (code 6)

[n]#      - [n] sharp
[n]$      - [n] flat

[n0]'[n1] - a chord of [n0] and [n1], chords can be chained
[n]_      - slur of [n] to next note, cannot be chained
[n]+      - [n] with 2x the normal duration, can be chained
[n]-      - [n] with 0.5x the normal duration, can be chained
[n].      - [n] with 1.5x the normal duration, can be chained
[n]>      - [n] raised an octave, can be chained
[n]<      - [n] reduced an octave, can be chained

{I[x] O[y] T[z] Y[a] N[b] [n] (#/$) (</>)* (+/-)* (.)* ('[n])* (_)}
"""
class ParserSyntaxError(Exception):pass
class Parser:
	def __init__(self):
		self.validStartingChars=["ABCDEFG0123456789~","IOTYRN"]
		self.noteKey=noteKey
	def sanitiseString(self,string):
		string=string.upper()
		string=string.replace(","," ")
		string=re.sub(r"\s+",r" ",string)
		string=re.sub(r"\([^)]+\)",r"",string)
		string=string.replace("_ ","_").replace("_","_ ")
		string=string.replace("' ","'")
		return(string.strip())
	def identifyNote(self,note):
		if note.isdigit():return(int(note))
		if note not in self.noteKey:raise(ParserSyntaxError(f"{note} not in known notes"))
		return(self.noteKey[note])
	def parseVoice(self,voice,variables=[]):
		parsedVoice=[]
		variables=variables
		for a,b,c in re.findall(r"(\[\?([^\]]+)\]\s*\[([^\]]+)\])",voice.replace("\\]",chr(0))):
			a,b,c=a.replace(chr(0),"\\]"),b.replace(chr(0),"\\]"),c.replace(chr(0),"\\]")
			voice=voice.replace(a,"")
			voice=voice.replace(b.strip(),c.strip())
		for name,sequence in variables[::-1]:
			voice=voice.replace(name,sequence)
		if voice.count(";")!=voice.count(":"):raise(ParserSyntaxError("Uneven repititions in voice"))
		while ";" in voice:
			if voice.index(":")>voice.index(";"):raise(ParserSyntaxError("Reversed repititions in voice"))
			voice=re.sub(r":([^;:]*);",r" \1 \1 ",voice)
		voice=self.sanitiseString(voice)
		for action in re.split(r"\s(?![^\[]*\])",voice):
			if len(action)<1:continue
			if action[0] not in self.validStartingChars[0]+self.validStartingChars[1]:raise(ParserSyntaxError(f"{action} not recognised"))
			if action[0] not in self.validStartingChars[1]:
				time=2**(action.count("+")-action.count("-"))*1.5**action.count(".")
				slur="_" in action
				for char in "_+-.":
					action=action.replace(char,"")
				tones=[self.identifyNote(note.replace("<","").replace(">",""))+12*(note.count(">")-note.count("<")) for note in action.split("'") if note not in ("~",)]
				parsedVoice.append(Action(0,Note(time,tones,slur)))
			else:
				code=1+self.validStartingChars[1].index(action[0])
				if code==5:
					data,notes=action[2:-1].split("[",1)
					data=data[:-1]
					identifier,*parameters=data.split("|")
					notesParsed=self.parseVoice(notes)
					parsedVoice.append(Action(code,[identifier,parameters,notesParsed]))
				else:
					parsedVoice.append(Action(code,action[1:]))
		return(parsedVoice)
	def parseVoices(self,string):
		variables=[]
		for a,b,c in re.findall(r"(\[\?([^\]]+)\]\s*\[([^\]]+)\])",string.replace("\\]",chr(0))):
			a,b,c=a.replace(chr(0),"\\]"),b.replace(chr(0),"\\]"),c.replace(chr(0),"\\]")
			string=string.replace(a,"")
			variables.append((b.strip(),c.strip()))
		h=re.findall(r"\!\[([^\]]+)\]",string)
		h=h[-1]+" " if len(h)>0 else ""
		return([self.parseVoice(h+voice,variables) for voice in re.findall(r"(?:^|[^\\])\{([^\}\{]*)\}",string)])
