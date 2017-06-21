# ACE2017

Repository with scripts to reproduce some results from my 2017 MIR course student blog: https://musicinformationretrieval.wordpress.com/category/audio-chord-detection/


To run most of the scripts you'll need:
   1. Linux-like or Mac OS X system with standard tools (shell, awk) and python 2.7.
   2. two directories which represents chord-annotated audio dataset:
      * <audio directory> with 'wav' audio files (perhaps other formats (e.g. .flac) will work as well)
      * <reference chord annotatins directory> MIREX-style 'lab' files with chord annotations.
        Every file in one directory should be matched to a file in another directory by name
        (e.g.: <audio directory>/chains.wav corresponds to <reference chord annotations directory>/chains.lab)
   3. https://github.com/jpauwels/MusOOEvaluator
     compiled, with its' executable path added to the PATH environment variable.
   4. Essentia (http://essentia.upf.edu/documentation/)
   5. numpy python package (http://www.numpy.org)
   6. vamp python package (https://pypi.python.org/pypi/vamp/1.0.0)

Additional dependencies are listed for each section.

## I. State of the Art Audio Chord Estimation algorithms evaluation
(https://musicinformationretrieval.wordpress.com/2017/03/06/state-of-the-art-audio-chord-estimation-algorithms-evaluation/)

Dependencies:
   1. madmom python package (https://github.com/CPJKU/madmom)
   4. Essentia (http://essentia.upf.edu/documentation/)
   5. Chordino vamp plugin (http://www.isophonics.net/nnls-chroma)

How to run:

   1. Chordino algorithm evaluation e.g.:
      ./run_chordino.sh audio chordannotations
   2. Madmom algorithm evaluation e.g.:
      ./run_madmom.sh audio chordannotations
   3. Essentia ChordsDetection algorithm evaluation e.g.:
      ./run_essentia.sh audio chordannotations
   4. Essentia ChordsDetectionBeats algorithm evaluation e.g.:
      ./run_essentia_beats.sh audio chordannotations

## II. Robustenss tests (https://musicinformationretrieval.wordpress.com/2017/03/21/robustness-tests-for-ace-algorithms/)

NOTE: scripts for this part have hardcoded file paths which must
be manually edited.

Dependencies:
   1. Lame library for MP3 compression test (http://lame.sourceforge.net)
   2. ffmpeg library for downsampling test (http://lame.sourceforge.net)
   3. MATLAB and AudioDegradationToolbox for vynil effect test (https://code.soundsoftware.ac.uk/projects/audio-degradation-toolbox)
   4. Audacity for pitch sift test (http://www.audacityteam.org)

How to run:

   1. For MP3 and downsampling edit pathes and run degrader.py
   2. For vynil effect run vynil.m from MATLAB
   3. For pitch shift use Audacity GUI
   4. For evaluation use run_on_degraded.sh, run_on_vynil.sh, run_on_shifted.sh.


## III. Chroma features evaluation (http://TODO)

Dependencies:
   1. for NNLS chroma: Chroma NNLS vamp plugin (http://www.isophonics.net/nnls-chroma)
   2. for librosa: librosa python package (https://github.com/librosa/librosa)
   3. for ChromaToolbox CLP and CRP features: MATLAB and Chroma Toolbox (http://resources.mpi-inf.mpg.de/MIR/chromatoolbox

How to run:
   1. run_essentia_beats.sh for HPCP chroma features
   2. run_nnls.sh for NNLS chroma
   3. for CLP and CRP:
      * run extract_muller_features.m  from MATLAB (manually edit hardcoded paths first).
      * ./run_clp.sh specifying obtained chroma directory and extension (either .clp or .crp).
   4. for librosa: modify run_essentia_beats.sh (uncomment librosa related sections).


## IV. Intermediate improvements  (http://TODO)

Dependencies:
   1. for NNLS chroma: Chroma NNLS vamp plugin (http://www.isophonics.net/nnls-chroma)
   2. madmom python package (https://github.com/CPJKU/madmom)
   3. Essentia with patched ChordsDetectionBeats algorithm (57284ab08b1bd93b24ef6b56dc7ccef5c6259d3c)
      should be used for second and third improvements.

Improvements:
   1. NNLS chroma plugged instead of HPCP: run_nnls.sh
   2. Chroma smoothed (by convolution with hanning window), sampled on every beat: run_essentia_beats_hacked.sh
   3. BeatTrackerMultiFeature replaced with madmom's DBN beats: run_essentia_dbn_beats.sh
   4. Template mapping pseudoprobabilities plugged into HMM: run_improved.sh

## V. Final Algorithm (http://TODO)

Dependencies:
   1. madmom python package (https://github.com/CPJKU/madmom)
   2. Chroma NNLS vamp plugin (http://www.isophonics.net/nnls-chroma)

How to run:
   1. Prepare directory with chroma and beat tracking data
      (in order to save time later on chord detection re-run with different parameter sets), e.g.:
      python prepare.py audio npz_dir
   2. Run the algorithm evaluation, e.g.:
      ./run_improved.sh npz_dir chordannotations
   3. find results in directory: IMPROVED_output_audio

## VI. Plots (some of the plots used in the blog are generated with scripts from 'plot' directory)

Dependencies:
   * matplotlib and seaborn python packages.
