# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 20:54:23 2017

@author: bbaker94


"""

def find_nearest_c(relative_pitch,octave):
    return 60

filename = "sample.md"

#Using the MidiUtil library
from MidiFile import MIDIFile
from PIL import Image
import numpy as np
import ConfigParser
import cv2
import ffmpy
import MidiConvert as mc
config = ConfigParser.ConfigParser()

def toKey(key,absolute_pitch):
    #first, get the notes in the key
    config.readfp(open("EdgeMidi.cfg"))
    key_notes = config.get("keys",key).split()
    key_midi_values = np.asarray([None]*len(key_notes))
    octave = (absolute_pitch/11)%10 # only allow 10 octaves
    for i in range(len(key_notes)):
        key_midi_values[i] = config.getint("notes",key_notes[i])+12*octave
    key_midi_values[len(key_notes)-1] = key_midi_values[0] + 12*(octave+1)
    distances = np.abs(key_midi_values - absolute_pitch)
    min_distance_index = distances == min(distances)
    return key_midi_values[min_distance_index][0]

# Create the MIDIFile Object
MyMIDI = MIDIFile(1)


#Image loading
image = Image.open("image.png")
pixels = list(image.getdata())

track_time = 30 #seconds
grid_res_x = 200 #units # make it the same as the duration for initial simplicity
grid_res_y = 200 # the range of the y grid, not quite pitches
grid = [[0 for x in range(grid_res_x)] for y in range(grid_res_y)]
rgb_grid = [(0,0,0) for x in range(grid_res_x*grid_res_y)]

thumbnail = image.rotate(90).resize([grid_res_x,grid_res_y], Image.ANTIALIAS)
thumb_pixels = list(thumbnail.getdata())
#print len(thumb_pixels)
pitch_map = 0 #do not use a pitchmap yet
total_mean = np.mean(pixels)
total_std = np.std(pixels)
print(total_mean)
each_midi_duration = track_time / grid_res_x # the duration that each midi will be 

edge_threshold = (255,255,255)#heuristic threshold for edges detected

range_grid_x = image.size[0]/grid_res_x # the x grid lengths
range_grid_y = image.size[1]/grid_res_y # the y grid lengths

# Grid-Filling Loop

for i in range(0,grid_res_x):
    for j in range(0,grid_res_y):
        min_grid_x = i*range_grid_x
        max_grid_x = min_grid_x + range_grid_x
        min_grid_y = i*range_grid_y
        max_grid_y = min_grid_y + range_grid_y
        #subimage = pixels[min_grid_x:max_grid_x][min_grid_y:max_grid_y]        
        #subimage_mean = np.mean(subimage) # maybe a more clever way to do this
        subimage = thumb_pixels[i*grid_res_y+j]
        subimage_mean = np.mean(subimage)
        #print(subimage_mean)
        if subimage_mean >= total_mean+total_std:
            grid[j][i] = 255
            rgb_grid[i*grid_res_y+j] = (255,255,255)
# Midi Filling Loop

track = 0
tempo = 120
volume = 100
for i in range(0,grid_res_x):
    for j in range(0,grid_res_y):
        if (grid[j][i] == 255):
            time = i
            MyMIDI.addTrackName(track,time,"Time Track :*{} and {}*:".format(i,j))
            MyMIDI.addTempo(track,time,tempo)
            channel = 0 #trying now with just one channel
            pitch = j%144 #midi notes only go up to 127, but we go to 144
            octave = (pitch/12)%10 # only support 10 octaves
            pitch = toKey("CM",pitch)
            MyMIDI.addNote(track,channel,pitch,time,each_midi_duration,volume)
# Add a note. addNote expects the following information:


grid_file = Image.fromarray(np.asarray(grid)*255)
grid_file.save("grid_output.png")
thumbnail.save("thumbnail.png")
#fourcc = cv2.VideoWriter_fourcc(*'DIVX')
video = cv2.VideoWriter("demo.avi",-1,2.3,(grid_res_x,grid_res_y))

for i in range(grid_res_x):
    copy_grid = rgb_grid
    for j in range(len(grid[i])):
        copy_grid[i*len(grid[i])+j] = (0,0,255)
    copy_grid_image = Image.new(image.mode,thumbnail.size)
    copy_grid_image.putdata(copy_grid)
    video.write(np.array(copy_grid_image))

video.release()


# Now add the note.

binfile = open("output.mid", 'wb')
MyMIDI.writeFile(binfile)
binfile.close()
#binfile = open("output.wav","wb")
#MyMIDI.writeFile(binfile)
#binfile.close()
mc.convert_midi("output.mid")
ff = ffmpy.FFmpeg( inputs = {'demo.avi':None, 'output.wav': None}, outputs={'final.avi':'-y -c:v h264 -c:a ac3'})
ff.run()
print("finished")

