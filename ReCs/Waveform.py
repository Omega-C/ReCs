import wave, struct, numpy
try:import pyaudio
except:pass
def save(data,Fs,path):
	with wave.open(path,"wb") as file:
		file.setnchannels(1)
		file.setsampwidth(2)
		file.setframerate(Fs)
		for d in data:
			file.writeframesraw(struct.pack("<h",int(d)))
def open(path,k=False):
	file=wave.open(path)
	if k:return(numpy.frombuffer(file.readframes(file.getnframes()),dtype=numpy.int16))
	else:return(numpy.frombuffer(file.readframes(file.getnframes()),dtype=numpy.int16))
class streamPress:
	def __init__(self,path,buffer=1024,*args,**kwargs):
		self.file=wave.open(path,"rb")
		self.buffer=buffer
		self.stream=self.streamMake(self.file,*args,**kwargs)
		self.frame=0
	def streamMake(self,file):
		p=pyaudio.PyAudio()
		stream=p.open(format=p.get_format_from_width(file.getsampwidth()),
			channels=file.getnchannels(),
			rate=file.getframerate(),
			output=True,
			frames_per_buffer=self.buffer,
			start=False,
			stream_callback=self.callback)
		return(stream)
	def play(self):
		return(self.stream.start_stream())
	def stop(self):
		self.stream.stop_stream()
		self.file.rewind()
	def callback(self,inp,frame,time,status):
		return(self.file.readframes(frame),pyaudio.paContinue)
