#!/bin/sh

./run_essentia.sh down22050 chords_annotation
./run_essentia.sh down11025 chords_annotation
./run_essentia.sh down5512 chords_annotation
./run_essentia.sh b32 chords_annotation
./run_essentia.sh b320 chords_annotation

./run_chordino.sh down22050 chords_annotation
./run_chordino.sh down11025 chords_annotation
./run_chordino.sh down5512 chords_annotation
./run_chordino.sh b32 chords_annotation
./run_chordino.sh b320 chords_annotation

./run_madmom.sh down22050 chords_annotation
./run_madmom.sh down11025 chords_annotation
./run_madmom.sh down5512 chords_annotation
./run_madmom.sh b32 chords_annotation
./run_madmom.sh b320 chords_annotation

