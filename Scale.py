# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# Name:        Scale.py
# Purpose:     Quantize frequencies based on scale
#
# Author:      Bradley Baker # BBradT at {gmail} dot com
#
# Created:     2018/05/26 (May 26 2018)
# Copyright:   (c) 2018 Bradley Baker
# License:     Please see License.txt for the terms under which this
#              software is distributed.
#-----------------------------------------------------------------------------


import pandas as pd
import numpy as np

DEF_TONIC = 'C'
DEF_OCTAVE = 4
DEF_SCALE = 'major'

FLAT_CHAR = '♭'
SHARP_CHAR = '♯'
SCALE_FILE = 'scales.csv'
KEY_FILE = 'keys.csv'

SCALES = pd.read_csv(SCALE_FILE, encoding='utf-8')
KEYS = pd.read_csv(KEY_FILE, encoding='utf-8')
INTERVALS = {'W':2, 'H':1, '3H':3, '2W':4}
MIN_FREQUENCY = np.min(KEYS['Frequency'])
MAX_FREQUENCY = np.max(KEYS['Frequency'])
OCTAVE_DISTANCE = 220

class Scale():
    def __init__(self,tonic=DEF_TONIC, octave=DEF_OCTAVE, scale=DEF_SCALE):
        '''
            A Scale object has a:
                octave
                tonic pitch
                tonic frequency
                tonic key
                name
                set of intervals
                set of degrees
                set of keys in the scale
                set of frequencies in the scale
                set of pitches in the scale
                and a set of equivalent scales in different octaves
        '''
        self.octave = octave
        self.tonic = '%s%d' % (tonic, self.octave)
        self.name = scale
        self.intervals = SCALES.loc[SCALES['Name']==self.name, 'Intervals'].iloc[0].split('-')
        self.degrees = SCALES.loc[SCALES['Name']==self.name, 'Degrees'].iloc[0].split()
        self.tonic_frequency = KEYS.loc[KEYS['Pitch'].str.contains(self.tonic), 'Frequency'].iloc[0]
        self.tonic_key = KEYS.loc[KEYS['Pitch'].str.contains(self.tonic), 'Key'].iloc[0]
        self.keys = [self.tonic_key]
        for degree, interval in enumerate(self.intervals):
            self.keys.append(self._next_key(self.keys[degree], degree))
        self.pitches = [KEYS.loc[KEYS['Key'] == key, 'Pitch'].iloc[0] for key in self.keys]
        self.frequencies = [KEYS.loc[KEYS['Key'] == key, 'Frequency'].iloc[0] for key in self.keys]
        self.octaves = [self._build_octave(i) for i in range(8)]
        self.octave_tonic_frequencies = [octave[0] for octave in self.octaves]

    def _build_octave(self, octave):
        '''
            Construct the frequencies in the scale belonging to a particular
            octave. 
                (Multiple calls to this function increase runtime
                     recommend only calling in the constructor.)
        '''
        tonic = "%s%d" % (self.tonic[0], octave)
        freqs = [KEYS.loc[KEYS['Pitch'].str.contains(tonic), 'Frequency'].iloc[0]]
        for degree, interval in enumerate(self.intervals):
            freqs.append(self._next_frequency(freqs[degree], degree))
        return freqs
    
    def _in_octave(self, frequency, oct_num):
        '''
            Check if a note falls inside a given octave range
        '''
        return bool(frequency > np.min(self.octaves[oct_num])
                    and frequency < np.max(self.octaves[oct_num]))
    
    def _next_key(self, key, degree):
        '''
            Grab the next piano key in the scale, according to the current
                degree in the scale.
        '''
        return key + INTERVALS[self.intervals[degree]]
		
    def _next_frequency(self, frequency, degree):
        '''
            Grab the next frequency in the scale, according to the current
                degree in the scale.
        '''
        key = KEYS.loc[KEYS['Frequency'] == frequency, 'Key'].iloc[0]
        next_key = self._next_key(key, degree)
        return KEYS.loc[KEYS['Key'] == next_key, 'Frequency'].iloc[0]
	
    def _closest_octave(self, frequency):
        '''
            Returns the closest octave by absolute distance to the tonic frequencies
            of the octaves.
        '''
        distances = frequency - np.asarray(self.octave_tonic_frequencies)
        chosen = np.where(np.abs(distances) == np.min(np.abs(distances)))
        return int(chosen[0])
    
    def _closest_note(self, frequency, frequencies=None):
        '''
            Grab the closest note according to the set of own frequencies
                or according to some other list of frequencies.
        '''
        if frequencies is None:
            frequencies = self.frequencies
        while frequency < MIN_FREQUENCY or frequency > MAX_FREQUENCY:
            while frequency < MIN_FREQUENCY:
                frequency += OCTAVE_DISTANCE
            while frequency > MAX_FREQUENCY:
                frequency -= OCTAVE_DISTANCE
        distances = frequency - np.asarray(frequencies)
        chosen = np.where(np.abs(distances) == np.min(np.abs(distances)))
        return frequencies[int(chosen[0])]
    
    def transpose(self, frequency, outside_octave=True):
        '''
            Transposes a note to the nearest octave equivalent in the scale.
                args: frequency - the input frequency
                      outside_octave - check outside the set octave 
                                          (increases runtime slightly)
        '''
        octave = self.octaves[self._closest_octave(frequency)] if outside_octave else self.frequencies
        return self._closest_note(frequency, frequencies=octave)



if __name__ == '__main__':
    scale = Scale()