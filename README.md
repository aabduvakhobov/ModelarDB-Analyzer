# ModelarDB Analyzer for multi-model Error-Bounded Lossy and Lossless Compression (EBLLC)
This repository contains code for the research paper "Scalable Model-Based Management of Massive High Frequency
Wind Turbine Data with ModelarDB" by Abduvakhobov et al. submitted to PVLDB Volume 17. 

Modelar-Analyzer is a python program developed for analyzing the performance of EBLLC on ModelarDB TSMS. We use ModelarDB's [legacy implementation](https://github.com/modelardata/modelardb) in our evaluation.

Experiments can be performed with public [WTM](https://github.com/cmcuza/EvalImpLSTS/tree/main/data/raw/Wind) dataset that can also be found in [data](https://github.com/aabduvakhobov/ModelarDB-Analyzer/tree/main/data) directory in different formats and structures (i.e., as univariate and multivariate time series).


## Prerequites
- Java Development Kit for ModelarDB (OpenJDK 11 and Oracle's Java SE Development Kit 11 have been tested)
- Scala Build Tool (sbt)
- Conda package manager

## Installation
- Clone [ModelarDB Analyzer](https://github.com/aabduvakhobov/ModelarDB-Analyzer.git) from the current directory
- Navigate to the project root with `cd ModelarDB-Analyzer` and clone [ModelarDB](https://github.com/modelardata/modelardb)
- Create new virtual environment with conda using the [requirements.txt](https://github.com/aabduvakhobov/ModelarDB-Analyzer/blob/main/requirements.txt) file: `conda env create <my_env> --file requirements.txt`
- Activate the new environment: `conda activate <my_env>`


## Instructions to Run
### Evaluate ModelarDB's compression effectiveness and Mean Absolute Percentage Error (MAPE) from its lossy compression

Use **ModelarDB Analyzer** to evaluate ModelarDB's compression effectiveness and MAPE from its lossy compression:
- Change directory to Modelardb: `cd modelardb`
- Apply the [git patch file](https://github.com/aabduvakhobov/ModelarDB-Analyzer/blob/main/patches/ModelarDB-Extended-Logging.patch) in the [patches](https://github.com/aabduvakhobov/ModelarDB-Analyzer/tree/main/patches) directory with: `git apply ../patches/ModelarDB-Extended-Logging.patch`
- Set the configurations in the [config.cfg](https://github.com/aabduvakhobov/ModelarDB-Analyzer/blob/main/config.cfg)   
- Run [main.py](https://github.com/aabduvakhobov/ModelarDB-Analyzer/blob/main/main.py): `python3 main.py`


### Evaluate OLAP queries in ModelarDB:
  1. Change to the project root
  2. Run loader_querying.sh: `./loader_querying.sh`. This will ingest the WTM dataset and start ModelarDB with [Apche Arrow Flight](https://arrow.apache.org/blog/2019/10/13/introducing-arrow-flight/) query interface
  3. On a separate terminal window run: `python3 run_olap_queries.py`

### ModelarDB in the edge-to-cloud scenario: 
  Transfer efficiency experiments were only performed with the highest frequency, closed dataset PCD. We followed instructions specified in ModelarDB's [user manual]().

Other hints:

1. Make sure to configure the same dimensions file and error bound in *modelardb.conf* file of both ModelarDB instances (edge and cloud)
2. Make sure that cloud instance's *modelardb.conf* file is on a server transfer mode* like: `modelardb.transfer server`
4. Make sure that edge instance's *modelardb.conf* file has cloud's IP address for transfer: `modelardb.transfer xxx.xx.xx.xx`
5. The cloud and the edge instance either with sbt or a a java program in the edge and a spark job in the cloud.


\* For transfer efficieny experiments, that require edge-to-cloud environment, make sure that hostname ip resolves to what is shown in ModelarDB's `modelardb.conf` file. Otherwise it needs to be changed from */etc/hosts*

## Run MAPE and OLAP query experiments for __AGG__ and __IoTDB__
Change to [Baselines](https://github.com/aabduvakhobov/ModelarDB-Analyzer/tree/main/Baselines) directory and choose the required method. There you will find respective bash scripts for each solution and detailed instructions for both [AGG](https://github.com/aabduvakhobov/ModelarDB-Analyzer/blob/main/Baselines/AGG-Experiments/README.md) and [IoTDB](https://github.com/aabduvakhobov/ModelarDB-Analyzer/blob/main/Baselines/IoTDB-experiments/README.md). The default configurations always use the available public dataset [WTM](https://github.com/aabduvakhobov/ModelarDB-Analyzer/tree/main/data).

## License
The code is licensed under version 2.0 of the Apache License and a copy of the license is bundled with the program.

The code uses components from [ModelarDB](https://github.com/ModelarData/ModelarDB).