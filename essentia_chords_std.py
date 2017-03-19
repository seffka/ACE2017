import sys
from essentia.streaming import *
from essentia.standard import YamlOutput
from essentia.standard import BeatTrackerMultiFeature
from essentia.standard import ChordsDetectionBeats
import essentia_chord_utils

def chordBeats(infile, outfile) :
    # initialize algorithms we will use
    tuningFreq = essentia_chord_utils.tuning(infile)
    chordHopSize = 2048
    frameSize = 8192
    loader = MonoLoader(filename=infile)
    framecutter = FrameCutter(hopSize=chordHopSize, frameSize=frameSize)
    windowing = Windowing(type="blackmanharris62")
    spectrum = Spectrum()
    spectralpeaks = SpectralPeaks(orderBy="magnitude",
                                  magnitudeThreshold=1e-05,
                                  minFrequency=40,
                                  maxFrequency=5000,
                                  maxPeaks=10000)
    hpcp = HPCP(size=12,
                referenceFrequency = tuningFreq,
                harmonics = 8,
                bandPreset = True,
                minFrequency = 40.0,
                maxFrequency = 5000.0,
                bandSplitFrequency = 500.0,
                weightType = "cosine",
                nonLinear = True,
                windowSize = 1.0)
    # use pool to store data
    pool = essentia.Pool()
    # connect algorithms together
    loader.audio >> framecutter.signal
    framecutter.frame >> windowing.frame >> spectrum.frame
    spectrum.spectrum >> spectralpeaks.spectrum
    spectralpeaks.magnitudes >> hpcp.magnitudes
    spectralpeaks.frequencies >> hpcp.frequencies
    hpcp.hpcp >> (pool, 'chroma.hpcp')
    # network is ready, run it
    essentia.run(loader)
    # don't forget, we can actually instantiate and call an algorithm on the same line!
    print 'Loading audio file...', infile
    audio = essentia.standard.MonoLoader(filename = infile)()
    bt = BeatTrackerMultiFeature()
    beats, _ = bt(audio)
    beats = beats[::4]
    chords = ChordsDetectionBeats()
    syms, strengths = chords(pool['chroma.hpcp'], beats)
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

