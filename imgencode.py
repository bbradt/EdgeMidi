#!/usr/bin/python

import cv2
import progressbar
import wave, sys, getopt, array
import numpy as np
from Scale import Scale
from multiprocessing import Process, Queue
quant_scale = Scale()
def do_y(q, data_x, sampleRate, height, C, x):
            rez = 0
            for y in range(height):
                volume = np.sum(data_x[y])*100/765
                if volume == 0:
                    continue        
                freq = C * (height - y + 1)
                freq = quant_scale.transpose(freq)
                rez += np.int(volume * np.sin(freq * np.pi * 2 * x /sampleRate)) 
            q.put(rez)

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
    max_procs = 20
    xhit = []
    for pr in range(int(np.ceil(numSamples/max_procs))):
        queues = []
        procs = []
        i = 0
        for x in range(numSamples):
            if x in xhit:
                continue
            pixel_x = int(x / samplesPerPixel)
            if pixel_x >= width:
                pixel_x = width -1
            data_x = rgb_im[pixel_x,:]
            q = Queue()
            queues.append(q)
            p = Process(target=do_y, args=(queues[i], data_x, sampleRate, height, C, x))
            i+=1
            p.start()
            procs.append(p)
            if len(procs) > max_procs:
                break
            xhit.append(x)

        for p, q in zip(procs, queues):
            rez = q.get()
            p.join()
            tmpData.append(rez)           
            if abs(rez) > maxFreq:
                maxFreq = abs(rez)
        print("Done with sample %d/%d" % (x,numSamples))
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
