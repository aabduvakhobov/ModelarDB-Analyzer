# ModelarDB Analyzer for multi-model Error-Bounded Lossy and Lossless Compression (EBLLC)
Analyzer is a python program created for implementing and analyzing the performance of EBLLC on ModelarDB TSMS. We use ModelarDB's legacy [JVM implementation](https://github.com/modelardata/modelardb) for this purpose.

All experiments can be performed with public [WTM](https://github.com/cmcuza/EvalImpLSTS/tree/main/data/raw/Wind) dataset that can also be found in _data_ directory.


## Prerequites
- Java Development Kit (OpenJDK 11 and Oracle's Java SE Development Kit 11 have been tested)
- Scala Build Tool (sbt)
- Conda package manager

## Installation
- Clone [ModelarDB Analyzer](https://github.com/aabduvakhobov/ModelarDB-Analyzer.git) from the current directory
- Navigate to the project root with `cd ModelarDB-Analyzer` and clone [ModelarDB](https://github.com/modelardata/modelardb)



## Instructions to Run
### To evaluate ModelarDB's compression effectiveness and Mean Absolute Percentage Error (MAPE) from its lossy compression

Use **ModelarDB Analyzer** to evaluate ModelarDB's compression effectiveness and MAPE from its lossy compression:
- Change directory to Modelardb: `cd modelardb`
- Apply the [git patch file](https://github.com/aabduvakhobov/ModelarDB-Analyzer/blob/main/patches/ModelarDB-Extended-Logging.patch) in the [patches](https://github.com/aabduvakhobov/ModelarDB-Analyzer/tree/main/patches) directory with: `git apply ../patches/ModelarDB-Extended-Logging.patch`
- Set the configurations in the [config.cfg](https://github.com/aabduvakhobov/ModelarDB-Analyzer/blob/main/config.cfg)   
- Run [main.py](https://github.com/aabduvakhobov/ModelarDB-Analyzer/blob/main/main.py)


### To run OLAP queries in ModelarDB:
  1. Apply the [patch](https://github.com/aabduvakhobov/ModelarDB-Analyzer/blob/main/patches/ModelarDB-QueryProcessing.patch) for query processing.  
  2. Create ModelarDB-JVM's Fat Jar by running: `sbt assembly` in ModelarDB-JVM's root directory.
  3. Download Apache Spark version [3.2.1](https://spark.apache.org/releases/spark-release-3-2-1.html) and set `SPARK_HOME` environment variable
  4. Change to directory _Utilities/DB-Utilities/OLAP_query_processing_ path and run `run_queries.sh` bash script on the machine that you are running Spark master

### To run ModelarDB in the edge-to-cloud scenario: 
  1. Configure the same data source, dimensions file and error bounds in conf files for both instances of ModelarDB (edge and cloud)
  2. Make sure that cloud's conf file is on a server transfer mode\* like: *modelardb.transfer server*
  3. Make sure that edge's conf file has cloud's IP address for transfer: *modelardb.transfer xxx.xx.xx.xx*
  4. Start the cloud and the edge.

\* For transfer efficieny experiments, that require edge-to-cloud environment, make sure that hostname ip resolves to what is shown in ModelarDB's modelardb.conf file. Otherwise it needs to be changed from */etc/hosts*

## To run MAPE and OLAP query experiments for __AGG__ and __IoTDB__
Go to [Utilities](https://github.com/aabduvakhobov/ModelarDB-Analyzer/tree/main/Utilities) directory and change to respective directory. There you will find respective bash scripts for each solution and [README.md](https://github.com/aabduvakhobov/ModelarDB-Analyzer/tree/main/Utilities/README.md) on how to perform experiments.

## License
The code is licensed under version 2.0 of the Apache License and a copy of the license is bundled with the program.

The code uses some components from [ModelarDB](https://github.com/ModelarData/ModelarDB).