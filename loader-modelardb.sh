#!/bin/bash

# Configuration
ERROR=($2)

CORRS=(0.0)

#DB=cassandra
DB=parquet
#DB=h2

CONF_PATH=$3

DB_PATH=$HOME/ModelarDB-Home/tempDBs

COPY_DB_PATH=$DB_PATH/Ingested

MODELARDB_PATH=$1

# also include OUTPUT_PATH
if [[ $DB == cassandra ]]
then
    MEMFRAC=0.50
else
    MEMFRAC=0.75
fi
MEMORY=$(python3 -c "from math import ceil; print(int(ceil($MEMFRAC * ($(awk '/MemTotal/ {print $2}' /proc/meminfo) / 1024 / 1024))))")G

# Helper Functions
function reset-database {
    echo "Resetting Database"
    case "$DB" in
	"cassandra")
	    # Reset the running instance of Cassandra
	    ps -ax | grep org.apache.cassandra.service.CassandraDaemon | grep -v grep | xargs | cut -d " " -f 1 | xargs kill
	    rm -rf $HOME/Downloads/apache-cassandra-4.0-beta4/data
	    $HOME/Downloads/apache-cassandra-4.0-beta4/bin/cassandra > $HOME/Downloads/cassandra-log && sleep 360
	    ;;
	"h2")
	    # Delete the existing data stored in H2
	    rm -rf $DB_PATH/modelardb.h2.mv.db
	    rm -rf MODELARDB_PATH/modelardb.h2.mv.db
	    ;;
	"parquet")
	    # Delete existing database stored in parquet
	    rm -rf $DB_PATH/modelardb
	    rm -rf $MODELARDB_PATH/modelardb
	    ;;
	*)
	    echo "ERROR: unknown database"
	    exit 0
	    ;;
    esac
}

function restart-database {
    echo "Restarting Database"
    case "$DB" in
	"cassandra")
	    # Restart the running instance of Cassandra
	    ps -ax | grep org.apache.cassandra.service.CassandraDaemon | grep -v grep | xargs | cut -d " " -f 1 | xargs kill
	    $HOME/Downloads/apache-cassandra-4.0-beta4/bin/cassandra > /dev/null && sleep 60
	    ;;
	*)
	    # Only Cassandra needs to be restarted to properly let the data settle
	    ;;
    esac
}

function measure-database {
    echo "Measuring Data Size"
    case "$DB" in
	"cassandra")
	    # Flush the ingested data to disk, restarts Cassandra and reads the size of the ingested data
	    echo "Flushing, Compacting and Restarting Cassandra"
	    $HOME/Downloads/apache-cassandra-4.0-beta4/bin/nodetool flush
	    $HOME/Downloads/apache-cassandra-4.0-beta4/bin/nodetool compact
	    ps -ax | grep org.apache.cassandra.service.CassandraDaemon | grep -v grep | xargs | cut -d " " -f 1 | xargs kill
	    sleep 60
	    $HOME/Downloads/apache-cassandra-4.0-beta4/bin/cassandra > /dev/null
	    sleep 180
	    ps -ax | grep org.apache.cassandra.service.CassandraDaemon | grep -v grep | xargs | cut -d " " -f 1 | xargs kill
	    sleep 60

	    echo >> $HOME/Downloads/output-"$1"-"$2"
	    du -d1 $HOME/Downloads/apache-cassandra-4.0-beta4/data >> $HOME/Downloads/output-"$1"-"$2"
	    echo >> $HOME/Downloads/output-"$1"-"$2"
	    du -d1 -h $HOME/Downloads/apache-cassandra-4.0-beta4/data >> $HOME/Downloads/output-"$1"-"$2"
	    echo >> $HOME/Downloads/output-"$1"-"$2"
	    du -d1 $HOME/Downloads/apache-cassandra-4.0-beta4/data/data >> $HOME/Downloads/output-"$1"-"$2"
	    echo >> $HOME/Downloads/output-"$1"-"$2"
	    du -d1 -h $HOME/Downloads/apache-cassandra-4.0-beta4/data/data >> $HOME/Downloads/output-"$1"-"$2"
	    ;;
	"h2")
	    echo >> $HOME/Downloads/output-"$1"-"$2"
	    du $MODELARDB_PATH/modelardb.h2.mv.db >> $HOME/Downloads/output-"$1"-"$2"
	    echo >> $HOME/Downloads/output-"$1"-"$2"
	    final_size=$(du $MODELARDB_PATH/modelardb.h2.mv.db)
	    echo "final_size=$final_size" >> $HOME/Downloads/output-"$1"-"$2"
	    ;;
	"parquet")
      echo >> $HOME/Downloads/output-"$1"-"$2"
      du --max-depth=0 $MODELARDB_PATH/modelardb >> $HOME/Downloads/output-"$1"-"$2"
      echo >> $HOME/Downloads/output-"$1"-"$2"
      final_size=$(du --max-depth=0 $MODELARDB_PATH/modelardb)
      echo "final_size=$final_size" >> $HOME/Downloads/output-"$1"-"$2"
	    ;;  
	*)
	    echo "ERROR: unknown database"
	    exit 0
	    ;;
    esac
}

function copy-database {
    echo "Copying Database"
    case "$DB" in
	"cassandra")
	    ps -ax | grep org.apache.cassandra.service.CassandraDaemon | grep -v grep | xargs | cut -d " " -f 1 | xargs kill
	    cp -r $HOME/Downloads/apache-cassandra-4.0-beta4 $HOME/Data/Ingested/apache-cassandra-4.0-beta4-"$1"-"$2"
	    ;;
	"h2")
	    mv $MODELARDB_PATH/modelardb.h2.mv.db $COPY_DB_PATH/modelardb.h2.mv.db-"$1"-"$2"
	    ;;
    "parquet")
	    mv $MODELARDB_PATH/modelardb $COPY_DB_PATH/modelardb-"$1"-"$2"
	    ;;
	*)
	    echo "ERROR: unknown database"
	    exit 0
	    ;;
    esac
    mv $HOME/Downloads/output-"$1"-"$2" $COPY_DB_PATH/
}

# Main Function
mkdir "$COPY_DB_PATH"
cd $1
for c in "${CORRS[@]}"
do
    for e in ${ERROR[@]}
    do
      # Reset the database
      reset-database

      # Prepare a new copy of the configuration
      #cp $HOME/Programs/modelardb-azure.conf $HOME/Programs/modelardb.conf

      # Set the user defined correlation and error bound
      sed -i -e "s/error_bound\s[0-9]\+/error_bound $e/g" $CONF_PATH/.modelardb.conf
      sed -i -e "s/(correlation)/$c/g" $CONF_PATH/.modelardb.conf

      # Ingest the data set with the correlation specified in corrs
      echo "Ingesting Dataset with: $c"
      SBT_OPTS="-Xmx$MEMORY -Xms$MEMORY" sbt run | tee $HOME/Downloads/output-"$e"-"$c"
      #echo 'dk.aau.modelardb.Main.main(Array())' | ~/Programs/spark-3.1.1-bin-hadoop3.2/bin/spark-shell --driver-memory $MEMORY --executor-memory $MEMORY --packages com.datastax.spark:spark-cassandra-connector_2.12:3.0.1 --jars ModelarDB-assembly-1.0.0.jar | tee $HOME/Downloads/output-"$e"-"$c"

      # Measure the amount of data stored in the database
      measure-database "$e" "$c"

      # Copy the database so the ingested data can be used
      copy-database "$e" "$c"
    done
done
