# CAUTION, THE WAV FILES OUTPUT BY THIS FILE MAY CONTAIN HIGH FREQUENCIES WITH LARGE AMPLITUDE
# DO NOT PLAY ANY WAV FILES OUTPUT WITHOUT FIRST CHECKING THE WAVE FORM AND TURNING DOWN YOUR SPEAKER VOLUME
# I AM NOT RESPONSIBLE FOR ANY DAMAGE CAUSED TO YOUR SPEAKERS OR YOUR HEARING BY NOT FOLLOWING THESE GUIDELINES
# YOU HAVE BEEN WARNED
#
# Midi to Wav Conversion attempt
# Author: Brad Baker
# License: Copyright 2017 - see License.txt for Open-Source License Agreement
# Date: February 23rd 2017
# Purpose: To perform generation of Wav files using frequency output from EdgeMidi.py
# 		   using only the libraries provided in EdgeMidi.py. Basically, the software 
#		   simulates a very primitive synthesizer to convert MIDI pitch outputs from EdgeMidi.py 
#		   into frequency data which is then written to a Wav file using the Scipy libraries. 
#
# Development: Ongoing
#
# Upcoming Features: Converting MIDI files directly into Wav 
# 					 Filters, envelopes, choice of wave-form
#					 Better volume adjustment
# 					 
import numpy as np
import scipy.io.wavfile as sio

pitch_grid = np.load('output/pitch.grid.npy') #load the pitch grid saved before 
xres = pitch_grid.shape[1]
yres = pitch_grid.shape[0]

volume_preventer = 0.2 # TO prevent people from blowing out their speakers
fs = 44100
duration_per_note = 1
total_duration = xres*fs*1
samples = np.zeros((total_duration))
single_sample = np.zeros((total_duration))
for y in range(yres): #for each pitch
	#print(y+1)
	for x in range(xres): #for each timepoint
		pitch = pitch_grid[y][x]

		partpow = (pitch-12.0)/12.0
		partfreq = np.power(2.0,partpow)
		freq =	(440.0/32.0)*(partfreq)
		if pitch == 0:
			freq = 0
		print("{}:{}:{}:{}".format(pitch,partpow,partfreq,freq))
		#freq = 440
		one_sample = volume_preventer*(np.sin(2*np.pi*np.arange(fs*duration_per_note)*freq/fs)).astype(np.float32)
		single_sample[x*duration_per_note*fs:(x+1)*duration_per_note*fs] = one_sample
	samples += single_sample
#sd.play(np.asarray(freq_grid[0]),44100)		
sio.write('test.wav',44100,samples)