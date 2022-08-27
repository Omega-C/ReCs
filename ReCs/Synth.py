from .SynthBase import *
try:
	from scipy.signal import find_peaks
	from scipy.optimize import curve_fit
	Sp=True
except:Sp=False

def resample(ndarray,squish):return(numpy.interp(numpy.arange(0,len(ndarray),squish),numpy.arange(0,len(ndarray)),ndarray))

def feed(consts:numpy.ndarray):return(numpy.vectorize(lambda x:sum(consts[1]*numpy.cos(2*numpy.pi*x*consts[0]+consts[2]))))

def fourierCoefficentsSci(data,thresh=0.001,limit=20):
	if not Sp:raise(Warning("Scipy not found"))
	fftdata=abs(numpy.fft.rfft(data))
	points,_=find_peaks(fftdata,distance=50)
	mX=max(points,key=lambda x:fftdata[x])
	mY=fftdata[mX]
	points=[(x/mX,fftdata[x]/mY) for x in points]
	points.sort(key=lambda x:-x[-1])
	points=[p for p in points if p[1]>=thresh][:limit]
	return(points)

def fourierCoefficents(data,length=None,resolution=30000,roundC=16384,cond=(lambda r:0<=r[0]<=64 and r[1]>=0.01)):
	if length==None:length=len(data)
	length=length*2-1
	D=numpy.fft.rfft(data,length)
	F=numpy.fft.rfftfreq(length,d=1/(len(data)*2-1))
	A=numpy.hypot(D.real,D.imag)
	P=numpy.arctan2(D.imag,D.real)
	data=numpy.array((*zip(F,A,P),))
	pks=[r for n,r in enumerate(data) if (data[n-1][1]<(r[1]-resolution)>data[(n+1)%len(data)][1])]
	dominant=max(pks,key=lambda x:x[1])
	rounding=lambda x:round(x*roundC)/roundC
	pks=[(rounding(2*r[0]/dominant[0]),rounding(r[1]/dominant[1]),rounding(r[2])) for r in pks]
	pks=[r for r in pks if cond(r)]
	return(pks)

def merge(*args,maxima=1):
	arrays,weights=(*zip(*args),)
	mLength=max([len(array) for array in arrays])
	arrays=[SynthBase.numpy.pad(arrays[i]*weights[i],(0,mLength-len(arrays[i])),"constant") for i in range(len(array))]
	final=sum(arrays)
	maxim=max(abs(final))
	final*=maxima/maxim
	return(final)

def arrayToFunction(array,rate=1,wrap=True):
	def func(x):
		x*=rate
		p=x%1
		l,u=x//1,-((-x)//1)
		if wrap:return(array[int(u)%len(array)]*p+array[int(l)%len(array)]*(1-p))
		return(array[max(int(u),0)]*p+array[min(len(array)-1,int(l))]*(1-p))
	return(func)

def cendio(data,amp=1.5):return(data*numpy.arange(1,amp*len(data))/len(data))

def lowPass(matrix,freqdomain=1024,FPS=44100):
	freqdomain=FPS//int(freqdomain)
	return(convolve(matrix,numpy.zeros(freqdomain)+1/freqdomain))

def lowPassC(matrix,cutoff=1024,bandwith=0.008,FPS=44100):
	cutoff*=1/FPS
	N=numpy.ceil(4/bandwith)
	if N%2:N-=1
	n=numpy.arange(N+1)
	h=numpy.sinc(2*tau*cutoff*(n-N/2))
	h*=0.42-cos(tau*n/N)/2+0.08*cos(2*tau*n/N)
	h/=sum(h)
	return(convolve(matrix,h))

def gausean(matrix,radius=1024,maxim=0.5,FPS=44100):
	radius=FPS//radius
	s=1/(maxim*numpy.sqrt(tau))
	kernal=maxim*exp(-(numpy.arange(0,radius)/s)**2/2)
	return(convolve(matrix,kernal))

def highPass(lp):return(lambda matrix,*args,**kwargs:matrix-lp(matrix,*args,**kwargs))

def inpWarble(x,a,b,c,d):return((a-b)*(x-c*sin(pi*x/c)/pi/d)/2+b*x)

def warble(matrix,l,f,wps=1,d=1,FPS=44100):
	matrixc=arrayToFunction(matrix)
	ar=inpWarble(numpy.arange(0,len(matrix)),l,f,FPS/wps,d)
	data=numpy.array([matrixc(x) for x in ar])
	return(data)

def reverb(matrix,timestep=0.07642,rb=10,damp=5,wd=(2,18),decay=lambda d,r,x,t,f:exp(-2*x/(r*t))/d,FPS=44100):
	timestep*=FPS
	timestep=int(timestep)
	st=timestep
	dmatrix=matrix.copy()
	wet=wd[0]/sum(wd)
	dry=wd[1]/sum(wd)
	while st<len(matrix):
		matrix[st:]=\
		(matrix[:-st]*wet+dmatrix[:-st]*dry)*decay(damp,rb,st,timestep,FPS)+matrix[st:]
		st+=timestep
	return(matrix)

def constantEnvelope(self,freq,time,p,inst,FPS):return(inst(numpy.arange(p,p+time)/FPS,self.noteConversion(freq)))

def soundify(ndarray,transform=lambda x:resample(x,2**(1/12)),window=44100/4,length=0.5,hop=4):
	window=int(window)
	hopL=int(window/hop+0.5)
	windows=int(len(ndarray)-window+window/hop)
	arrays=[numpy.fft.irfft(transform(numpy.fft.rfft(ndarray[i:i+window]*numpy.hamming(len(ndarray[i:i+window])),n=window).real),n=window).real for i in range(0,windows,hopL)]
	reconstructed=numpy.zeros(int(len(ndarray)*length))
	for n,i in enumerate(range(0,int(windows*length),int(hopL*length))):
		reconstructed[i:i+window]+=arrays[n][:len(reconstructed[i:i+window])]
	return(reconstructed)

def ADSR(A=0.05,D=5,S=1,R=0.3,Ah=1.5,Af=lambda x:x,Df=lambda x:numpy.log(1+x),Rf=lambda x:x):
	def func(self,freq,time,p,inst,FPS):
		AA=Af(numpy.arange(0,A*FPS)/FPS)
		DA=Df(numpy.arange(0,D*FPS)/FPS)
		RA=Rf(numpy.arange(0,R*FPS)/FPS)
		if len(AA)>0:AA=(AA-AA[0])/AA[-1]*Ah
		if len(DA)>0:DA=(DA-DA[0])/DA[-1]*(S-Ah)+Ah
		BA=numpy.concatenate((AA,DA))
		data=inst(numpy.arange(p,p+time+FPS*R)/FPS,self.noteConversion(freq))
		if time<len(BA):
			data[:time]=data[:time]*BA[:time]
			if len(RA)>0:RA=(RA-RA[0])/RA[-1]*-BA[time]+BA[time]
		else:
			data[:len(BA)]=data[:len(BA)]*BA
			data[len(BA):time]=data[len(BA):time]*S
			if len(RA)>0:RA=(RA-RA[0])/RA[-1]*-S+S
		data[time:]=data[time:]*RA
		return(data)
	return(func)
