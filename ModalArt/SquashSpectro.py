# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# Name:        SquashSpectro.py
# Purpose:     Generation of Wavfile by Quantized Spectrogram
#
# Author:      Bradley Baker # BBradT at {gmail} dot com
#
# Created:     2018/05/26 (May 26 2018)
# Copyright:   (c) 2018 Bradley Baker
# License:     Please see License.txt for the terms under which this
#              software is distributed.
#-----------------------------------------------------------------------------


import os
import cv2
import wave
import configparser
import numpy as np
import progressbar
import Scale
import array
import getopt
import sys

def encode(image_data, scale=None):
    global fmax
    global fmin
    global amplitude
    global duration
    global sample_rate
    real_duration = int(duration*sample_rate)
    rgb = np.sum(cv2.resize(image_data,
                            (int(fmax)-int(fmin),
                             real_duration)),2)
    signal = 0
    max_sig = 0
    data = []
    final = array.array('h')
    with progressbar.ProgressBar(max_value=real_duration) as bar:
        for x in range(real_duration):
            for y in range(int(fmax)-int(fmin)):
                frequency = rgb[x, y]+int(fmin)
                frequency = scale.transpose(frequency)
                signal += amplitude*np.sin(2 * np.pi * x * frequency)
            if abs(signal) > max_sig:
                max_sig = abs(signal)
            data.append(signal)
            bar.update(x)
        for d in data:
            final.append(int(32767 * d / max_sig))
    return final
    
def main(argv):
    global inputfile
    global outdir
    global outfile
    global tonic
    global scale_name
    global duration
    global octave
    global amplitude
    global fmin
    global fmax
    global sample_rate
    print("****Squashed Spectrogram****")
    scale = Scale.Scale(tonic=tonic, octave=octave, scale=scale_name)
    if fmin is None or fmin == '':
        fmin = np.min(scale.frequencies)
    if fmax is None or fmax == '':
        fmax = np.max(scale.frequencies)
    try:
        opts, args = getopt.getopt(argv,"hi:o:t:s:a:",["ifile=","tonic=","scale=","octave=","amplitude=","od=","odir=","ofile="])
    except getopt.GetoptError:
        print('USAGE: TextKeywordImage.py -i <InputText> -o <OutputFileName>')
        sys.exit(2)
        
    for opt, arg in opts:
        if opt == '-h':
            print('TextKeywordImage.py -i <InputImage> [-o <OutputFile> -od <OutputDirectory>  -g <# Groups of Images> -r <Size> -l <Limit of Images> -u <Usage rights> -c <Color Type> -f <Image Format>]')
        elif opt in ("-i","--ifile"):
            inputfile = arg
        elif opt in ("-o","--ofile"):
            outfile = arg
        elif opt in ("-od","--odir"):
            outdir = arg
        elif opt in ("-t","--tonic"):
            tonic = arg
        elif opt in ("-s", "--scale"):
            scale = arg
        elif opt in ('-oc', "--octave"):
            octave = int(arg)
        elif opt in ('-a', '--amplitude'):
            amplitude = float(arg)

    _, ext = os.path.split(inputfile)
    image_data = cv2.imread(inputfile)
    print("Encoding...")
    encoded = encode(image_data, scale)
    print("Saving wavfile to %s..." % os.path.join(outdir, outfile))
    f = wave.open(os.path.join(outdir, outfile), 'w')
    f.setparams((1, 2, 44100, duration, "NONE", "Uncompressed"))
    f.writeframes(encoded.tobytes())
    print("Done...")

if __name__ == "__main__":
    global inputfile
    global outdir
    global outfile
    global tonic
    global scale_name
    global duration
    global octave
    global amplitude
    global fmax
    global fmin
    global sample_rate
    config = configparser.ConfigParser()
    config.readfp(open("config.cfg"))
    
    inputfile = config.get("io","default_spc_infile")
    outfile = config.get("io","default_spc_outfile")
    outdir = config.get("io","default_spc_outdir")
    tonic = config.get("spectro", "default_tonic")
    scale_name = config.get("spectro", "default_scale")
    duration = config.getint("spectro", "default_duration")
    octave = config.getint("spectro", "default_octave")
    amplitude = config.getfloat("spectro", "default_amplitude")
    fmin = config.get("spectro", "default_fmin")
    fmax = config.get("spectro", "default_fmax")
    sample_rate = config.getint("io", "default_sample_rate")
    main(sys.argv[1:])   
    