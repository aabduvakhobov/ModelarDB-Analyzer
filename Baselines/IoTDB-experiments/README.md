# Experiments for Apache IoTDB (IoTDB)
This directory contains bash script and python scripts for performing the experiments (data ingestion - Section 5.1, OLAP query processing - Section 5.3.2) with IoTDB using public WTM dataset. Also the code for the transfer efficiency experiment (Section 5.2) is [included](https://github.com/aabduvakhobov/ModelarDB-Analyzer/tree/main/Baselines/IoTDB-experiments/IoTB-Ingest-Transfer-Edge). Please note that the transfer efficiency experiment was performed using PCD dataset and thus its results cannot be reproduced.

## Prerequites
- IoTDB version v1.3.1
- Conda package manager

## IoTDB Installation
1. Install IoTDB v1.3.1. You can check installation [instructions](https://iotdb.apache.org/UserGuide/V1.3.0-2/QuickStart/QuickStart_apache.html)
2. If not already created, create conda environment using [requirements.txt](requirements.txt) in the project root
3. Install Apache IoTDB python library: `pip3 install apache-iotdb==1.3.3`

## Run

1. Create conda virtual environment using [requirements.txt](https://github.com/aabduvakhobov/ModelarDB-Analyzer/blob/main/requirements.txt) file in the project root (if not already created)
2. Set `IoTDB_HOME` environment variable in your path that points to IoTDB installation directory
3. Run: `python3 run_ingest_olap_wtm.py`*

*This python script is configured to be run with the only open dataset WTM. However, the code that was used for the other datasets can also be checked from the bash and python scripts in the directory. 

You can change configurations related to IoTDB experiment (i.e., precision limits for TS_DIFF) in [config.cfg](config.cfg) file.

## Experiment Outputs
The results are stored in `outputs` directory and they contain information about ingestion logs including the size of the IoTDB database as well as OLAP query results for each given precision limit for IoTDB's lossy compression method TS_DIFF.

## Transfer Efficiency Experiment
Transfer efficiency experiment is performed using the PCD dataset. The small Java program [IoTB-Ingest-Transfer-Edge](Baselines/IoTDB-experiments/IoTB-Ingest-Transfer-Edge) was created to  ingest data on the edge IoTDB instance and create a IoTDB Pipe to synchronize data with the IoTDB cloud instance. We run the edge instance on *localhost:6667* and the cloud instance on *localhost:6668*

