# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 20:54:23 2017

@author: bbaker94


"""
#Using the MidiUtil library
from MidiFile import MIDIFile
from PIL import Image
import numpy as np
import ConfigParser
import cv2
#import ffmpy
import sys, getopt, os

def main(argv):
	global config
	global permitted_octave
	global notes_per_octave
	global track_time
	global grid_res_x
	global grid_res_y
	global inputfile
	global outfile
	global outdir
	global save_midi
	global save_any
	global save_grid
	global save_thumb
	try:
		opts, args = getopt.getopt(argv,"hi:o:x:y:t:s:",["od","xr","yr","oct","octr","sg","st","sm","ifile=","ofile=","xres=","yres=","octaves=","octrange=","time=","savegrid=","savethumb=","savemidi=","save=","odir="])
	except getopt.GetoptError:
		print 'EdgeMidi.py -i <InputImage> -o <OutputFileName>'
		sys.exit(2)
		
	for opt, arg in opts:
		if opt == '-h':
			print 'EdgeMidi.py -i <InputImage> -o <OutputFileName>'
		elif opt in ("-i","--ifile"):
			inputfile = arg
		elif opt in ("-o","--ofile"):
			outfile = arg
		elif opt in ("-od","--odir"):
			outdir = arg
		elif opt in ("-xr","-x","--xres"):
			grid_res_x = int(arg)
		elif opt in ("-yr","-y","--yres"):
			grid_res_y = int(arg)
		elif opt in("-oct","--octaves"):
			permitted_octave = int(arg)
		elif opt in("-octr","--octrange"):
			notes_per_octave = int(arg)
		elif opt in("-t","--time"):
			track_time = int(arg)
		elif opt in("-sg","--savegrid"):
			save_grid = int(arg)	
		elif opt in("-st","--savethumb"):
			save_thumb = int(arg)
		elif opt in("-sm","--savemidi"):
			save_midi = int(arg)
		elif opt in("-s","--save"):
			save_any = int(arg)			
	
	print("ARGS:")
	print(inputfile)
	print(outfile)
	print(outdir)
	print(grid_res_x)	
	print(grid_res_y)
	print(permitted_octave)
	print(notes_per_octave)
	print(track_time)
	print(save_grid)
	print(save_thumb)
	print(save_midi)
	print(save_any)

	#Attempt to make save directory
	if not os.path.exists(outdir):
		os.makedirs(outdir)
	
	#Image loading
	image = Image.open(inputfile)
	pixels = list(image.getdata())

	grid = [[0 for x in range(grid_res_x)] for y in range(grid_res_y)]
	#rgb_grid = [(0,0,0) for x in range(grid_res_x*grid_res_y)]
	#range_grid_x = image.size[0]/grid_res_x # the x grid lengths
	#range_grid_y = image.size[1]/grid_res_y # the y grid lengths

	# Current analysis method resizes image using PIL
	thumbnail = image.rotate(90).resize([grid_res_x,grid_res_y], Image.ANTIALIAS)
	thumb_pixels = list(thumbnail.getdata())

	# Guiding Global Statistics
	total_mean = np.mean(pixels)
	total_std = np.std(pixels)

	# Midi Information
	Midi = MIDIFile(1) #type 1 midi - mono track, type 2 is stereo
	each_midi_duration = track_time / grid_res_x # the duration that each midi will be 


	# Grid-Filling Loop

	for i in range(0,grid_res_x):
		for j in range(0,grid_res_y):
		   # min_grid_x = i*range_grid_x
		   # max_grid_x = min_grid_x + range_grid_x
		   # min_grid_y = i*range_grid_y
		   # max_grid_y = min_grid_y + range_grid_y
			subimage = thumb_pixels[i*grid_res_y+j] #current method for sampling is just to resize the image
			subimage_mean = np.mean(subimage)
			#print(subimage_mean)
			if subimage_mean >= total_mean+total_std:
				grid[j][i] = 255
				#rgb_grid[i*grid_res_y+j] = (255,255,255)

	# Midi Filling Loop

	track = 0
	tempo = 120
	volume = 100
	for i in range(0,grid_res_x):
		for j in range(0,grid_res_y):
			if (grid[j][i] == 255):
				time = i
				Midi.addTrackName(track,time,"Time Track :*{} and {}*:".format(i,j))
				Midi.addTempo(track,time,tempo)
				channel = 0 #trying now with just one channel
				pitch = j%144 #midi notes only go up to 127, but we go to 144
				octave = (pitch/12)%10 # only support 10 octaves
				pitch = toKey("CM",pitch)
				Midi.addNote(track,channel,pitch,time,each_midi_duration,volume)


	#Video Creation -- Currently not synced with Audio
	if (save_any):
		grid_file = Image.fromarray(np.asarray(grid)*255)
		if (save_grid):
			grid_file.save(outdir + "/grid_output.png")
		if (save_thumb):
			thumbnail.save(outdir + "/thumbnail.png")
	#fourcc = cv2.VideoWriter_fourcc(*'DIVX')
	#video = cv2.VideoWriter("demo.avi",-1,2.3,(grid_res_x,grid_res_y))
	'''
	for i in range(grid_res_x):
		copy_grid = rgb_grid
		for j in range(len(grid[i])):
			copy_grid[i*len(grid[i])+j] = (0,0,255)
		copy_grid_image = Image.new(image.mode,thumbnail.size)
		copy_grid_image.putdata(copy_grid)
		video.write(np.array(copy_grid_image))

	video.release()

	''' 
	if (save_any and save_midi):
		binfile = open(outdir + "/output.mid", 'wb')
		Midi.writeFile(binfile)
		binfile.close()

	#ffmpy export for video 
	#ff = ffmpy.FFmpeg( inputs = {'demo.avi':None, 'output.wav': None}, outputs={'final.avi':'-y -c:v h264 -c:a ac3'})
	#ff.run()

	print("Finished")

#ToKey maps absolute pitches to nearest pitches in a key
def toKey(key,absolute_pitch):
	global permitted_octave
	global notes_per_octave
    #first, get the notes in the key
	key_notes = config.get("keys",key).split() 
	key_midi_values = np.asarray([None]*len(key_notes))
	octave = (absolute_pitch/(notes_per_octave-1))%(permitted_octave) #restrict by the allowed octave limit
	for i in range(len(key_notes)):
		key_midi_values[i] = config.getint("notes",key_notes[i])+(notes_per_octave)*octave #map the grabbed key notes to the correct octave
	key_midi_values[len(key_notes)-1] = key_midi_values[0] + notes_per_octave*(octave+1) #last value in key will be the tonic up an octave
	distances = np.abs(key_midi_values - absolute_pitch) #currently using absolute value distance. Makes sense given 1d values
	min_distance_index = distances == min(distances) #indexing 
	return key_midi_values[min_distance_index][0] #heuristic, if distances are equal, just choose the nearest note

	
if __name__ == '__main__':
	global config
	global permitted_octave
	global notes_per_octave
	global track_time
	global grid_res_x
	global grid_res_y
	global inputfile
	global outfile
	global outdir
	global save_midi
	global save_any
	global save_grid
	global save_thumb
	config = ConfigParser.ConfigParser()
	config.readfp(open("EdgeMidi.cfg"))

	#Read Default values from config file prior to argument parsing
	permitted_octave = config.getint("midi","permitted_octaves")
	notes_per_octave = config.getint("midi","notes_per_octave")
	track_time = config.getint("midi","default_track_time") #seconds #BUG - currently track time is not working correctly
	grid_res_x = config.getint("analysis","default_x_res") #units # make it the same as the duration for initial simplicity
	grid_res_y = config.getint("analysis","default_y_res") # the range of the y grid, not quite pitches
	inputfile = config.get("io","default_infile")
	outfile = config.get("io","default_outfile")
	outdir = config.get("io","default_outdir")
	save_midi = config.getint("io","default_save_midi")
	save_any = config.getint("io","default_save")
	save_grid = config.getint("io","default_save_grid")
	save_thumb = config.getint("io","default_save_thumb")

	main(sys.argv[1:])	