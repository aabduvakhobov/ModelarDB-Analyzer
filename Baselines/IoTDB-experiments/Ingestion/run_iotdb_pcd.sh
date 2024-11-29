#!/bin/bash

# Exit when any command fails
set -e

encodings="RLE TS_2DIFF"
precision_values="1 2 3 4 5 6 7"
data_path=$1
save_path='/srv/data3/abduvoris/iotdb_data'
# time to sleep for vacuum
sleep_for_vacuum=120

if [ -z $data_path ]
then
    echo "Usage: script.sh /path/to/file.orc"
    exit 0
fi

for encoding in $encodings
do
    for precision in $precision_values
    do
        # change config files
        sed -i -e "s/.*float_precision=.*/float_precision=$precision/" $IoTDB_HOME/conf/iotdb-common.properties
        sed -i -e "s/.*default_float_encoding=.*/default_float_encoding=$encoding/" $IoTDB_HOME/conf/iotdb-common.properties
        sed -i -e "s/.*default_double_encoding=.*/default_double_encoding=$encoding/" $IoTDB_HOME/conf/iotdb-common.properties

        bash $IoTDB_HOME/sbin/start-standalone.sh
        sleep 5
        # timing ingestion process
        start=$SECONDS
        python3 ingest_pcd_sgre.py $data_path
        # sleep for a minute or two to finish vacuuming
        duration=$((SECONDS-start))
        # write results of the python program logs to the common file
        cat app.log >> $encoding-$precision.log
        rm app.log
        sleep $sleep_for_vacuum
        du -h -d0 $IoTDB_HOME/data/datanode/data >> $encoding-$precision.log
        echo "Processed in $duration seconds" >> $encoding-$precision.log
        bash $IoTDB_HOME/sbin/stop-standalone.sh
        sleep 5
        # clean everything after ingestion
        # rm -r $IoTDB_HOME/logs $IoTDB_HOME/data $IoTDB_HOME/ext
        # instead of clean move dataset to save_path
        save_dir=$save_path/$encoding-$precision
        if [ -d $save_dir ]
        then
            echo "$save_dir already exists so we only write"
        else
            mkdir $save_dir
        fi
        mv $IoTDB_HOME/logs $IoTDB_HOME/data $IoTDB_HOME/ext $save_dir
        echo "database moved to: $save_dir"
    done
done

