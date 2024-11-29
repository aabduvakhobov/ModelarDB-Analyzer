import pandas as pd
import numpy as np
import sys
import pyarrow.orc as pc
import math
import csv
import os
import time
import logging


""""
script that returns MAPE and max error for aggregated dataset.

args: 
    1. Path to original dataset
    2. Path to aggregated dataset

"""

# read both datasets
# merge two datasets on timestamp
# forward fill the aggregated datasets null values
# calculate the MAPE
# calculate the MAX absolute error, mse, rmse, mae

#Defining MAPE function
def mape(y,yhat):
    np.seterr(all="print")
    x = np.abs((y - yhat)/y)
    x = np.nan_to_num(x, nan=0, posinf=0, neginf=0) 
    #x = x[~np.isnan(x)]
    #x = x[~(x==np.inf)]
    mape = np.mean(x)*100
    return mape

def max_absolute_error(y, y_hat):
    np.seterr(all="print")
    x = np.abs((y - y_hat)/y)
    return np.nan_to_num(x, nan=0, posinf=0, neginf=0).max()


def dflist(path):
    datasets = []
    for dirname, _, filenames in os.walk(path):
        for filename in filenames:
            datasets.append(dirname+"/"+filename)
    return datasets


    
if __name__=="__main__":
    
    timestamp_col = "ts"
    logging.basicConfig(filename="logs/metrics-generator.log", filemode="w", format='%(asctime)s - %(message)s', level=logging.INFO)
    
    # create metrics csv file
    header = ["si", "dataset_name", "mape", "max_absolute_error", "mse", "rmse", "mae"]
    with open("metrics.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        
    
    original_data_path = "/srv/data5/abduvoris/ukwan-selected"
    aggregates_home_path = "/srv/data5/abduvoris/ukwan-aggregates-univariate/{}x/mean/"
    datasets = dflist(original_data_path)
    
    for si in [7, 14, 33, 67, 400, 4000]:
        for dataset in datasets:
            
            dataset_name = dataset.split("/")[-1].replace(".orc", "")
            new_path_2 = aggregates_home_path.format(si) + dataset.split("/")[-1]
            logging.info(f"{new_path_2} being processed")
            tic = time.perf_counter()
            
            original_df = pd.read_orc(dataset)
            aggregate_df = pd.read_orc(new_path_2)
            
            single_df = pd.merge(original_df, aggregate_df, how="left", on=timestamp_col)
            single_df.fillna(method="ffill", inplace=True)
            
            y=single_df.iloc[:, 1].values
            yhat=single_df.iloc[:, 2].values
            
            mape_val = mape(y,yhat)
            max_error_val = max_absolute_error(y,yhat)
            mse = np.mean(np.square(np.subtract(y,yhat)))
            rmse = math.sqrt(mse)
            mae= np.mean(np.abs(y-yhat))
            # header order: ["si", "dataset_name", "mape", "max_absolute_error", "mse", "rmse", "mae"]
            row = [si, dataset_name, mape_val, max_error_val, mse, rmse, mae]
            
            
            # append metrics
            with open("metrics.csv", "a") as f:
                writer = csv.writer(f)
                writer.writerow(row)
            tac = time.perf_counter()
            logging.info(f"{new_path_2} write time: {tac - tic:0.4f} seconds, vals:\n{row}")
    
    toc = time.perf_counter()
    logging.info(f"Overall metrics execution time: {toc - tic:0.4f} seconds")
            
    
    
    
     
