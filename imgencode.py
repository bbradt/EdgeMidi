#!/usr/bin/python

import cv2
import progressbar
import wave, sys, getopt, array
import numpy as np
acceptable = np.array([261.63, 293.66, 329.99, 349.32, 392.00, 440.00, 493.88, 523.25])
def start(inputfile, outputfile, duration):
    print(inputfile)
    rgb_im = cv2.imread(inputfile)
    width, height, channels = rgb_im.shape
    M = cv2.getRotationMatrix2D((height/2, width/2), 90, 1)
    rgb_im = cv2.warpAffine(rgb_im, M, (height, width))
    width, height, channels = rgb_im.shape
    durationSeconds = float(duration) 
    tmpData = []
    maxFreq = 0
    data = array.array('h')
    sampleRate = 44100
    channels = 1
    dataSize = 2 
    
    numSamples = int(sampleRate * durationSeconds)
    samplesPerPixel = np.floor(numSamples / width)
    
    C = 20000 / height
    print('Encoding...')
    with progressbar.ProgressBar(max_value=numSamples) as bar:
        for x in range(numSamples):
            rez = 0
            pixel_x = int(x / samplesPerPixel)
            if pixel_x >= width:
                pixel_x = width -1
            for y in range(height):
                volume = np.sum(rgb_im[pixel_x, y])*100/765
                if volume == 0:
                    continue        
                freq = C * (height - y + 1)
                rez += np.int(volume * np.sin(freq * np.pi * 2 * x /sampleRate)) 
            tmpData.append(rez)
            if abs(rez) > maxFreq:
                maxFreq = abs(rez)
            bar.update(x)
    
    for i in range(len(tmpData)):
        data.append(int(32767 * tmpData[i] / maxFreq))
    print('Writing...')
    f = wave.open(outputfile, 'w')
    f.setparams((channels, dataSize, sampleRate, numSamples, "NONE", "Uncompressed"))
    f.writeframes(data.tobytes())
    f.close()
    return data

if __name__ == '__main__':
    inputfile = ''
    outputfile = ''
    duration = ''
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:o:t:")
    except getopt.GetoptError:
        print('imgencode.py -i <input_picture> -o <output.wav> -t <duration_seconds>')
        sys.exit(2)
        
    for opt, arg in opts:
        if opt == '-h':
            print('imgencode.py -i <input_picture> -o <output.wav> -t <duration_seconds>')
            sys.exit()
        elif opt == "-i":
            inputfile = arg
        elif opt == "-o":
            outputfile = arg
        elif opt == "-t":
            duration = arg

    start(inputfile, outputfile, duration)
