# ModelarDB Analyzer for multi-model Error-Bounded Lossy and Lossless Compression (EBLLC)
Analyzer is a python program created for implementing and analyzing the performance of EBLLC on ModelarDB TSMS. We use [ModelarDB-JVM](https://github.com/modelardata/modelardb) for this purpose.

To run **ModelarDB Analyzer** for ingestion and subsequent MAPE computation task:
  1. Clone [ModelarDB-JVM](https://github.com/modelardata/modelardb) repository and apply the [git patch file](https://github.com/aabduvakhobov/ModelarDB-Analyzer/blob/main/patches/ModelarDB-Extended-Logging.patch) in the [patches](https://github.com/aabduvakhobov/ModelarDB-Analyzer/tree/main/patches) directory.
  2. Set the configurations in the [config.cfg](https://github.com/aabduvakhobov/ModelarDB-Analyzer/blob/main/config.cfg)   
  3. Run [main.py](https://github.com/aabduvakhobov/ModelarDB-Analyzer/blob/main/main.py)

\* Make sure that hostname ip resolves to what is shown in the conf file. Otherwise it needs to be changed from */etc/hosts* 

To run OLAP queries in ModelarDB:
  1. Apply the [patch](https://github.com/aabduvakhobov/ModelarDB-Analyzer/blob/main/patches/ModelarDB-QueryProcessing.patch) for query processing.  
  2. Create ModelarDB's Fat Jar by running: `sbt assembly` in ModelarDB's root directory.
  3. Download Apache Spark version __3.2.1__ and set `SPARK_HOME` environement variable
  4. Change to directory _Utilities/DB-Utilities/OLAP_query_processing_ path and run `run_queries.sh` bash script on the machine that you are running Spark master

To run ModelarDB in the edge-to-cloud scenario: 
  1. Configure the same data source, dimensions file and error bounds in conf files for both instances of ModelarDB (edge and cloud)
  2. Make sure that cloud's conf file is on a server transfer mode\* like: *modelardb.transfer server*
  3. Make sure that edge's conf file has cloud's IP address for transfer: *modelardb.transfer xxx.xx.xx.xx*
  4. Start the cloud and the edge.

To run MAPE and OLAP query experiments for __AGG__ and __IoTDB__, go to [Utilities](https://github.com/aabduvakhobov/ModelarDB-Analyzer/tree/main/Utilities) directory and change to respective directory. There you will find respective shell scripts for each solution.