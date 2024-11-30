import subprocess
import configparser
"""
The script for running the ingestion and query evaluation with IoTDB altogether
"""

def read_config(path="../../config.cfg"):
    config = configparser.ConfigParser()
    config.read(path)
    return config

    
if __name__ == "__main__":
    config = read_config()
    # ingest first
    subprocess.run(
        [
            'bash',
            'run_iotdb_wtm_pcd.sh',
            '../../' + config['DATA']['WTM_MULTIVARIATE_ORC'],
            config['IOTDB']['ENCODINGS'],
            config['IOTDB']['PRECISION_VALUES'],
            config['IOTDB']['IOTDB_DATABASE_SAVE_PATH'], 
            config['IOTDB']['SLEEP_FOR_VACUUM'],
            config['IOTDB']['OUTPUT_DIR'],
        ]
    )
    
    # run query evalyation
    subprocess.run(
        [
            'bash',
            'compute_mape_iotdb_wtm_pcd.sh',
            config['IOTDB']['ENCODINGS'],
            config['IOTDB']['PRECISION_VALUES'],
            config['IOTDB']['IOTDB_DATABASE_SAVE_PATH'], 
            config['IOTDB']['OUTPUT_DIR'],
        ]
    )