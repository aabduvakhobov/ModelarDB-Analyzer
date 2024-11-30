from iotdb.Session import Session
from iotdb.template.MeasurementNode import TSDataType
from iotdb.template.MeasurementNode import TSEncoding
from iotdb.template.MeasurementNode import Compressor
from iotdb.utils import BitMap
from iotdb.utils import Tablet 
from iotdb.utils import NumpyTablet

import pandas as pd
import numpy as np
from pyarrow import csv
import pyarrow
from pyarrow import orc

import sys
import time
import logging
import configparser


def read_config(config_path = '../../config.cfg'):
    config = configparser.ConfigParser()
    config.read(config_path)
    return config

# read config file and create env vars
config = read_config()
THREASHOLD=10_000_000 # the number of rows in the tablet that IoTDB can process
DEVICE_ID = config['IOTDB']['DEVICE_ID']


def create_iotdb_session():
    ip = "127.0.0.1"
    port_ = "6667"
    username_ = "root"
    password_ = "root"
    # Apache IoT DB Database and TimeSeries creation
    session = Session(ip, port_, username_, password_)
    session.open(False)
    return session


def create_values_timestamps(table, start_index, end_index):
    table_cols = table.column_names
    np_values_ = []
    for col in table_cols:
        if col not in  ["ts", "datetime"]:
            # append values into value list
            np_values_.append(np.array( table.column(col).to_numpy()[start_index:end_index], TSDataType.FLOAT.np_dtype()) )
            # create and append bitmaps to bitmap list
            # we continue with the last file to extract timestamps as unix int64
        else:
            np_timestamps_ = np.array( pyarrow.Array.from_pandas(table.column(col)[start_index:end_index]).cast(pyarrow.timestamp("ms")).cast(pyarrow.int64()).to_numpy(), TSDataType.INT64.np_dtype())
            # create timestamp values
    if len(np_timestamps_) == 0 or len(np_values_) == 0:
        raise ValueError(f"Your timestamp with len: {len(np_timestamps_)} or numpy list with len: {len(np_values_)} is empty!")
    return np_timestamps_, np_values_


def create_numpy_tablets(file_path):
    # we ingest a single big ORC file in this context
    table = orc.read_table(file_path)
    table = table.select([col for col in table.column_names if col not in ['__index_level_0__']])
    # measurement are column names in the ORC file apart from datetime
    measurements_ = [col for col in table.column_names if col not in ['datetime', 'ts']]
    # we return list of numpy Tablets
    np_tablets = []
    # split dataset by 10 million rows and ingest in batches
    last_number = table.num_rows // THREASHOLD
    for i in range(last_number + 1):
        if i == last_number:
            start_index = i * THREASHOLD
            end_index = None
            print(f"Index: [{i * THREASHOLD}  : ]")
        else:
            start_index = i * THREASHOLD
            end_index = THREASHOLD + (i * THREASHOLD)
            print(f"Index: [{i * THREASHOLD}  : {THREASHOLD + (i*THREASHOLD)}]")
        # TODO: have a clause to return if start_index and end_index return empty table
        if table[start_index:end_index].num_rows == 0:
            return np_tablets
        
        # once we have start and end indeces, we create timestamps and numpy values
        np_timestamps_, np_values_ = create_values_timestamps(table, start_index, end_index) 
        # create data types for dataset columns  
        data_types_ = [TSDataType.FLOAT] * len(measurements_) 
        # create NumpyTablet
        np_tablet_ = NumpyTablet.NumpyTablet(
            DEVICE_ID, measurements_, data_types_, np_values_, np_timestamps_
            )
        np_tablets.append(np_tablet_)
    return np_tablets


def main(file_path:str):
    # np_tablet_
    session = create_iotdb_session()
    # give path to multivariate time series dataset
    np_tablets = create_numpy_tablets(file_path)
    tic = time.perf_counter()
    logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
    
    for tablet in np_tablets:
        session.insert_aligned_tablet(tablet)
    
    logging.info(f"Ingestion finished in:{time.perf_counter() - tic:0.4f} seconds")
    print("Completed ingestion!")
    session.execute_non_query_statement("FLUSH")
    session.close()
    

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise Exception("Usage: script.py path/to/file.orc")
    
    dataset_path = sys.argv[1]
    main(dataset_path)