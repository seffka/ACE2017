import sys
from essentia.streaming import *
from essentia.standard import BeatTrackerMultiFeature
import essentia_chord_utils
import numpy as np
import vamp
from madmom.features.beats import BeatTrackingProcessor
from madmom.features.beats import RNNBeatProcessor
import sklearn.preprocessing as preprocessing
# smoothing: hanning 2.75 sec + madmom beats: gives 71.3318%
# smoothing: my chroma window + hanning 2.75 sec + DBN beats: 73.7812%
#                                                + with l2 normalization: 73.7508%
#                                                + with max normalization 73.7644%
#                                                + with l1 normalization: 73.7689%
# smoothing: my chroma window + hanning 2.75 sec + DBN beats + no "median" (just first beat): 76.2419%
# smoothing: my chroma window + hanning 2.75 sec + DBN beats + no "median" (just first beat) + HMM (p: 0.15) 77.6384%
# smoothing: my chroma window + hanning 2.75 sec + DBN beats + no "median" (just first beat) + HMM (new, with Temperley .019) 77.6604%


# TODO: normalization, down beat!!!
# smoothing: my chroma window + hanning 2.75 sec + madmom beats: gives 73.7197%

# madmom beats
# 6 beats: 58.8159% with new tempo
# 4 beats: 64.0005% /63.9084% with new tempo/
# 3 beats: 65.8205% with new tempo
# 2 beats: 65.1892% / 64.8092% with new tempo / 65.1202 mean instead of median/ 2s, beat centered: 57.6266%, 53.7138% for 1 beat.
# 1 beats: Segmentation Fault
# absolute time
# 2 sec: 69.1604%
# 1 sec: 68.4633%
# 0.5 sec: 61.6278%
# 0.25 sec: 57.1777%
#
def calculateBeatsAndSemitones(infile):
    print 'Loading audio file...', infile
    proc = BeatTrackingProcessor(
        fps = 100,
        method='comb', min_bpm=40,
        max_bpm=240, act_smooth=0.09,
        hist_smooth=7, alpha=0.79)
    act = RNNBeatProcessor()(infile)
    beats = proc(act).astype('float32')

    audio = essentia.standard.MonoLoader(filename = infile)()
    #bt = BeatTrackerMultiFeature()
    #beats, _ = bt(audio)
    # TODO: best partameters.
    parameters = {}
    #stepsize, chroma = vamp.collect(
    #    audio, 44100, "nnls-chroma:nnls-chroma", output = "chroma", step_size=2048)["matrix"]
    stepsize, semitones = vamp.collect(
        audio, 44100, "nnls-chroma:nnls-chroma", output = "semitonespectrum", step_size=2048)["matrix"]
    return len(audio), beats, semitones

def chordPseudoProbabilities(hopSize, sampleRate, chroma, beats):
    majorPattern = np.array([1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0])
    minorPattern = np.array([1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0])
    allChords = np.zeros((24, 12))
    for i in xrange(12):
        p = i * 2
        allChords[p] = np.roll(majorPattern, i)
        allChords[p + 1] = np.roll(minorPattern, i)

    #syms = np.empty(len(beats - 1), dtype='object')
    probs = np.zeros((len(beats) - 1, 24))
    for i in xrange(len(beats) - 1):
        frameStart = int(float(sampleRate) * beats[i]/hopSize);
        currentChroma = chroma[frameStart]
        corrs = np.corrcoef(currentChroma, allChords)[0, 1:]
        corrs[corrs == np.nan] = 1
        e = np.exp(corrs)
        probs[i, :] = e / sum(e)
    return  probs

def viterbiStep(logProbs, logMatrix):
    newLogProbs = np.zeros(len(logProbs))
    bestIndices = np.zeros(len(logProbs), dtype='int')
    for i in xrange(len(logProbs)):
        pathLogProbs = logProbs + logMatrix[:, i]
        p = np.argmax(pathLogProbs)
        newLogProbs[i] = pathLogProbs[p]
        bestIndices[i] = p
    return newLogProbs, bestIndices

def viterbi(trellis, logMatrix):
    paths = np.zeros(trellis.shape, dtype='int')
    s = np.log(trellis[0,:])
    for i in xrange(1, trellis.shape[0]):
        s, prev = viterbiStep(s, logMatrix)
        paths[i, :] = prev
        s = s + np.log(trellis[i,:])
    best = np.empty(trellis.shape[0], dtype='int')
    p = np.argmax(s)
    for i in xrange(trellis.shape[0] - 1, -1, -1):
        best[i] = p
        p = paths[i, p]
    return best


def smoothProbabilities(p, degree):
    m = 1.0 / len(p)
    res = np.zeros(len(p), dtype='float')
    for i in xrange(len(p)):
        delta = m - p[i]
        if (delta > 0) :
            res[i] = p[i] + np.abs(delta) ** degree
        elif (delta < 0) :
            res[i] = p[i] - np.abs(delta) ** degree
        else :
            res[i] = p[i]
    return res/sum(res)

