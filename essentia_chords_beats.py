import sys
import os
from essentia.streaming import *
from essentia.standard import YamlOutput
from essentia.standard import BeatTrackerMultiFeature
from essentia.standard import ChordsDetectionBeats
import essentia_chord_utils
import librosa
import numpy as np

def chordBeats(infile, outfile) :
    #    chroma_cq = librosa.feature.chroma_cqt(y=y, sr=44100)

    chordHopSize = 4096
    frameSize = 8192
    tuningFreq = essentia_chord_utils.tuning(infile)
    # initialize algorithms we will use
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

    ## network is ready, run it
    #essentia.run(loader)
    ## don't forget, we can actually instantiate and call an algorithm on the same line!

    print 'Loading audio file...', infile
    audio = essentia.standard.MonoLoader(filename = infile)()
    bt = BeatTrackerMultiFeature()
    beats, _ = bt(audio)
    beats = beats[::4]

    #y, sr = librosa.load(infile, sr=44100)
    #chroma_stft = librosa.feature.chroma_stft(y=y, sr=44100, n_chroma = 12, n_fft = 8192, hop_length=2048)
    #chroma_stft = chroma_stft.transpose()
    #chroma_stft = chroma_stft.astype('float32')
    ## to essentia convention
    #chroma_stft = np.roll(chroma_stft, 3, 1)
    #
    #chords = ChordsDetectionBeats()
    #syms, strengths = chords(chroma_stft, beats)

    #y, sr = librosa.load(infile, sr=44100)
    #C = np.log(np.abs(librosa.cqt(y, sr=sr,
    #                              hop_length=2048,
    #                              fmin=None,
    #                              n_bins=12 * 7,
    #                              bins_per_octave=12,
    #                              tuning=None,
    #                              norm=None,
    #                              scale=False)) * 100 + 1)
    #chroma_cqt = librosa.feature.chroma_cqt(y, sr, norm=2, C=C)
    #chroma_cqt = librosa.feature.chroma_cqt(y, sr, hop_length=2048, norm=2, threshold=0.0)
    #chroma_cqt = chroma_cqt.transpose()
    #chroma_cqt = chroma_cqt.astype('float32')
    ## to essentia convention
    #chroma_cqt = np.roll(chroma_cqt, 3, 1)
    #
    #chords = ChordsDetectionBeats()
    #syms, strengths = chords(chroma_cqt, beats)

    chords = ChordsDetectionBeats()
    syms, strengths = chords(pool['chroma.hpcp'], beats)
    print 'size: ', len(pool['chroma.hpcp'])
    #name, ext = os.path.splitext(outfile)
    #YamlOutput(filename=name+'.chroma.json')(pool)
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

