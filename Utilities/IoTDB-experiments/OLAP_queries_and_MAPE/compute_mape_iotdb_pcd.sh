#!/bin/bash

# Exit when any command fails
set -e

encodings="TS_2DIFF"
precision_values="1 2 3 4 5 6"

save_path='/path/to/save/results'

test_type="query_error" # options: mape or query_error
# Can be used with both PCD and WTM datasets
dataset_name="WTM"
higher_than_zero="False"
exclude_queries='None'


for encoding in $encodings
do
    for precision in $precision_values
    do
        # change config files
        sed -i -e "s/.*float_precision=.*/float_precision=$precision/" $IoTDB_HOME/conf/iotdb-common.properties
        sed -i -e "s/.*default_float_encoding=.*/default_float_encoding=$encoding/" $IoTDB_HOME/conf/iotdb-common.properties
        sed -i -e "s/.*default_double_encoding=.*/default_double_encoding=$encoding/" $IoTDB_HOME/conf/iotdb-common.properties

        save_dir=$save_path/$encoding-$precision
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
        # timing ingestion process
        start=$SECONDS
        python3 iotdb_mape_pcd.py "$test_type" "PCD" "$encoding" "$precision" "$higher_than_zero" "$exclude_queries" >> $encoding-$precision-MAPE.log
        duration=$((SECONDS-start))
        # write results of the python program logs to the common file
        echo "All processed in $duration seconds" >> $encoding-$precision-MAPE.log
        bash $IoTDB_HOME/sbin/stop-standalone.sh
        sleep 10
    done
done

