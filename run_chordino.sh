#!/bin/sh

if [ $# -ne 2 ]; then
    echo "arguments required: <audio directory> <reference chord annotatins directory>"
    exit -1
fi

input_dir="$1"
output_dir="Chordino_output_$1"
anno_dir="$2"
awk_line="{gsub(/^$output_dir\/|.lab$/,\"\")}; 1"

mkdir "$output_dir"
sonic-annotator -t chords.n3 -r "$input_dir" -w lab --lab-basedir "$output_dir" --lab-fill-ends
python remove_quotes.py "$output_dir"
ls -1 "$output_dir"/*.lab |awk "$awk_line" > chordino_list.txt
./MusOOEvaluator --list chordino_list.txt --refdir "$anno_dir" --testdir "$output_dir" --refext .lab --testext .lab --chords MirexMajMin --output "$output_dir"/MirexMajMin.txt
./MusOOEvaluator --list chordino_list.txt --refdir "$anno_dir" --testdir "$output_dir" --refext .lab --testext .lab --segmentation Inner --output "$output_dir"/segmentation.txt

echo "Output chords metrics: $output_dir/MirexMajMin.txt"
cat "$output_dir/MirexMajMin.txt"
echo "Output segmentation metrics: $output_dir/segmentation.txt"
cat "$output_dir/segmentation.txt"

