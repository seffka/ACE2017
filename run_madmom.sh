#!/bin/sh

if [ $# -ne 2 ]; then
    echo "arguments required: <audio directory> <reference chord annotatins directory>"
    exit -1
fi

input_dir="$1"
output_dir="Madmom_output_$1"
anno_dir="$2"
awk_line="{gsub(/^$output_dir\/|.chords.txt$/,\"\")}; 1"

mkdir "$output_dir"
CNNChordRecognition batch -o "$output_dir" "$input_dir"/*
ls -1 "$output_dir"/*.txt |awk "$awk_line" > madmom_list.txt
./MusOOEvaluator --list madmom_list.txt --refdir "$anno_dir" --testdir "$output_dir" --refext .lab --testext .chords.txt --chords MirexMajMin --output "$output_dir"/MirexMajMin.txt
./MusOOEvaluator --list madmom_list.txt --refdir "$anno_dir" --testdir "$output_dir" --refext .lab --testext .chords.txt --segmentation Inner --output "$output_dir"/segmentation.txt

echo "Output chords metrics: $output_dir/MirexMajMin.txt"
cat "$output_dir/MirexMajMin.txt"
echo "Output segmentation metrics: $output_dir/segmentation.txt"
cat "$output_dir/segmentation.txt"
