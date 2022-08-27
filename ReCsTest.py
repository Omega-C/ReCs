from ReCs import TextParser, Compiler, Waveform, Synth
from Instruments import instruments
import time

envelopes={"F":Synth.ADSR(A=0.05,D=0.125,S=0,R=0.1,Ah=1.75),"FH":Synth.ADSR(A=0.05,D=0.075,S=0,R=0.1,Ah=1.75),"S":Synth.ADSR(A=0.05,D=5,S=0.5,R=0.01,Ah=1.5),"L":Synth.ADSR(A=0.01,D=0,S=1,R=0.01,Ah=1)}

FPS=44100
AMP=5000

melody="Test.mlod"
saveTo="TestProd.wav"
if __name__=="__main__":
	string=open(melody,"r").read()
	
	parser=TextParser.Parser()
	compiler=Compiler.Compiler(instruments[-1],130,3,instruments=instruments,noteConversion=Compiler.equalTone,envelopes=envelopes)

	stream=parser.parseVoices(string)

	print("Parsed input")

	tape=compiler.compileVoices(stream,FPS=FPS,amplitude=AMP)

	print("Compiled tokens")

	Waveform.save(compiler.functions["LP"](tape,768),FPS,saveTo)

	print("Audio saved")
	try:
		audio=Waveform.streamPress(saveTo)
		audio.play()
		while audio.stream.is_active:
			time.sleep(1)
	except:
		exit()
