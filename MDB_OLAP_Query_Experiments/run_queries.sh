#!/bin/bash

MDB_DATA=/srv/data4/abduvoris/modelardb_legacy_data/ukwan
error=$1
filter_out_not_zero="True"

if [ -z $error ]
then
    echo "Usage: script.sh eb"
    exit 0
fi

MDB_HOME="/home/cs.aau.dk/zg03zi/ModelarDB-Home/ModelarDB-JVM"
CONF_FILE=$MDB_HOME/conf/server.conf
MDB_FAR_JAR=./Fat-ModelarDB-assembly-0.3.0.jar

echo "Processing with $error"
# change ebs
sed -i -e "s/error_bound\s[0-9\.?0-9]\+/error_bound $error/g" $CONF_FILE
# sed -i -e "s/ukwan\/modelardb-.*/ukwan\/modelardb-$error/g" $CONF_FILE
# change data path to read from
# python3 conf_change.py "$CONF_FILE" "storage=orc:$MDB_DATA/modelardb-$error"
# start spark master and worker

$SPARK_HOME/sbin/start-master.sh
master_url="$(hostname).srv.aau.dk:7077"
$SPARK_HOME/sbin/start-worker.sh -c 20 -m 50G spark://$master_url

spark-submit --total-executor-cores 15 --driver-memory 10g --executor-memory 30g \
--class dk.aau.modelardb.Main \
--master spark://a256-io1-01.srv.aau.dk:7077 $MDB_FAR_JAR $CONF_FILE

# python3 olap_modelardb.py "$error" "$MDB_DATA/modelardb-$error" "$filter_out_not_zero"













