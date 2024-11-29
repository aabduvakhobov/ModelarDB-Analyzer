import pandas as pd
from pyarrow import flight
from time import perf_counter
import time
import sys
import csv
import os
import configparser

config = configparser.ConfigParser()
config.read('config.cfg')

SAVE_DIR = config['DEFAULT']['RESULTS_SAVE_PATH']


DATASET = "WTM"
MDB_VALUE_COLUMN_NAME = "location"

queries_per_tid_datapoint = {
    "COUNT" : "SELECT COUNT(*) FROM datapoint where tid={}",
    "SUM" : "SELECT SUM(value) FROM datapoint where tid={}",
    "MAX" : "SELECT MAX(value) FROM datapoint where tid={} AND value > 0",
    "MIN" : "SELECT MIN(value) FROM datapoint where tid={} AND value > 0",
    "AVG" : "SELECT AVG(value) FROM datapoint where tid={}",
    "STD" : "SELECT STD(value) FROM datapoint where tid={}",
    'ALL' : "SELECT value FROM datapoint where tid={}",
    "MEDIAN" : "SELECT approx_percentile(value, 0.5) FROM datapoint where tid={}",
}


queries_per_tid_segment = {
    "COUNT" : "SELECT COUNT_S(#) FROM Segment where tid={}",
    "SUM" : "SELECT SUM_S(#) FROM Segment where tid={}",
    "MAX" : "SELECT MAX_S(#) FROM Segment where tid={}",
    "MIN" : "SELECT MIN_S(#) FROM Segment where tid={}",
    "AVG" : "SELECT AVG_S(#) FROM Segment where tid={}"
}

queries_all_datapoint = {
    "COUNT" : "SELECT COUNT(*) FROM datapoint",
    "SUM" : "SELECT SUM(value) FROM datapoint",
    "MAX" : "SELECT MAX(value) FROM datapoint",
    "MIN" : "SELECT MIN(value) FROM datapoint",
    "AVG" : "SELECT AVG(value) FROM datapoint"
}


def get_tid(ts_path, signal, column_name):
    import pandas as pd
    ts = pd.read_orc(ts_path)
    return ts.loc[ts[column_name]==signal, 'tid'].values[0]


def query_modelardb(flight_client, query): 
    tic = perf_counter()
    ticket = flight.Ticket(query)
    # wait until response is received
    while True:
        try:        
            flight_stream_reader = flight_client.do_get(ticket)
            res = flight_stream_reader.read_all()
            execution_time = perf_counter() - tic
            break
        except Exception as e:
            print(e)
            time.sleep(20)
            pass
    print("Processed in {:.2f} s".format(execution_time))    
    return res, execution_time


def write_csv(filename, rows):
    mode = "a" if os.path.exists(filename) else "w"
    # field names
    with open(filename, mode) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(rows)
        
        
def main(error_bound:float, modelardb_data_path:str, filter_out_not_zero:bool):

    ts_path = modelardb_data_path + "/time_series.orc"
    target_queries = ["MAX", "MIN", "AVG", "STD", "MEDIAN"]
    
    signals = pd.read_orc(ts_path)[MDB_VALUE_COLUMN_NAME].tolist()
    output = {}
    csv_header = [
        'dataset', 'signal','error_bound', 'query', 'result', 'execution_time', 'datapoint_cnt'
        ]
    csv_file_name = f"{SAVE_DIR}/results-{error_bound}.csv"
    # delete old csv file
    if os.path.exists(csv_file_name):
        os.remove(csv_file_name)
    write_csv(csv_file_name, csv_header)
    socket = "grpc://127.0.0.1:9999"
    flight_client = flight.FlightClient(socket)
    for query in target_queries:
        for signal in signals:
            print("Processing: " + query + ": " + signal)
            tid = get_tid(ts_path, signal, MDB_VALUE_COLUMN_NAME)
            if query in ["AVG"] and not filter_out_not_zero:
                query_statement = queries_per_tid_segment[query].format(tid)
            else:
                query_statement = queries_per_tid_datapoint[query].format(tid)

            if filter_out_not_zero and query in ["STD", "MEDIAN", "AVG"]:
                query_statement = query_statement + " AND value <> 0"
            res, execution_time = query_modelardb(flight_client, query_statement)
            val = res.to_pandas().iloc[0,0]
            output = [DATASET, signal, error_bound, query, val, execution_time, len(signal)]
            write_csv(csv_file_name, output)
    flight_client.close()

if __name__ == "__main__":
    
    if len(sys.argv) < 4:
        raise SyntaxError("Insufficient arguments. Usage: Arg1: error_bound Arg2: /path/to/modelardb-data Arg3: 0 or 1")
    else:
        error_bound = float(sys.argv[1])
        modelardb_data_path = sys.argv[2]
        filter_out_not_zero = bool(sys.argv[3])
        main(error_bound, modelardb_data_path, filter_out_not_zero)