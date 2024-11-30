import subprocess
import configparser
import os

import compute_aggregates


config = configparser.ConfigParser()
config.read('../../config.cfg')

DATASET = "WTM"
SAVE_DIR = './OLAP_query_results'


if __name__ == "__main__":
    # compute aggregates and store
    subprocess.run(
        [
            'bash',
            'downsampler-ingestor.sh',
            config['AGG']['WTM_SI'],
            config['AGG']['AGGREGATES_SAVE_PATH'],
            '../../' + config['DATA']['WTM_UNIVARIATE'],
            'downsample.py'            
        ]
    )
    # create output save dir if not exists
    if not os.path.exists(SAVE_DIR):
        os.mkdir(SAVE_DIR)
    # compute OLAP queries on aggregates
    compute_aggregates.main(DATASET, True, SAVE_DIR)