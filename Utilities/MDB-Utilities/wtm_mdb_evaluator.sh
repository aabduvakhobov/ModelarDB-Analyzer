#!/bin/bash

echo "here we are starting: activate conda env"
dataset_path=/path/to/WTM
# also same as the ModelarDB path
analyzer_tool_path=/path/to/analyzer
analyzer_output_save_path=''
MDB_dimension_file=/path/to/dim_file

sed -i -e "s~dimensions\s.\+~dimensions $MDB_dimension_file~g" $HOME/.modelardb.conf

for s in 3 5 15 30 300 
do
	for m in mean
	do
		let sampling_rate=$((s * 2000))
		echo "downsampling at $sampling_rate"
		data_path=$dataset_path/${s}x/$m/*.orc
		# change to ModelarDB root
		cd $analyzer_tool_path
		# change modelardb.conf
		sed -i -e "s/interval\s[0-9]\+/interval $sampling_rate/g" $HOME/.modelardb.conf
		sed -i -e "s~source\s.\+~source $data_path~g" $HOME/.modelardb.conf
		# run evaluation tool
		python3 $analyzer_tool_path/main.py
		# rename and move the output database to the another place
		mv $analyzer_tool_path/output.db $analyzer_output_save_path/engie_lite_${s}x_${m}.db
		echo "$data_path was evaluated"
 	done
done

