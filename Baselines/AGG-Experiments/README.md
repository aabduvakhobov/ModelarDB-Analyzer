# Experiments for AGG (Aggregation) method

This directory includes scripts for computing aggregates (i.e., downsampling) for the WTM dataset and evaluating the OLAP query results from computed aggregates.
## Prerequites
- Conda package manager
## Installation
- Go to project root and create conda environment with requirements.txt file: `conda create --name <env> --file requirements.txt`
## Instructions to run
- Change to AGG-Experiments directory: `cd Baselines/AGG-Experiments` 
- Run _main.py_ with: `python3 main.py`

## Output explanation
`main.py` creates a new directory `aggregates` that stores all computed aggregates using the sampling intervals used in the paper and directory `OLAP_query_results` for storing the evaluation results of OLAP queries. Evaluation results for OLAP queries are given in two types: aggregated results (i.e., information similar to Table 4) and full version (i.e., query result for each signal, query type and sampling interval).

## Transfer efficiency experiment
Transfer efficiency experiment is performed using the PCD dataset. The small Java program `JavaDownsampler` was created to perform the downsampling on the edge and `scp` was used to transfer the computed aggregates to the cloud node. The program can be found in the current directory.
