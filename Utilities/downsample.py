""""
Script for downsampling the time series file by a given multiple
Commandline Params:
    - argv[1]: Path to time series folder
    - argv[2]: Path for saving downsampled time series
    - argv[3]: Downsampling rate in multiplies 

"""

import pandas as pd
import numpy as np
import pyarrow.orc as pc
import os
import sys
import pyarrow
import time
from datetime import timedelta
import logging

SAMPLING_INTERVAL = 2
TIMESTAMP_COL = "datetime"
TIME_UNITS = "s"

def dataset_list(path):
    dataset_list = []
    
    for dirname, _, filenames in os.walk(path):
        for filename in filenames:
            # print(dirname+filename)
           
            dataset_list.append(dirname + filename)
            
    return dataset_list

def downsample_by_last_value(db_path, save_path, aggregate_factor):
    # reading dataset
    df = pd.read_orc(db_path)
    ts = db_path.split("/")[-1]
    print(ts + " being processed")
    # downsampling by pandas resample
    
    df = df.resample(rule=f"{SAMPLING_INTERVAL*aggregate_factor}{TIME_UNITS}", on=TIMESTAMP_COL, label="right", origin="start", closed="right").last()
    df.reset_index().dropna().to_orc(save_path+ts)
    print(f"{db_path} was saved at {save_path} \nwith {int(aggregate_factor)*SAMPLING_INTERVAL} sampling rate")
    
    
def downsample_by_mean(db_path, save_path, aggregate_factor):
    # reading dataset
    df = pd.read_orc(db_path)
    ts = db_path.split("/")[-1]
    print(ts + " being processed")
    # downsampling by pandas resample
    
    df = df.resample(rule=f"{SAMPLING_INTERVAL*aggregate_factor}{TIME_UNITS}", on=TIMESTAMP_COL, label="right", origin="start", closed="right").mean()
    df.reset_index().dropna().to_orc(save_path+ts)
    print(f"{db_path} was saved at {save_path} \nwith {int(aggregate_factor)*SAMPLING_INTERVAL} sampling rate")
    
    
if __name__== "__main__":
    logging.basicConfig(filename="downsampling-logs.log", filemode="w", format='%(asctime)s - %(message)s', level=logging.INFO)
    tic = time.perf_counter()
    PATH = sys.argv[1]
    SAVE_PATH_FOR_MEAN_AGGREGATE = sys.argv[2]
    # SAVE_PATH_FOR_LAST_AGGREGATE = sys.argv[3]
    MULTIPLE = int(sys.argv[3])
    # METHOD = sys.argv[4]
    
    ts_list = dataset_list(PATH)
    # print(ts_list[0])
    
    # downsampling of datasets
    for ts in ts_list:
        logging.info(f"{ts} being aggregated")
        print(f"{ts} being aggregated")
        # downsample_by_last_value(ts, SAVE_PATH_FOR_LAST_AGGREGATE, MULTIPLE)
        downsample_by_mean(ts, SAVE_PATH_FOR_MEAN_AGGREGATE, MULTIPLE)
        logging.info(f"{ts} done")
    logging.info(f"Job finished in {time.perf_counter() - tic:0.4f} seconds")
    print(f"Job finished in {time.perf_counter() - tic:0.4f} seconds")
        

        
        

    