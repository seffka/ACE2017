import sys
import os
from essentia.streaming import *
from essentia.standard import BeatTrackerMultiFeature
from essentia.standard import ChordsDetectionBeats
import essentia_chord_utils
import numpy as np
import vamp

#1.3sec: 74.0534%
#2.75: 76.0055%
def chordBeats(infile, outfile) :
    mywindow = np.array([0.001769, 0.015848, 0.043608, 0.084265, 0.136670, 0.199341, 0.270509, 0.348162, 0.430105, 0.514023,
                0.597545, 0.678311, 0.754038, 0.822586, 0.882019, 0.930656, 0.967124, 0.990393, 0.999803, 0.999803,
                0.999803, 0.999803, 0.999803, 0.999803, 0.999803, 0.999803, 0.999803, 0.999803, 0.999803, 0.999803,
                0.999803, 0.999803, 0.999803,  0.999803, 0.999803,
                0.999803, 0.999803, 0.999803, 0.999803, 0.999803, 0.999803, 0.999803, 0.999650, 0.996856, 0.991283,
                      0.982963, 0.971942, 0.958281, 0.942058, 0.923362, 0.902299, 0.878986, 0.853553, 0.826144,
                      0.796910, 0.766016, 0.733634, 0.699946, 0.665140, 0.629410, 0.592956, 0.555982, 0.518696,
                      0.481304, 0.444018, 0.407044, 0.370590, 0.334860, 0.300054, 0.266366, 0.233984, 0.203090,
                      0.173856, 0.146447, 0.121014, 0.097701, 0.076638, 0.057942, 0.041719, 0.028058, 0.017037,
                      0.008717, 0.003144, 0.000350])

    #    chroma_cq = librosa.feature.chroma_cqt(y=y, sr=44100)
    audio = essentia.standard.MonoLoader(filename = infile)()
    bt = BeatTrackerMultiFeature()
    beats, _ = bt(audio)
    #beats = beats[::4]

    parameters = {}
    stepsize, semitones = vamp.collect(
        audio, 44100, "nnls-chroma:nnls-chroma", output = "semitonespectrum", step_size=2048)["matrix"]
    chroma = np.zeros((semitones.shape[0], 12))
    for i in range(semitones.shape[0]):
        tones = semitones[i] * mywindow
        cc = chroma[i]
        for j in range(tones.size):
            cc[j % 12] = cc[j % 12] + tones[j]
    chroma = essentia_chord_utils.smooth(chroma, window_len= int(2.0 * 44100 / 2048), window='hanning').astype('float32')
    chords = ChordsDetectionBeats(hopSize=2048)
    syms, strengths = chords(chroma, beats)

    segments = essentia_chord_utils.toMirexLab(0.0, len(audio) / 44100.0, beats, syms, strengths)
    with open(outfile, 'w') as content_file:
        for s in segments:
            content_file.write(str(s) + '\n')

try:
    infile = sys.argv[1]
    outfile = sys.argv[2]
except:
    print "usage:", sys.argv[0], "<input directory (with audio)> <output lab directory>"
    sys.exit()
essentia_chord_utils.processFiles(infile, outfile, chordBeats)

