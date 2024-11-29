import pandas as pd
import pyarrow.orc as orc
import pyarrow.compute as pc
import numpy as np

import sys
import json


def get_files(path):
    import os
    ff = []
    for _, _, files in os.walk(path):
        for file in files:
            ff.append(file)
    return ff


def compute_aggregates_pyarrow(query, pyarrow_column):
    if query == 'MIN':
        return pc.min(pyarrow_column).as_py()
    elif query == "MAX":
        return pc.max(pyarrow_column).as_py()
    elif query == "AVG":
        return pc.mean(pyarrow_column).as_py()
    elif query == "COUNT":
        return pc.count(pyarrow_column).as_py()
    elif query == "SUM":
        return pc.sum(pyarrow_column).as_py()
    elif query == "MEDIAN":
        return float(pyarrow_column.to_pandas().median())
    elif query == "STD":
        return pc.stddev(pyarrow_column).as_py()


def compute_aggregates_pandas(query, pandas_dataframe):
    if "min_value" in query:
        return pandas_dataframe.min()
    elif "max_value" in query:
        return pandas_dataframe.max()
    elif "AVG" in query:
        return pandas_dataframe.mean()
    elif "COUNT" in query:
        return pandas_dataframe.count()
    elif "SUM" in query:
        return pandas_dataframe.sum()
    elif "stddev" in query:
        return pandas_dataframe.std()
    elif "median" in query:
        return pandas_dataframe.median()


def compute_olap_query_errors(queries, raw_data_table, agg_table, si, higher_than_zero):   
    results_dict = {}
    raw_data_table_filtered = raw_data_table.filter(pc.greater(raw_data_table[1],0))
    agg_table_filtered = agg_table.filter(pc.greater(agg_table[1],0))
    # read original dataset
    for query in queries:
        # For all MAX and MIN queries, we keep only more than zeros 
        if higher_than_zero or query.lower() in ['max', 'min']:    
            real_output = compute_aggregates_pyarrow(query, raw_data_table_filtered[1])
            aggregate_output = compute_aggregates_pyarrow(query, agg_table_filtered[1])
        else:
            real_output = compute_aggregates_pyarrow(query, raw_data_table[1])
            aggregate_output = compute_aggregates_pyarrow(query, agg_table[1])
        if query == "SUM" and aggregate_output is not None and ~np.isnan(aggregate_output):
            aggregate_output = aggregate_output * si
    
        if aggregate_output == real_output:
            query_error = 0
        elif real_output == 0 or real_output is None or aggregate_output is None or np.isnan(real_output) or np.isnan(aggregate_output):
            print("Printing only values: real: {} vs aggr: {}".format(real_output,  aggregate_output))
            query_error = None
        else:
            query_error = abs((real_output - aggregate_output)/real_output)
        results_dict[query] = query_error
    return results_dict


def compute_max_min_median_rqe(results_dict, queries, si):
    # iterate over all columns to find the max min and median
    aggregated_results_dict = {} 
    
    for s in si:
        if aggregated_results_dict.get(s) == None:
            aggregated_results_dict[s] = {}  
        for query in queries:
            max_rqe = float("-inf")
            min_rqe = float("inf")
            res = []
            if aggregated_results_dict[s].get(query) == None:
                aggregated_results_dict[s][query] = {}
            for file in results_dict.keys():
                q_res = results_dict[file][s][query]
                if q_res is not None and ~np.isnan(q_res):
                    res.append(q_res)
                    if q_res > max_rqe:
                        max_rqe = q_res
                        
                    if q_res < min_rqe:
                        min_rqe = q_res  
            aggregated_results_dict[s][query]["max"] = max_rqe
            aggregated_results_dict[s][query]["min"] = min_rqe
            aggregated_results_dict[s][query]["median"] = np.median(res)
    return aggregated_results_dict


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise Exception("Usage: script.py dataset_name higher_than_zero_bool")

    dataset = sys.argv[1]
    # only applicable for the following queries: STD, AVG, SUM and MEDIAN
    higher_than_zero = bool(sys.argv[2])
    
    QUERIES = ['MIN', 'MAX', 'AVG', 'SUM', 'MEDIAN', 'STD']
    if dataset == "PCD":
        # path to raw datasets
        original_path =  ''
        # path to aggregates
        aggregate_path = ''
        si = [7, 14, 33, 67, 400, 4000]
    elif dataset == "MTD":
        # path to raw dataset
        original_path = ''
        # path to aggregates
        aggregate_path = ''
        si = [3, 5, 15, 30, 300]

        
    # the names of the files in both the raw and aggregated data are the same
    files = get_files(original_path)
    results_dict = {}
    for file in files:
        results_dict[file] = {}
        
        raw_data_table = orc.read_table(original_path + "/" + file)
        for s in si:
            print(f"Computing for SI: {s}")
            # path to individual files including SI
            file_path = aggregate_path + '/' + f'{s}x/mean/' + file
            agg_table = orc.read_table(file_path) 
            results_dict[file][s] = compute_olap_query_errors(QUERIES, raw_data_table, agg_table, s, higher_than_zero)
    
    aggregated_results_per_si = compute_max_min_median_rqe(results_dict, QUERIES, si)
    # dump everything into json files
    with open(f"{dataset}-AGG-extended-rqe.json", "w") as outfile:
        json.dump(results_dict, outfile)
    with open(f"{dataset}-AGG-aggregated-rqe.json", "w") as f:
        json.dump(aggregated_results_per_si, f)
    