import sys
import numpy as np
from essentia.streaming import *
from essentia.standard import ChordsDetectionBeats
import essentia_chord_utils

def chords(infile, outfile) :
    """
      Algorithm* peaks = factory.create("SpectralPeaks",
                                    "maxPeaks", 10000,
                                    "magnitudeThreshold", 0.00001,
                                    "minFrequency", 40,
                                    "maxFrequency", 5000,
                                    "orderBy", "magnitude");
   Algorithm* skey = factory.create("Key",
                                   "numHarmonics", 4,
                                   "pcpSize", 36,
                                   "profileType", "temperley",
                                   "slope", 0.6,
                                   "usePolyphony", true,
                                   "useThreeChords", true);
  Algorithm* hpcp_chord = factory.create("HPCP",
                                         "size", 36,
                                         "referenceFrequency", tuningFreq,
                                         "harmonics", 8,
                                         "bandPreset", true,
                                         "minFrequency", 40.0,
                                         "maxFrequency", 5000.0,
                                         "bandSplitFrequency", 500.0,
                                         "weightType", "cosine",
                                         "nonLinear", true,
                                         "windowSize", 0.5);
    """
    # initialize algorithms we will use
    tuningFreq = essentia_chord_utils.tuning(infile)
    print "tg = ", tuningFreq
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
    chords = ChordsDetection()
    # use pool to store data
    pool = essentia.Pool()
    # connect algorithms together
    loader.audio >> framecutter.signal
    framecutter.frame >> windowing.frame >> spectrum.frame
    spectrum.spectrum >> spectralpeaks.spectrum
    spectralpeaks.magnitudes >> hpcp.magnitudes
    spectralpeaks.frequencies >> hpcp.frequencies
    hpcp.hpcp >> chords.pcp
    hpcp.hpcp >> (pool, 'chroma.hpcp')
    chords.chords >> (pool, 'tonal.key_chords')
    chords.strength >> (pool, 'tonal.key_strength')
    # network is ready, run it
    print 'Processing audio file...', infile
    essentia.run(loader)
    audio = essentia.standard.MonoLoader(filename = infile)()
    endTime = len(audio) / 44100.0
    stamps = np.arange(0, endTime, float(chordHopSize/44100.0))
    # workaround for Essentia behaviour I don't quite undestand
    syms = list(pool['tonal.key_chords'][:-1])
    strengths = list(pool['tonal.key_strength'][:-1])
    segments = essentia_chord_utils.toMirexLab(0.0, endTime, stamps, syms, strengths)
    with open(outfile, 'w') as content_file:
        for s in segments:
            content_file.write(str(s) + '\n')

try:
    infile = sys.argv[1]
    outfile = sys.argv[2]
except:
    print "usage:", sys.argv[0], "<input audio file> <output json file>"
    sys.exit()
essentia_chord_utils.processFiles(infile, outfile, chords)
