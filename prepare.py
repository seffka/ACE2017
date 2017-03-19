import sys
import os
from essentia.streaming import *
from essentia.standard import BeatTrackerMultiFeature
import numpy as np
import vamp
from madmom.features.beats import DBNBeatTrackingProcessor
from madmom.features.beats import RNNBeatProcessor

def chordBeats(infile, outfile) :
    print 'Loading audio file...', infile

    #proc = BeatTrackingProcessor(
    #    fps = 100,
    #    method='comb', min_bpm=40,
    #    max_bpm=240, act_smooth=0.09,
    #    hist_smooth=7, alpha=0.79)
    proc = DBNBeatTrackingProcessor(
        fps = 100,
        method='comb', min_bpm=40,
        max_bpm=240)
    act = RNNBeatProcessor()(infile)
    beats = proc(act).astype('float32')
    audio = essentia.standard.MonoLoader(filename = infile)()
    # TODO: best partameters.
    parameters = {}
    stepsize, semitones = vamp.collect(
        audio, 44100, "nnls-chroma:nnls-chroma", output = "semitonespectrum", step_size=2048)["matrix"]
    np.savez(outfile, [len(audio)], beats, semitones)

def processFiles(inputDir, outputDir) :
    for file in [f for f in os.listdir(inputDir) if os.path.isfile(os.path.join(inputDir, f))] :
        name, ext = os.path.splitext(file)
        chordBeats(
            os.path.join(inputDir, file),
            os.path.join(outputDir, name + '.npz'))


#chordBeats("audio/01_-_It_Won't_Be_Long.wav", "q.txt")
#quit()
try:
    infile = sys.argv[1]
    outfile = sys.argv[2]
except:
    print "usage:", sys.argv[0], "<input directory (with audio)> <output npz directory>"
    sys.exit()
processFiles(infile, outfile)

