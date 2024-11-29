#!/bin/bash

# Configuration
ERROR=($2)

CORRS=(0.0)

#DB=cassandra
DB=file
#DB=h2
current_dir=$(pwd)
MODELARDB_PATH=$current_dir/$1
CONF_PATH=$MODELARDB_PATH/modelardb.conf

# also include OUTPUT_PATH
if [[ $DB == cassandra ]]
then
    MEMFRAC=0.50
else
    MEMFRAC=0.75
fi
MEMORY=$(python3 -c "from math import ceil; print(int(ceil($MEMFRAC * ($(awk '/MemTotal/ {print $2}' /proc/meminfo) / 1024 / 1024))))")G



# Main Function
mkdir $COPY_DB_PATH
cd $MODELARDB_PATH
# this is contentious line of code...
rm -r $COPY_DB_PATH/*
# Ingest the data set with the correlation specified in corrs
echo "Ingesting Dataset with: $e"
SBT_OPTS="-Xmx$MEMORY -Xms$MEMORY" sbt "run $CONF_PATH" 2> /dev/null #| tee $HOME/Downloads/output-"$e"-"$c"
#echo 'dk.aau.modelardb.Main.main(Array())' | ~/Programs/spark-3.1.1-bin-hadoop3.2/bin/spark-shell --driver-memory $MEMORY --executor-memory $MEMORY --packages com.datastax.spark:spark-cassandra-connector_2.12:3.0.1 --jars ModelarDB-assembly-1.0.0.jar | tee $HOME/Downloads/output-"$e"-"$c"
# cd to verifier and tee the result and cd back to modelardb home
