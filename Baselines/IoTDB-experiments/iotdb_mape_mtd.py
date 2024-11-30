from iotdb.Session import Session

import numpy as np
import pyarrow.orc as orc
import pyarrow.compute as pc

import csv
import sys
import json


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


def get_files(path):
    import os
    ff = []
    for _, _, files in os.walk(path):
        for file in files:
            ff.append(file)
    return ff


def get_device_groups(files):
    device_group = {}
    devices = set([file.split("_")[0] for file in files])
    for device in devices:
        device_group[device] = [d for d in files if device in d]
    # returns a dict: "BEBUE1" : [BEBUE1.activepower.orc, BEBUE1.wind_speed.orc ... ]
    return device_group
    

def correct_measurement_name(measurement_name, device):
    return measurement_name.replace(device + "_", "").replace(".orc", "").replace(".", "")


def compute_mape(x):
    # mean must be performed after all errors are computed for all columns
    mape = np.mean(x)
    return mape


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

    
def compute_iotdb_mape_OLAP_queries(device_group, base_path, not_zero=False):
    if not_zero:
        query_template = "SELECT {} FROM root.engie.{} where {} <> 0"
    else:
        query_template = "SELECT {} FROM root.engie.{}"
        
    queries = ["min_value({})", "max_value({})", "AVG({})", "COUNT({})", "SUM({})"]
    # computes mape for each device group and file of a device group separately
    session = create_iotdb_session()
    errors = np.array([])
    max_errors = []
    inf_cnts = 0
    # to store query results
    results_dict = {}
    # for MTD, iterate over files and read each file
    
    for device, device_files in device_group.items():
        results_dict[device] = {}
        for device_file in device_files:
            # execute query with a corrected measurement name to retrieve from the IoTDB
            measurement_name = correct_measurement_name(device_file, device)
            if not_zero:
                result_df = session.execute_query_statement(( query_template.format(measurement_name, device, measurement_name)  )).todf()
            else:
                result_df = session.execute_query_statement(( query_template.format(measurement_name, device)  )).todf()
            # read original dataset file
            original_data = orc.read_table(base_path + '/{}'.format(device_file) )
            original_data = original_data.to_pandas()
            if not_zero:
                original_data = original_data.loc[original_data['value']!=0]
            real_error, inf_vals = compute_error( original_data.iloc[:, 1].values, result_df.iloc[:, 1].values )
            # real_error, inf_vals = [0], [0] # temp solution for computing query for non-equal arrays
            if len(inf_vals) > 0:
                print(f"Col {device_file} inf count: {len(inf_vals)}")
                print(inf_vals[:100])
            inf_cnts += len(inf_vals)
            errors = np.concatenate( [errors, real_error] )
            max_errors.append(np.max(real_error))
            # create nested dict for measurement_name to store results of each query
            results_dict[device][measurement_name] = {}
            for query in queries:
                if not_zero:
                    query_statement = query_template.format(query.format(measurement_name), device, measurement_name)
                else:
                    query_statement = query_template.format(query.format(measurement_name), device)
                iotdb_res = session.execute_query_statement(query_statement).todf()
                iotdb_res = iotdb_res.iloc[0,0]
                # now we iterate over each query and compute the diff between original value and IoTDB response
                real_output = compute_aggregates_pandas(query, original_data.iloc[:, 1])
                if iotdb_res == real_output:
                    query_error = 0
                elif real_output == 0:
                    print("These real output: {} vs {} will generate nan, so printing only difference: {}".format(real_output, iotdb_res, abs(real_output - iotdb_res)) )
                    query_error = None
                else:
                    query_error = abs((real_output - iotdb_res)/real_output)

                results_dict[device][measurement_name][query.split("(")[0]] = query_error 
    
    mape = compute_mape(errors)
    max_errors = max(max_errors)
    session.close()
    return mape, max_errors, inf_cnts, results_dict



