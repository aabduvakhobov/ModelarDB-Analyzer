# Experiments for AGG (Aggregation)

This directory includes scripts for computing aggregates (i.e., downsampling) for the WTM dataset and evaluating the OLAP query results from computed aggregates.
## Prerequites
- Conda package manager

## Run
- Change to project root and create conda environment with [requirements.txt](https://github.com/aabduvakhobov/ModelarDB-Analyzer/blob/main/requirements.txt) file (if not already created): `conda create --name <my_env> --file requirements.txt`
- Activate the new conda environment: `conda activate <my_env>`
- Change to [AGG-experiments](Baselines/AGG-experiments) directory. 
- Run _main.py_ with: `python3 main.py`

## Experiment Outputs
`main.py` creates a new directory `aggregates` that stores all computed aggregates using the sampling intervals used in the paper and directory `OLAP_query_results` for storing the evaluation results of OLAP queries. Evaluation results for OLAP queries are given in two types: aggregated results (i.e., information similar to Table 4) and full version (i.e., query result for each signal, query type and sampling interval).

## Transfer Efficiency Experiment
Transfer efficiency experiment is performed using the PCD dataset. The small Java program [JavaDownsampler](Baselines/AGG-Experiments/JavaDownsampler) was created to perform the downsampling on the edge and `scp` was used to transfer the computed aggregates to the cloud node.
