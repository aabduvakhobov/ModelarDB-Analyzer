# IoTDB experiments
This directory contains bash script and python scripts for performing the experiments (data ingestion - Section 5.1, OLAP query processing - Section 5.3.2) with IoTDB using public WTM dataset. Also the code for the transfer efficiency experiment (Section 5.2) is [included](https://github.com/aabduvakhobov/ModelarDB-Analyzer/tree/main/Baselines/IoTDB-experiments/IoTB-Ingest-Transfer-Edge). Please note that the transfer efficiency experiment was performed using PCD dataset and thus its results cannot be reproduced.
## Prerequites
- IoTDB version v1.3.1
- conda package manager

## IoTDB Installation
- Check IoTDB v1.3.1 installation [instructions](https://iotdb.apache.org/UserGuide/V1.3.0-2/QuickStart/QuickStart_apache.html)

## Instructions to run

- Create conda virtual environment using [requirements.txt](https://github.com/aabduvakhobov/ModelarDB-Analyzer/blob/main/requirements.txt) file in the project root (if not already created)
- Set `IoTDB_HOME` environment variable in your path that points to IoTDB installation directory
- Run: `python3 run_ingest_olap_wtm.py`*

*This python script is configured to be run with the only open dataset WTM. However, the code that was used for the other datasets can also be checked from the bash and python scripts in the directory.  

## Experiment outputs
The results are stored in `outputs` directory and they contain information about ingestion logs including the size of the IoTDB database as well as OLAP query results for each given precision limit for IoTDB's lossy compression method TS_DIFF.