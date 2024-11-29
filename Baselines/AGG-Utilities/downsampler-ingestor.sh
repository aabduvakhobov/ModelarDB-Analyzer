#!/bin/bash

# a string list of number of data points to aggregate into 1
WINDOWS=($1)

# path to save newly created files
base_path=$2
mkdir $base_path
# path to original dataset
data_path=$3
# path to python script
downsampler_py=$4
echo "saving in: $base_path"
for s in "${WINDOWS[@]}"
do 
	echo "downsampling $s"
	mkdir $base_path/${s}x
	#mkdir $base_path/${s}x/last
	mkdir $base_path/${s}x/mean
	python3 $downsampler_py $data_path $base_path/${s}x/mean/ $s
	echo "$s was downsampled" 
 
done