def compute_iotdb_min_max_sum(device_group, base_path, higher_than_zero=False):
    if higher_than_zero:
        query_template = "SELECT {} FROM root.engie.{} where {} > 0"
    else:
        query_template = "SELECT {} FROM root.engie.{}"
        
    queries = ["min_value({})", "max_value({})", "AVG({})", "COUNT({})", "SUM({})"]
    session = create_iotdb_session()
    # to store query results
    results_dict = {}
    # for MTD, iterate over files and read each file
    for device, device_files in device_group.items():
        results_dict[device] = {}
        for device_file in device_files:
            # execute query with a corrected measurement name to retrieve from the IoTDB
            measurement_name = correct_measurement_name(device_file, device)
            # read original dataset file
            original_data = orc.read_table(base_path + '/{}'.format(device_file) )
            original_data = original_data.to_pandas()
            if higher_than_zero:
                original_data = original_data.loc[original_data['value'] > 0.0]
            # real_error, inf_vals = compute_error( original_data.iloc[:, 1].values, result_df.iloc[:, 1].values )
            # create nested dict for measurement_name to store results of each query
            results_dict[device][measurement_name] = {}
            for query in queries:
                if higher_than_zero:
                    query_statement = query_template.format(query.format(measurement_name), device, measurement_name)
                else:
                    query_statement = query_template.format(query.format(measurement_name), device)
                iotdb_res = session.execute_query_statement(query_statement).todf()
                iotdb_res = iotdb_res.iloc[0,0]
                # now we iterate over each query and compute the diff between original value and IoTDB response
                real_output = compute_aggregates_pandas(query, original_data.iloc[:, 1])
                if iotdb_res == real_output:
                    query_error = 0
                elif real_output == 0:
                    print("These real output: {} vs {} will generate nan, so printing only difference: {}".format(real_output, iotdb_res, abs(real_output - iotdb_res)) )
                    query_error = None
                else:
                    query_error = abs((real_output - iotdb_res)/real_output)
                results_dict[device][measurement_name][query.split("(")[0]] = query_error 
    session.close()
    return results_dict


def compute_iotdb_max_median_std(device_group, base_path, queries, higher_than_zero=False, exlude_queries = ["max", 'min']):
    query_template = "SELECT {} FROM root.engie.{}"
        
    session = create_iotdb_session()
    # to store query results
    results_dict = {}
    # for MTD, iterate over files and read each file
    for device, device_files in device_group.items():
        results_dict[device] = {}
        for device_file in device_files:
            # execute query with a corrected measurement name to retrieve from the IoTDB
            measurement_name = correct_measurement_name(device_file, device)
            # read original dataset file
            original_data = orc.read_table(base_path + '/{}'.format(device_file) )
            original_data = original_data.to_pandas()
            
            query_statement = query_template.format(measurement_name, device)
            # select value column from iotdb result
            iotdb_data = session.execute_query_statement(query_statement).todf()
            results_dict[device][measurement_name] = {}
            for query in queries:
                # for MAX and MIN always filter out zeros
                if higher_than_zero or query.lower() in exlude_queries:
                    real_output = float(compute_aggregates_pandas(query, original_data.loc[ original_data['value'] > 0 ].iloc[:, 1]))
                    iotdb_val_col = iotdb_data.columns[-1]
                    iotdb_res = float(compute_aggregates_pandas(query, iotdb_data.loc[ iotdb_data[iotdb_val_col] > 0 ].iloc[:,-1]))
                else:
                    # now we iterate over each query and compute the diff between original value and IoTDB response
                    real_output = float(compute_aggregates_pandas(query, original_data.iloc[:, 1]))
                    iotdb_res = float(compute_aggregates_pandas(query, iotdb_data.iloc[:, 1]))
                                      
                if iotdb_res == real_output:
                    query_error = 0.0
                elif real_output == 0 or real_output is None or iotdb_res is None or np.isnan(real_output) or np.isnan(iotdb_res):
                    print("These real output: {} vs {} will generate nan".format(real_output, iotdb_res) )
                    query_error = None
                else:
                    query_error = abs((iotdb_res - real_output)/ real_output)
                
                results_dict[device][measurement_name][query] = query_error 
    session.close()
    return results_dict


def compute_max_min_median_rqe(results_dict, query):
    max_rqe = float("-inf")
    min_rqe = float("inf")
    median_res = []
    nan_cnt = 0
    for _, results in results_dict.items():
        for _, res in results.items():
            if res[query] is not None and ~np.isnan(res[query]):
                median_res.append(res[query])
                if res[query] > max_rqe:
                    max_rqe = res[query]
                if res[query] < min_rqe:
                    min_rqe = res[query] 
            else:
                nan_cnt += 1 
    return max_rqe, min_rqe, np.median(median_res), nan_cnt


