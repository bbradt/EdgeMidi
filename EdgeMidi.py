# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# Name:        EdgeMidi.py
# Purpose:     Generation of Midi Tracks using Edge-Detection
#
# Author:      Bradley Baker # BBradT at {gmail} dot com
#
# Created:     2017/02/22  (February 22 2017)
# Copyright:   (c) 2017 Bradley Baker
# License:     Please see License.txt for the terms under which this
#              software is distributed.
#-----------------------------------------------------------------------------

#Using the MidiUtil library
from MidiUtil import MIDIFile
import numpy as np
import configparser
import scipy.io as sio
import cv2
import Scale
import sys, getopt, os
import progressbar

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
    global input_key
    try:
        opts, args = getopt.getopt(argv,"hi:o:x:y:t:s:k:",["od=","xr=","yr=","oct=","octr=","sg=","st","sm","ifile=","ofile=","xres=","yres=","octaves=","octrange=","time=","savegrid=","savethumb=","savemidi=","save=","odir="])
    except getopt.GetoptError:
        print('EdgeMidi.py -i <InputImage> -o <OutputFileName>')
        sys.exit(2)
        
    for opt, arg in opts:
        if opt == '-h':
            print('EdgeMidi.py -i <InputImage> [-o <OutputFilePrefix> -x <XResolution> -y <YResolution> -s <SaveFiles>]')
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
        elif opt in("-k"):
            input_key = arg

    #Attempt to make save directory
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    print("Initializing")        
    #Image loading
    image = cv2.imread(inputfile,0)
    
    grid = np.zeros((grid_res_y,grid_res_x))
    pitch_grid = np.zeros((grid_res_y,grid_res_x))

    # Current analysis method resizes image using PIL
    thumbnail = cv2.resize(image,(grid_res_x,grid_res_y),interpolation= cv2.INTER_CUBIC)#image.rotate(0).resize([grid_res_x,grid_res_y], Image.ANTIALIAS)
    edges = cv2.Canny(thumbnail,200,300)
    thumbnail = edges
    cv2.imwrite(outdir + "/edge_output.png",edges)
    # Guiding Global Statistics
    total_mean = np.mean(image)
    def test_edge(arg1,arg2):
        return arg1 < arg2
    if (np.sum(test_edge(image,total_mean)) > thumbnail.size/2):
        def test_edge(arg1,arg2):
            return (arg1 > arg2)
    
    # Midi Information
    Midi = MIDIFile(1) #type 1 midi - mono track, type 2 is stereo
    each_midi_duration = track_time / grid_res_x # the duration that each midi will be 

    # Main Loop
    tempo = 120
    volume = 100
    track = 0
    print("Creating Midi File")
    with progressbar.ProgressBar(max_value=grid_res_y*grid_res_x) as bar:
        for i in range(0,grid_res_y):
            for j in range(0,grid_res_x):
                subimage_mean = np.mean(thumbnail[i][j])
                volume = 100
                time = j
                Midi.addTrackName(track,time,"Track *{}*:".format(i))
                Midi.addTempo(track,time,tempo)
                channel = 0 #trying now with just one channel
                if test_edge(subimage_mean,total_mean):
                    grid[i][j] = 255
                    pitch = i 
                    pitch = toKey(input_key,pitch)
                else: 
                    pitch = 0
                    volume = 0
                pitch_grid[i][j] = pitch
                Midi.addNote(track,channel,pitch,time,each_midi_duration,volume)    
                bar.update(i*grid_res_x+j)

    if (save_any):
        if (save_grid):
            print("Saving debug images")
            np.save(outdir + '/pitch.grid',pitch_grid)
            cv2.imwrite(outdir + "/grid_output.png",grid.astype('uint8'))
            cv2.imwrite(outdir + "/pitch_grid_output.png",pitch_grid.astype('uint8'))
        if (save_thumb):
            print("Saving thumbnail")
            cv2.imwrite(outdir + "/thumbnail.png",thumbnail)

    if (save_any and save_midi):
        print("Saving midi")
        binfile = open(outdir + "/" + outfile +".mid", 'wb')
        Midi.writeFile(binfile)
        binfile.close()

    print("Finished")

#ToKey maps absolute pitches to nearest pitches in a key
def toKey(key,absolute_pitch):
    global permitted_octave
    global notes_per_octave
    global octave_buffer
    #first, get the notes in the key
    scale = Scale.Scale(scale=key)
    key_notes = config.get("keys",key).split() 
    print(key_notes)
    key_midi_values = np.asarray([None]*len(key_notes))
    octave = (absolute_pitch/(notes_per_octave-1))%(permitted_octave) + octave_buffer#restrict by the allowed octave limit
    for i in range(len(key_notes)):
        key_midi_values[i] = config.getint("notes",key_notes[i])+(notes_per_octave)*octave #map the grabbed key notes to the correct octave
    key_midi_values[len(key_notes)-1] = key_midi_values[0] + notes_per_octave*(octave+1) #last value in key will be the tonic up an octave
    distances = np.abs(key_midi_values - absolute_pitch) #currently using absolute value distance. Makes sense given 1d values
    min_distance_index = distances == min(distances) #indexing 
    return key_midi_values[min_distance_index][0] #heuristic, if distances are equal, just choose the nearest note

def updateLoadBar(iterator,total):
    full_percent = total/100
    bar = "["
    for i in range(0,100):
        if iterator >= i * full_percent-1:
            bar += "#"
        else: bar += "."
    bar += "]\r"
    sys.stdout.write(bar)
    if (iterator == total-1):
        sys.stdout.write("\n")
        
if __name__ == '__main__':
    global config
    global permitted_octave
    global octave_buffer
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
    global input_key
    config = configparser.ConfigParser()
    config.readfp(open("EdgeMidi.cfg"))

    #Read Default values from config file prior to argument parsing
    permitted_octave = config.getint("midi","permitted_octaves")
    notes_per_octave = config.getint("midi","notes_per_octave")
    octave_buffer = config.getint("midi","default_octave_buffer")
    track_time = config.getint("midi","default_track_time") #seconds #BUG - currently track time is not working correctly
    grid_res_x = config.getint("analysis","default_x_res") #units # make it the same as the duration for initial simplicity
    grid_res_y = config.getint("analysis","default_y_res") # the range of the y grid, not quite pitches
    inputfile = config.get("io","default_emd_infile")
    outfile = config.get("io","default_emd_outfile")
    outdir = config.get("io","default_emd_outdir")
    save_midi = config.getint("io","default_save_midi")
    save_any = config.getint("io","default_save")
    save_grid = config.getint("io","default_save_grid")
    save_thumb = config.getint("io","default_save_thumb")
    input_key = config.get("analysis","default_key")
    main(sys.argv[1:])    
