from iotdb.Session import Session

import pandas as pd
import numpy as np
import pyarrow.orc as orc
import pyarrow.compute as pc

import csv
import time
import sys


# ENV Vars
PCD_UNIVARIATE_PATH = '/path/to/save/dataset'
IOTDB_SELECT_ALL_QUERIES = {"PCD": "SELECT {} FROM root.engie.powerlog", "MTD": ""}

# names of PCD dataset cols cannot be disclosed as per NDA
PCD_columns = ['']

def create_iotdb_session():
    ip = "127.0.0.1"
    port_ = "6667"
    username_ = "root"
    password_ = "root"
    # Apache IoT DB Database and TimeSeries creation
    session = Session(ip, port_, username_, password_)
    session.open(False)
    return session


def compute_error(y, yhat):
    # returns numpy array of errors
    np.seterr(all="print")
    x = np.abs((y - yhat)/y)
    # drop nan vals after division by zero
    x = x[~np.isnan(x)]
    # check if inf exists
    inf_index = np.argwhere( np.isinf(x) == True )
    x = x[~(x==np.inf)]
    return x, inf_index


def compute_mape(x):
    # mean must be performed after all errors are computed for all columns
    mape = np.mean(x)
    return mape


def compute_iotdb_mape(col, raw_dataset, iotdb_dataset ):

    # iterate over columns and read datasets
    start = time.perf_counter()
    real_error, inf_vals = compute_error( raw_dataset.iloc[:, 1].values, iotdb_dataset.iloc[:, 1].values )
    if len(inf_vals) > 0:
        print(f"Col {col} inf count: {len(inf_vals)}")
        print(inf_vals[:100])    
    print(f"Col: {col} finished in: {(time.perf_counter()-start):.4f}")
    return real_error, inf_vals


def compute_aggregates_pyarrow(query, pyarrow_column):
    if "min_value" in query:
        return pc.min(pyarrow_column)
    elif "max_value" in query:
        return pc.max(pyarrow_column)
    elif "AVG" in query:
        return pc.mean(pyarrow_column)
    elif "COUNT" in query:
        return pc.count(pyarrow_column)
    elif "SUM" in query:
        return pc.sum(pyarrow_column)


def compute_aggregates_pandas(query, pandas_dataframe):
    if "min" in query.lower():
        return pandas_dataframe.min()
    elif "max" in query.lower():
        return pandas_dataframe.max()
    elif "avg" in query.lower():
        return pandas_dataframe.mean()
    elif "count" in query.lower():
        return pandas_dataframe.count()
    elif "sum" in query.lower():
        return pandas_dataframe.sum()
    elif "std" in query.lower():
        return pandas_dataframe.std()
    elif "median" in query.lower():
        return pandas_dataframe.median()
    
    
def compute_query_errors(raw_dataset, iotdb_dataset, queries, higher_than_zero, exclude_queries=['max', 'min']):
    results_dict = {}
    for query in queries:
        if higher_than_zero or query.lower() in exclude_queries:
            raw_data_col = raw_dataset.columns[-1]
            real_output = compute_aggregates_pandas(query, raw_dataset.loc[raw_dataset[raw_data_col] > 0.0, raw_data_col])
            iotdb_col = iotdb_dataset.columns[-1]
            iotdb_output = compute_aggregates_pandas(query, iotdb_dataset.loc[iotdb_dataset[iotdb_col] > 0.0, iotdb_col])
        else:
            real_output = compute_aggregates_pandas(query, raw_dataset.iloc[:, 1])
            iotdb_output = compute_aggregates_pandas(query, iotdb_dataset.iloc[:, 1])
        if iotdb_output == real_output:
            query_error = 0
        elif real_output == 0 or real_output is None or iotdb_output is None or np.isnan(real_output) or np.isnan(iotdb_output):
            print("Printing only difference: {}".format(abs(real_output - iotdb_output)) )
            query_error = None
        else:
            query_error = abs((real_output - iotdb_output)/real_output)
        results_dict[query] = query_error
    return results_dict


def compute_max_min_median_rqe(results_dict, query):
    # iterate over all columns to find the max min and median
    max_rqe = float("-inf")
    min_rqe = float("inf")
    res = []
    nan_cnt = 0
    for col in results_dict.keys():
        response = results_dict[col][query]
        if response is not None and ~np.isnan(response):
            res.append(response)
            if response > max_rqe:
                max_rqe = response
            if response < min_rqe:
                min_rqe = response 
        else:
            nan_cnt += 1
    return min_rqe, max_rqe, np.median(res), nan_cnt 


if __name__ == "__main__":
    if len(sys.argv) < 7:
        raise Exception("Usage: script.py test_type dataset encoding precision higher_than_zero")
    
    test_type = sys.argv[1]
    dataset_name = sys.argv[2]
    encoding = sys.argv[3]
    precision = sys.argv[4]
    higher_than_zero = bool(sys.argv[5])
    exclude_queries = sys.argv[6:]
    
    QUERIES = ["MIN", "MAX", "AVG", "MEDIAN", "STD", "SUM"]
    if test_type == "mape":
        header = ["dataset_name", "encoding", "precision", "mape", "max_absolute_error", "inf_count",]
    elif test_type == "query_error":
        header = ["dataset_name", "encoding", "precision", "query", "rqe_min", "rqe_max", "rqe_median", 'nan_cnt']

    save_file = f"{test_type}-{dataset_name}-{encoding}-{precision}-metrics.csv"
    with open(save_file, "w") as f:
        writer = csv.writer(f)
        writer.writerow(header)    
    
    session = create_iotdb_session()    
    # start = time.perf_counter()
    results_dict = {}
    errors = np.array([])
    max_errors = []
    inf_cnts = 0
    for col in PCD_columns:
        raw_dataset = orc.read_table(PCD_UNIVARIATE_PATH + '/{}.orc'.format(col) ).to_pandas()
        measurement_name = col.replace(".orc", '')
        iotdb_dataset = session.execute_query_statement(IOTDB_SELECT_ALL_QUERIES[dataset_name].format(col)).todf()
        if test_type == "mape":
            real_errors, inf_cnt = compute_iotdb_mape(col, raw_dataset, iotdb_dataset )
            errors = np.concatenate( [errors, real_errors] )
            max_errors.append(np.max(real_errors))      
            inf_cnts += inf_cnt  
        elif test_type == 'query_error':
            results_dict[col] = compute_query_errors(raw_dataset, iotdb_dataset, QUERIES, higher_than_zero, exclude_queries)
            
    for query in QUERIES:
        rqe_min, rqe_max, rqe_median, nan_cnt = compute_max_min_median_rqe(results_dict, query)
        row = [dataset_name, encoding, precision, query, rqe_min, rqe_max, rqe_median, nan_cnt]
        # append metrics
        with open(save_file, "a") as f:
            writer = csv.writer(f)
            writer.writerow(row)
    if len(errors) > 0:
        mape = compute_mape(errors)
        max_errors = max(max_errors)
        row = [dataset_name, encoding, precision, mape, max_errors, inf_cnts]

    # wrute extended results if there is data in dict
    if len(results_dict.items()) > 0:
        pd.DataFrame(results_dict).to_csv(f"{dataset_name}_{encoding}_{precision}_extended_rqe.csv")
    