if __name__ == "__main__":
    if len(sys.argv) < 7:
        raise Exception("Usage: script.py test_type dataset encoding precision higher_than_zero")
    test_type = sys.argv[1]
    dataset_name = sys.argv[2]
    encoding = sys.argv[3]
    precision = sys.argv[4]
    HIGHER_THAN_ZERO = bool(sys.argv[5])
    EXCLUDE_QUERIES = sys.argv[6:]
    # ENV Vars
    
    BASE_DATASET_PATH = '/path/to/raw/dataset' 
    
    device_group = get_device_groups(get_files(BASE_DATASET_PATH)) 

    if test_type == "mape": 
        QUERIES = ["min_value", "max_value", "AVG", "SUM"]
        header = ["dataset_name", "encoding", "precision", "mape", "max_absolute_error", "inf_count", "query", "rqe_min", "rqe_max", "rqe_median", 'nan_cnt']
        save_file = f"{test_type}-{dataset_name}-{encoding}-{precision}-metrics.csv"
        mape_value, max_errors, inf_cnt, rqe_results = compute_iotdb_mape_OLAP_queries(device_group, BASE_DATASET_PATH, not_zero=True)
        for query in QUERIES:
            rqe_max, rqe_min, rqe_median, nan_cnt = compute_max_min_median_rqe(rqe_results, query)
            row = [dataset_name, encoding, precision, mape_value, max_errors, inf_cnt, query, rqe_min, rqe_max, rqe_median, nan_cnt]
            # append metrics
            with open(save_file, "a") as f:
                writer = csv.writer(f)
                writer.writerow(row)
    elif test_type == "query_error_min_max_sum":
        QUERIES = ["min_value", "max_value", "AVG", "SUM"]
        header = ["dataset_name", "encoding", "precision", "query", "rqe_min", "rqe_max", "rqe_median", 'nan_cnt']
        save_file = f"{test_type}-{dataset_name}-{encoding}-{precision}-metrics.csv"
        rqe_results = compute_iotdb_min_max_sum(device_group, BASE_DATASET_PATH, higher_than_zero=HIGHER_THAN_ZERO)
        for query in QUERIES:
            rqe_max, rqe_min, rqe_median, nan_cnt = compute_max_min_median_rqe(rqe_results, query)
            row = [dataset_name, encoding, precision, query, rqe_min, rqe_max, rqe_median, nan_cnt]
            # append metrics
            with open(save_file, "a") as f:
                writer = csv.writer(f)
                writer.writerow(row)
    elif test_type == "query_error_min_std_median":
        QUERIES = ["MIN", "AVG", "MAX", "STD", "MEDIAN", "SUM"]
        header = ["dataset_name", "encoding", "precision", "query", "rqe_min", "rqe_max", "rqe_median", 'nan_cnt']
        save_file = f"{test_type}-{dataset_name}-{encoding}-{precision}-metrics.csv"
        with open(save_file, "w") as f:
            writer = csv.writer(f)
            writer.writerow(header)
        rqe_results = compute_iotdb_max_median_std(device_group, BASE_DATASET_PATH, QUERIES, higher_than_zero=HIGHER_THAN_ZERO, exlude_queries=EXCLUDE_QUERIES)
        for query in QUERIES:
            rqe_max, rqe_min, rqe_median, nan_cnt = compute_max_min_median_rqe(rqe_results, query)
            row = [dataset_name, encoding, precision, query, rqe_min, rqe_max, rqe_median, nan_cnt]
            # append metrics
            with open(save_file, "a") as f:
                writer = csv.writer(f)
                writer.writerow(row)
    else:
        raise RuntimeError("Please enter valid test type: 1) mape_and_query_error or 2) query_error_min_max_sum or 3) query_error_min_std_median")
    # dumpping extended query results
    with open(f"{test_type}-{dataset_name}_{encoding}_{precision}_extended_rqe.json", "w") as f:
        json.dump(rqe_results, f, indent = 6) 
    
