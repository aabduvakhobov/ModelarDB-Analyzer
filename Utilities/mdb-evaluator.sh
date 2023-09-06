#!/bin/bash

echo "here we are starting: activate conda env"
base_path=/srv/data1/abduvoris/engie_lite/engie_lite_downsampled
EVALUATION_TOOL_PATH=$HOME/ModelarDB-Home/ModelarDB-Evaluation-Tool
RESULTS_FOLDER=$HOME/opt/grafana/ModelarDB-dashboards/analyzer-datasets/engie/engie_lite_aggregates
MDB_HOME=$HOME/ModelarDB-Home/ModelarDB
DIM_FILE_PATH=$HOME/ModelarDB-Home/dimfiles/engie_dims/engie_lite.txt

sed -i -e "s~dimensions\s.\+~dimensions $DIM_FILE_PATH~g" $HOME/.modelardb.conf

for s in 3 5 15 30 300 
do
	for m in mean
	do
		let sampling_rate=$((s * 2000))
		echo "downsampling at $sampling_rate"
		#python3 $HOME/test-data-sgre/downsample.py $data_path $base_path/${s}x/mean/ $base_path/${s}x/last/ $s
		data_path=$base_path/${s}x/$m/*.orc
		# change modelardb.conf
		sed -i -e "s/interval\s[0-9]\+/interval $sampling_rate/g" $HOME/.modelardb.conf
		sed -i -e "s~source\s.\+~source $data_path~g" $HOME/.modelardb.conf
		# run evaluation tool
		python3 $EVALUATION_TOOL_PATH/main.py
		# rename and move the output database to the another place
		mv $EVALUATION_TOOL_PATH/output.db $RESULTS_FOLDER/engie_lite_${s}x_${m}.db

		echo "$data_path was evaluated"
 	done
done

