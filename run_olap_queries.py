import configparser

import utils.olap_modelardb as run_all_queries

# read config file
config = configparser.ConfigParser()
config.read('config.cfg')


if __name__ == "__main__":
    modelardb_path = config['DEFAULT']['MODELARDB_PATH']
    filter_out_zeros = bool(int(config['OLAP_QUERIES']['FILTER_OUT_ZEROS']))
    error_bound = float(config['OLAP_QUERIES']['ERROR_BOUND'])
    # runs all queries  
    run_all_queries.main(error_bound, modelardb_path + '/modelardb', filter_out_zeros)