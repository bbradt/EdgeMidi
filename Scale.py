# -*- coding: utf-8 -*-
"""
Created on Sun May 27 03:14:48 2018

@author: Brad
"""

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

class Scale():
    def __init__(self,tonic=DEF_TONIC, octave=DEF_OCTAVE, scale=DEF_SCALE):
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

    def _build_octave(self, octave):
        tonic = "%s%d" % (self.tonic[0], octave)
        keys = [tonic]
        for degree, interval in enumerate(self.intervals):
            keys.append(self._next_key(self.keys[degree], degree))
        return keys
    
    def _in_octave(self, frequency, octave):
        octave = self._build_octave(octave)
        return frequency > np.min(octave) and frequency < np.max(octave)
    
    def _next_key(self, key, degree):
        return key + INTERVALS[self.intervals[degree]]
    
    def _closest_note(self, frequency, frequencies=None):
        if frequencies is None:
            frequencies = self.frequencies
        distances = frequency - frequencies
        chosen = np.where(distances == np.min(distances))
        return frequencies[chosen[0]]
    
    def transpose(self, frequency):
        octave = None
        for oct_num in range(8):
            if self._in_octave(frequency, oct_num):
                octave = self._build_octave(oct_num)
                break
        if octave is None:
            return frequency
        return self._closest_note(frequency, frequencies=octave)
        


if __name__ == '__main__':
    scale = Scale()