from ReCs import Synth
import random

def sinI(time,frequency):
	factor=time*frequency/2
	wave=Synth.sinusoid(factor)*Synth.exp(-0.001*factor)
	wave+=wave*wave*wave
	return(wave)

def squareI(time,frequency):
	factor=time*frequency
	wave=Synth.square(factor)*Synth.exp(-0.05*factor)
	wave+=wave*wave*wave
	wave/=3
	return(wave)

def sawI0(time,frequency):
	factor=time*frequency/2
	wave=Synth.chip(Synth.saw,3)(factor)*Synth.chip(Synth.exp,3)(-0.01*factor)
	wave+=wave*wave*wave
	return(wave)

def sawI(time,frequency):
	factor=time*frequency
	wave=Synth.saw(factor)*Synth.exp(-0.001*factor)
	wave+=wave*wave*wave
	return(wave)

def triangleI(time,frequency):
	factor=time*frequency
	wave=Synth.triangle(factor)*Synth.exp(-0.01*factor)
	wave+=wave*wave*wave
	return(wave)

def teslaI(time,frequency):
	return(sawI(time,frequency+random.random()*2-1)+sawI(time,frequency+random.random()*2-1))/2

def hum(time,frequency):
	factor=Synth.tau*time*frequency
	typer=lambda factor2:(Synth.sin(factor2)+Synth.sin(1.412*factor2)*0.029+Synth.sin(2.959*factor2)*0.029+Synth.sin(2.0*factor2)*0.022)
	wave=sum([typer(factor)/(1<<(i-1)) for i in range(1,7)])
	return(wave)

musicBoxConstants=[(1.0, 1.0), (1.1341350601295097, 0.054645769596322634), (2.0, 0.030048989761013053), (0.9759481961147086, 0.02914664209063185), (1.0235892691951896, 0.0275444941910754), (0.1933395004625347, 0.026633835203000028), (1.265494912118409, 0.01646960866197846), (0.9509713228492137, 0.014671760949695151), (1.0568917668825162, 0.014062685932222022), (0.16188714153561518, 0.011656280945092192), (1.3427382053654024, 0.010859210358589793), (0.9269195189639223, 0.010345446176991006), (1.0864939870490287, 0.009377053700948091), (0.893154486586494, 0.0087617975268573), (25.320074005550417, 0.008354501734720526), (0.8367252543940795, 0.007549692015350736), (0.8691026827012026, 0.005897439957050192), (0.2895467160037003, 0.0053040198447438635), (0.7224791859389454, 0.005292883490973412), (1.1110083256244219, 0.005208667794692784)]
musicBoxFunction=Synth.coefficentMap(musicBoxConstants)

def musicBox(time,frequency):
	factor=time*frequency
	wave=musicBoxFunction(factor)*Synth.exp(-0.01*factor)
	return(wave)

def experimental(time,frequency):pass

instruments={-5:lambda *args:teslaI(*args)+0.5*sinI(*args),-6:sawI0,-4:triangleI,-3:sawI,-2:squareI,-1:sinI,0:experimental,1:musicBox}