def chordBeats(infile, outfile) :
    # to essentia convention
    #chroma = np.roll(chroma, 3, 1)
    l, beats, semitones = essentia_chord_utils.loadBeatsAndChroma(infile)
    treblewindow = np.array([0.000350, 0.003144, 0.008717, 0.017037, 0.028058, 0.041719, 0.057942, 0.076638, 0.097701,
                      0.121014, 0.146447, 0.173856, 0.203090, 0.233984, 0.266366, 0.300054, 0.334860, 0.370590,
                      0.407044, 0.444018, 0.481304, 0.518696, 0.555982, 0.592956, 0.629410, 0.665140, 0.699946,
                      0.733634, 0.766016, 0.796910, 0.826144, 0.853553, 0.878986, 0.902299, 0.923362, 0.942058,
                      0.958281, 0.971942, 0.982963, 0.991283, 0.996856, 0.999650, 0.999650, 0.996856, 0.991283,
                      0.982963, 0.971942, 0.958281, 0.942058, 0.923362, 0.902299, 0.878986, 0.853553, 0.826144,
                      0.796910, 0.766016, 0.733634, 0.699946, 0.665140, 0.629410, 0.592956, 0.555982, 0.518696,
                      0.481304, 0.444018, 0.407044, 0.370590, 0.334860, 0.300054, 0.266366, 0.233984, 0.203090,
                      0.173856, 0.146447, 0.121014, 0.097701, 0.076638, 0.057942, 0.041719, 0.028058, 0.017037,
                      0.008717, 0.003144, 0.000350])
    basswindow = np.array([0.001769, 0.015848, 0.043608, 0.084265, 0.136670, 0.199341, 0.270509, 0.348162, 0.430105, 0.514023,
                    0.597545, 0.678311, 0.754038, 0.822586, 0.882019, 0.930656, 0.967124, 0.990393, 0.999803, 0.995091,
                    0.976388, 0.944223, 0.899505, 0.843498, 0.777785, 0.704222, 0.624888, 0.542025, 0.457975, 0.375112,
                    0.295778, 0.222215, 0.156502, 0.100495, 0.055777, 0.023612, 0.004909, 0.000000, 0.000000, 0.000000,
                    0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
                    0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
                    0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
                    0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
                    0.000000, 0.000000, 0.000000, 0.000000])
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

    chroma = np.zeros((semitones.shape[0], 12))
    for i in range(semitones.shape[0]):
        tones = semitones[i] * mywindow
        cc = chroma[i]
        for j in range(tones.size):
            cc[j % 12] = cc[j % 12] + tones[j]
    chroma = essentia_chord_utils.smooth(chroma, window_len= int(1.3 * 44100 / 2048), window='hanning').astype('float32')
    #chroma = preprocessing.normalize(chroma, norm='max')
    #beats = beats[::3]

    #chords = ChordsDetectionBeats(hopSize=2048)
    #syms, strengths = chords(chroma, beats)
    noteNames = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]
    chordNames = np.empty(24, dtype='object')
    for i in xrange(12):
        p = i * 2
        chordNames[p] = noteNames[i]
        chordNames[p + 1] = noteNames[i] + ":min"
    probs = chordPseudoProbabilities(2048, 44100, chroma, beats)
    #indices = np.argmax(probs, axis=1)
    #
    #transitionMatrix = np.ones((24, 24)) * 1.0/24
    #logMatrix = np.log(transitionMatrix)
    #penalty = np.ones((24, 24)) * 0.15
    #penalty[xrange(24), xrange(24)] = 0
    #logMatrix = logMatrix - penalty
    #
    # temperley
    pOthers = np.array([
        113, 113, 1384, 1384, 410, 410, 326, 326, 2266, 2266, 20, 20, 2220, 2220, 412, 412, 454, 454, 1386, 1386,
         162, 162], dtype='float')
    pOthers = pOthers / sum(pOthers)
    pSelftransition = 5.0/8.0
    pModeChange = 1.0/24.0
    pMaj = np.concatenate((np.array([pSelftransition, pModeChange]), pOthers * (1.0 - pSelftransition - pModeChange)))
    pMin = np.concatenate((np.array([pModeChange, pSelftransition]), pOthers * (1.0 - pSelftransition - pModeChange)))
    pMaj = smoothProbabilities(pMaj, 1.055)
    pMin = smoothProbabilities(pMin, 1.055)
    transitionMatrix = np.zeros((24, 24))
    for i in xrange(12):
        transitionMatrix[2 * i, :] = np.roll(pMaj, 2 * i)
        transitionMatrix[2 * i + 1, :] = np.roll(pMin, 2 * i)
    #
    #
    #transitionMatrix = np.ones((24, 24), dtype='float') * 1.0/24

    # simplest one.
    #p = 0.046
    #transitionMatrix = np.ones((24, 24)) * (1 - p) / 24
    #transitionMatrix[xrange(24), xrange(24)]=p

    logMatrix = np.log(transitionMatrix)
    indices = viterbi(probs, logMatrix)
    syms = map(lambda x: chordNames[x], indices)
    strengths = probs[xrange(len(indices)), indices]
    segments = essentia_chord_utils.toMirexLab(0.0, l / 44100.0, beats, syms, strengths)
    #chords = ChordsDetection(windowSize=0.2)
    #syms, strengths = chords(chroma)
    #endTime = l / 44100.0
    #stamps = np.arange(0, endTime, float(2048/44100.0))
    #segments = essentia_chord_utils.toMirexLab(0.0, endTime, stamps, syms, strengths)
    with open(outfile, 'w') as content_file:
        for s in segments:
            content_file.write(str(s) + '\n')

#chordBeats("npz/01_-_No_Reply.npz", "q.txt")
#quit()
try:
    infile = sys.argv[1]
    outfile = sys.argv[2]
except:
    print "usage:", sys.argv[0], "<input directory (with audio)> <output lab directory>"
    sys.exit()
essentia_chord_utils.processFiles(infile, outfile, chordBeats)

