import subprocess
import re
import os
from sqlite3 import Error

from db_loader import MyDB
from output_parser import OutputParser


# TODO: go one level up and consider multiple databases
# TODO: create a list of parameters to iterate from
# creates sqlite database to store fetched data
MODELARDB_PATH = "$HOME/ModelarDB-Home/ModelarDB-dev/ModelarDB"
ERROR_BOUND = "0 1 5"
OUTPUT_PATH = "$HOME/ModelarDB-Home/tempDBs/Ingested"
DATA_PATH ="$HOME/ModelarDB-Home/ModelarDB/data/low_freq/processed"
CONF_PATH = "$HOME/.modelardb.conf"



def run_script(MODELARDB_PATH):
    # also need to pass in output_path
    subprocess.run(["bash", "loader-modelardb.sh", f"{MODELARDB_PATH}", f"{ERROR_BOUND}", f"{CONF_PATH}"])


if __name__ == '__main__':

    # db = MyDB("./output.db")
    #
    # conn = db.create_connection()
    # db.create_table(conn, delete=True)
    # db.create_table(conn)

    # iterate over bunch of files. use regex to get required elements and write them to db


    run_script(MODELARDB_PATH)

    parser = OutputParser(DATA_PATH, OUTPUT_PATH, ERROR_BOUND)
    output_list = parser.parse_segment_size()
    print(output_list)
    # file_size_dict = parser.parse_file_size()
    # print(file_size_dict.values())
    # now insert data to db

    # for data in output_list:
    #     db.insert_metrics(conn, data, file_size=False)

    # print(file_size_dict)

    # db.insert_metrics(conn, [0] + list(file_size_dict.values()))
    # print(db.select_segments(conn))
    # print(db.select_file_size(conn))
    # conn.close()