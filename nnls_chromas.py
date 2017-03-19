import csv
import sys
import os
from essentia.streaming import *
from essentia.standard import BeatTrackerMultiFeature
from essentia.standard import ChordsDetectionBeats
import essentia_chord_utils
import numpy as np
import vamp

#4: 69.6416
#2: 68.6673
#1: 61.9565

def chordBeats(infile, outfile) :
    print 'Loading audio file...', infile
    audio = essentia.standard.MonoLoader(filename = infile)()
    bt = BeatTrackerMultiFeature()
    beats, _ = bt(audio)
    #beats = beats[::4]

    parameters = {}
    stepsize, chroma = vamp.collect(
        audio, 44100, "nnls-chroma:nnls-chroma", output = "chroma", step_size=2048)["matrix"]
    # to essentia convention
    #chroma = np.roll(chroma, 3, 1)

    chords = ChordsDetectionBeats(hopSize=2048)
    syms, strengths = chords(chroma, beats)

    segments = essentia_chord_utils.toMirexLab(0.0, len(audio) / 44100.0, beats, syms, strengths)
    with open(outfile, 'w') as content_file:
        for s in segments:
            content_file.write(str(s) + '\n')

def processFiles(inputDir, outputDir) :
    for file in [f for f in os.listdir(inputDir) if os.path.isfile(os.path.join(inputDir, f))] :
        name, ext = os.path.splitext(file)
        chordBeats(
            os.path.join(inputDir, file),
            os.path.join(outputDir, name + '.lab'))

try:
    infile = sys.argv[1]
    outfile = sys.argv[2]
except:
    print "usage:", sys.argv[0], "<input directory (with audio)> <output lab directory>"
    sys.exit()
processFiles(infile, outfile)

