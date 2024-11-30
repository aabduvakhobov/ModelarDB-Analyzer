#!/bin/bash

# Configuration
ERROR=$2

#DB=cassandra
DB=file
#DB=h2
current_dir=$(pwd)
MODELARDB_PATH=$current_dir/$1
CONF_PATH=$MODELARDB_PATH/modelardb.conf

if [ -z $1  ] || [ -z $ERROR ]
then
    echo "Usage: script.sh /path/to/ModelarDB error_bound"
    exit 0
fi

# also include OUTPUT_PATH
if [[ $DB == cassandra ]]
then
    MEMFRAC=0.50
else
    MEMFRAC=0.75
fi
MEMORY=$(python3 -c "from math import ceil; print(int(ceil($MEMFRAC * ($(awk '/MemTotal/ {print $2}' /proc/meminfo) / 1024 / 1024))))")G

# Main part
cd $MODELARDB_PATH
# Ingest the data set with the correlation specified in corrs
echo "Ingesting Dataset with: $ERROR"
sed -i -e "s/error_bound\s[0-9\.?0-9]\+/error_bound $ERROR/g" $CONF_PATH
# start ModelarDB with query interface
SBT_OPTS="-Xmx$MEMORY -Xms$MEMORY" sbt "run $CONF_PATH" 2> /dev/null #| tee $HOME/Downloads/output-"$e"-"$c"
