# ModalArt v 0.0.3
**Art Between Modalities**

**Author: Bradley Baker**

*Currently in development.*

## Version History:
	0.0.1 - Initial Development Version
	0.0.2 - Added more flexible support for scales, 
            	and support of spectrogram img-encoding
	0.0.3 - Moved to Python3, Added Text to Image Converter, 
            	additional Spectrogram encoding, 
            	and updates to EdgeMidi

## Description

This package strives to foster the creation of art by conversion
of data modalities, facilitating new perspectives on the art-creation
process and the art-encounter via technology.

Current functionality targets conversion between RGB images, audio, and text;
however, conversion between other kinds of data and art modalities will
be explored in the future.

Feedback is appreciated. 

### EdgeMidi

Midi works most simply in two dimensions - the Pitch (Y) dimension, and the Time (X) dimension. There are additional 
dimensions given in the intensity of the strike on the virtual keyboard and in the channel chosen, etc; however, the simpleest
mapping imagines these values as pre-determined constants, such that the MIDI functionality involves some mapping of 
pitches over time. 

Similarly images at their most basic have two spatial dimensions, an X and Y spatial axis. The idea of this program is 
thus spatial information given in an image to create a mapping from the image into this basic MIDI-space. There are 
many potential mappings from the image-space into MIDI-basic-space and into other MIDI spaces; however, one simple 
mapping uses a binary-spatial-indicator to detect whether or not an image is present at a given spatial coordinate in an 
image, and if so, adds a positive binary indicator to the same coordinate in the MIDI-basic-space. 

To put it simply, we imagine that the MIDI-basic-space of pitches over time is placed as a grid over an image. Then, wherever
we detect an edge in the image at a coordinate (x,y), we indicate that pitch (y) should be played at time (x). 

This software performs 2 basic functions:
	1) Edge Detection
	2) Edge -> MIDI mapping 
	
Beyond these basic functions, there is the included functionality of mapping images to particular Musical Keys.

### Spectrogram Analysis

Converts image data into a spectrogram which can be used to generate .wav files.
[Alexodan's img-encode library](https://github.com/alexadam/img-encode) is included,
and additional "Squashed" analysis provides quantization of the spectrogram
to a particular choice of scale.

All scales in scales.csv are currently supported.

### Text Keyword Image

With input text, this module queries google images for images with related keywords.
Queries are currently made naively, line by line.
The library outputs a generated image created by combining the queried images.

For example, we take the text of "Ten Maps of Sardonic Wit" by Christian Bok:

    Ten Maps of Sardonic Wit

    atoms in space now drift
    on a swift and epic storm
    
    soft wind can stir a poem
    
    snow fits an optic dream
    into a scant prism of dew
    
    words spin a faint comet
    
    some words in fact paint
    two stars of an epic mind
    
    manic words spit on fate

and output the following image:

![alt text](https://raw.githubusercontent.com/bbradt/ModalityAudio/master/output/example/example.png)

## Support

I am looking for active co-developers. 
Contact me at bbradt.com if you would like to contribute.



## Features

Version 0.0.3:

    EdgeMidi

		MIDI mapping and output for Images already Edge-Detected
		All MAJOR scales
		All MINOR scales
		GNU-style Command-Line arguments for: 
			Adjusting resolution of grid
			Input/Output
			Turning debugging on/off
			more 
		Pitch-Grid Debugging Outputs
		Customizeable Config File

	Spectro

    	Squashed Spectrogram Analysis with Quantization
    	Additional ImgEncode functionality
    		based on [alexodan's img-encode library](https://github.com/alexadam/img-encode)

    TextKeywordImage

        Generate an Image based on text

Features coming:

   GUI
	Unit Tests
	Image-Format Tests
	Edgemidi
	
    	More command line arguments:
    		Adjust MIDI Tempo
    		Adjust MIDI Volume
    	Alternative Octave-Grid Wrapping Choices
    	Dynamic Image Transformation : 
    	Auto-Playback
    	Generation of Video including time-marker showing pitch-playback 
    	Auto-Dependency Check/Installation

	More Scales

		Full Harmonic Scales
		All augmented/diminished keys
		All modes for major/minor keys
		Blues scales
		Jazz scales 
		...
	
Usage: 
	Required Packages:
		See requirements.txt

	The tool is used only via the command line currently. A GUI is on the TODO list.
	For now, the tool can be used via the command:
		$python EdgeMidi.py -i <inputfile> 
		$python TextKeywordImage.py -i <inputfile>
		$python SquashSpectro.py -i <inputfile>
	
	For additional flags and arguments via the command line, type 
		python EdgeMidi.py -h 
		python TextKeywordImage.py -h
		python SquashSpectro.py -h
