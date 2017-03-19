#!/bin/sh

echo "Evaluating chords with "improved" essentia's algorithm."

if [ $# -ne 2 ]; then
    echo "arguments required: <audio directory> <reference chord annotatins directory>"
    exit -1
fi

input_dir="$1"
output_dir="IMPROVED_output_$1"
echo "Output to $output_dir"
anno_dir="$2"
awk_line="{gsub(/^$output_dir\/|.lab$/,\"\")}; 1"

mkdir "$output_dir"

python my.py "$input_dir" "$output_dir"
ls -1 "$output_dir"/*.lab |awk "$awk_line" > essentia_list.txt
MusOOEvaluator --list essentia_list.txt --refdir "$anno_dir" --testdir "$output_dir" --refext .lab --testext .lab --chords MirexMajMin --output "$output_dir"/MirexMajMin.txt
MusOOEvaluator --list essentia_list.txt --refdir "$anno_dir" --testdir "$output_dir" --refext .lab --testext .lab --segmentation Inner --output "$output_dir"/segmentation.txt

echo "Output chords metrics: $output_dir/MirexMajMin.txt"
cat "$output_dir/MirexMajMin.txt"
echo "Output segmentation metrics: $output_dir/segmentation.txt"
cat "$output_dir/segmentation.txt"
