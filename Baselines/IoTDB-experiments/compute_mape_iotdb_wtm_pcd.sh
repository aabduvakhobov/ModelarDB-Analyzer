#!/bin/bash

# Exit when any command fails
set -e

encodings=$1
precision_values=$2
iotdb_database=$3
output_dir=$4

test_type="query_error" # options: mape or query_error
# These parameters are hardcoded since we cannot share other datasets
dataset_name="WTM"
higher_than_zero="1"
exclude_queries='None'


for encoding in $encodings
do
    for precision in $precision_values
    do
        # change config files
        sed -i -e "s/.*float_precision=.*/float_precision=$precision/" $IoTDB_HOME/conf/iotdb-common.properties
        sed -i -e "s/.*default_float_encoding=.*/default_float_encoding=$encoding/" $IoTDB_HOME/conf/iotdb-common.properties
        sed -i -e "s/.*default_double_encoding=.*/default_double_encoding=$encoding/" $IoTDB_HOME/conf/iotdb-common.properties

        save_dir=$iotdb_database/$encoding-$precision
        # remove datasets
        if [ -d $IoTDB_HOME/data ]
        then
            rm -r $IoTDB_HOME/logs $IoTDB_HOME/data $IoTDB_HOME/ext
        fi
        # copy and paste datasets
        cp -r $save_dir/logs $save_dir/data $save_dir/ext $IoTDB_HOME
        # 
        bash $IoTDB_HOME/sbin/start-standalone.sh
        sleep 5
        # timing query processing
        start=$SECONDS
        python3 iotdb_mape_wtm_pcd.py "$test_type" $dataset_name "$encoding" "$precision" "$higher_than_zero" "$exclude_queries" >> $output_dir/$encoding-$precision-MAPE.log
        duration=$((SECONDS-start))
        # write results of the python program logs to the common file
        echo "All processed in $duration seconds" >> $output_dir/$encoding-$precision-MAPE.log
        bash $IoTDB_HOME/sbin/stop-standalone.sh
        sleep 10
    done
done

