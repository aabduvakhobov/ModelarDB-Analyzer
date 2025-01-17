# ModelarDB Analyzer
This repository contains the code for the PVLDB paper: ["Scalable Model-Based Management of Massive High Frequency Wind Turbine Data with ModelarDB"](https://www.vldb.org/pvldb/vol17/p4723-abduvakhobov.pdf)

Abduvoris Abduvakhobov, Søren Kejser Jensen, Torben Bach Pedersen, and Christian Thomsen 

Modelar Analyzer is a Python program developed for analyzing the compression effectiveness and compressed data quality from ModelarDB TSMS's error-bounded lossy and lossless compression. We use [ModelarDB's JVM-based implementation](https://github.com/modelardata/modelardb) in our evaluation.

Experiments can be performed with the public [WTM](https://github.com/cmcuza/EvalImpLSTS/tree/main/data/raw/Wind) dataset that can also be found in [data/](https://github.com/aabduvakhobov/ModelarDB-Analyzer/tree/main/data) directory in different formats and structures (i.e., as univariate and multivariate time series).

## Paper

***Scalable Model-Based Management of Massive High Frequency Wind Turbine Data with ModelarDB***
by Abduvoris Abduvakhobov, Søren Kejser Jensen, Torben Bach Pedersen, and Christian Thomsen
in *The Proceedings of the VLDB Endowment, 17(13): 4723-4732, 2024*  
Links: [PVLDB](https://www.vldb.org/pvldb/vol17/p4723-abduvakhobov.pdf)

## Prerequites
- Java Development Kit for ModelarDB. The following were tested:
  -  OpenJDK 11 
  -  Oracle's Java SE Development Kit 11
- Scala Build Tool (sbt)
- Conda package manager

## Installation
1. Clone [ModelarDB Analyzer](https://github.com/aabduvakhobov/ModelarDB-Analyzer.git) from this repository
2. Create new virtual environment with conda using the [requirements.txt](https://github.com/aabduvakhobov/ModelarDB-Analyzer/blob/main/requirements.txt) file: `conda env create <my_env> --file requirements.txt`
3. Activate the new environment: `conda activate <my_env>`
4. In the project root, clone [ModelarDB 's JVM-based implementation](https://github.com/ModelarData/ModelarDB.git).
5. Change to ModelarDB and verify that the Head is at tag `v0.3.0`. Otherwise, checkout.

## Run
ModelarDB is configured using a configuration file (i.e., *modelardb.conf*). In our experiments, we only use few them, thus we created [config.cfg](https://github.com/aabduvakhobov/ModelarDB-Analyzer/blob/main/config.cfg) for centralized and simplified management of all configurations used in this paper. For more details on ModelarDB's configuration options, check the [instructions](https://github.com/ModelarData/ModelarDB/blob/main/docs/index.md#config) in ModelarDB repository and the comments in modelardb.conf file. Specifically we only configure the following parameters:
- `modelardb.engine` - processing engine. We use option *spark* (i.e., for Apache Spark) for evaluating OLAP queries, evaluation of compression factor and data quality. 
- `modelardb.source` - file-path or ip:port to the data source. In our case, those high frequency datasets: PCD, MTD and WTM*.
- `modelardb.dimensions` - path to schema file (dimensions file) for specifying a hierarchy for the ingested data. We include the dimensions [file for WTM](https://github.com/aabduvakhobov/ModelarDB-Analyzer/tree/main/data/ModelarDB_dimension_files). More on dimensions can be [here](https://github.com/ModelarData/ModelarDB/blob/main/docs/index.md#troubleshooting).
- `modelardb.error_bound` - pointwise error bound used for lossy compression with ModelarDB.
- `modelardb.sampling_interval` - sampling interval of the data source. ModelarDB's JVM-based implementation only assumes that the regular time series is provided for ingestion.
- `modelardb.interface` - we configure Apache Arrow Flight interface for the evaluation of OLAP queries with ModelarDB.

*Please note that only [WTM](https://github.com/aabduvakhobov/ModelarDB-Analyzer/tree/main/data) is a public dataset and can be used for reproducability. Thus, in this repository, we automatically configure all ModelarDB configuration options for WTM. The rest of the parameters are not changed.


### Evaluate Compression Effectiveness and Mean Absolute Percentage Error (MAPE)

Use ModelarDB Analyzer to evaluate ModelarDB's compression effectiveness and MAPE from its lossy compression:
1. Change to ModelarDB: `cd ModelarDB`
2. To add extended logging to ModelarDB, apply the [git patch file](https://github.com/aabduvakhobov/ModelarDB-Analyzer/blob/main/patches/ModelarDB-Extended-Logging.patch) in the [patches](https://github.com/aabduvakhobov/ModelarDB-Analyzer/tree/main/patches) directory with: `git apply ../patches/ModelarDB-Extended-Logging.patch`
3. Run [main.py](https://github.com/aabduvakhobov/ModelarDB-Analyzer/blob/main/main.py): `python3 main.py`

Please note that configurations in [config.cfg](https://github.com/aabduvakhobov/ModelarDB-Analyzer/blob/main/config.cfg) are tuned for WTM and thus you are not required to change them when testing with WTM.


### Evaluate OLAP Queries in ModelarDB:
  1. Run `git restore .` in ModelarDB directory
  2. Change to the project root: `cd ..`
  2. Run `python3 utils/conf_change_olap_querying.py`
  3. Run [loader_querying.sh](https://github.com/aabduvakhobov/ModelarDB-Analyzer/blob/main/loader_querying.sh) with two parameters: 1) path to ModelarDB; 2) error bound value for ingestion. Run the script using `./loader_querying.sh ModelarDB/ 0.0`. ModelarDB will start the ingestion of the WTM dataset and open the query interface using [Apache Arrow Flight](https://arrow.apache.org/blog/2019/10/13/introducing-arrow-flight/) at *localhost:9999*
  4. In a separate terminal window run: `python3 run_olap_queries.py`

### ModelarDB in the Edge-to-Cloud Scenario: 
The transfer efficiency experiments were only performed with the highest frequency, proprietary dataset PCD. In order to set up edge and cloud nodes, we used ModelarDB's [user manual](https://github.com/ModelarData/ModelarDB/blob/main/docs/index.md#user-manual) and configuration file [modelardb.conf](ModelarDB/modelardb.conf).

Other hints:

1. Make sure to configure the same dimensions file and error bound in *modelardb.conf* file of both ModelarDB instances (edge and cloud)
2. Make sure that the cloud instance's *modelardb.conf* enables server transfer mode* like: `modelardb.transfer server`
4. Make sure that the edge instance's *modelardb.conf* file has the cloud instance's IP address for transfer: `modelardb.transfer xxx.xx.xx.xx`
5. Start the cloud and the edge instance either with sbt or a compiled jar file in the edge and Spark job in the cloud. To check for more options, refer to [ModelarDB's user manual](https://github.com/ModelarData/ModelarDB/blob/main/docs/index.md#install).


\* For transfer efficieny experiments, that require edge-to-cloud environment, make sure that hostname ip resolves to what is shown in ModelarDB's *modelardb.conf* file. Otherwise it needs to be changed from */etc/hosts* at the cloud node.

## Run MAPE and OLAP Query Experiments for AGG and IoTDB
1. Change to [Baselines](https://github.com/aabduvakhobov/ModelarDB-Analyzer/tree/main/Baselines) directory
2. Choose the subdirectory for the chosen method (i.e., either [AGG-experiments](Baselines/AGG-experiments) or [IoTDB-experiments](Baselines/IoTDB-experiments)). There you will find respective bash scripts for each solution and detailed instructions for both [AGG](Baselines/AGG-experiments/README.md) and [IoTDB](Baselines/IoTDB-experiments/README.md). 

The default configurations for both methods use the available public dataset [WTM](https://github.com/aabduvakhobov/ModelarDB-Analyzer/tree/main/data).

## License
The code is licensed under version 2.0 of the Apache License and a copy of the license is bundled with the program.

The code uses components from [ModelarDB](https://github.com/ModelarData/ModelarDB) which is released under version 2.0 of the Apache License.