import subprocess

from db_loader import MyDB
from output_parser import OutputParser


# TODO: go one level up and consider multiple databases
# TODO: create a list of parameters to iterate from
# creates sqlite database to store fetched data
HOME = "/home/cs.aau.dk/zg03zi"
MODELARDB_PATH = f"{HOME}/ModelarDB-Home/ModelarDB"
ERROR_BOUND = "0 0.01 0.05 0.1 0.2 0.5 1"
# ERROR_BOUND = "0"
OUTPUT_PATH = f"{HOME}/ModelarDB-Home/tempDBs/Ingested" #"/srv/data5/abduvoris/Ingested" 
DATA_PATH = "/srv/data5/abduvoris/ukwan-selected" # for estimating size of raw data
VERIFIER_PATH = f"{HOME}/ModelarDB-Home/ModelarDB-Evaluation-Tool/Verifier_2"


def run_script(modelardb_path, error_bound, verifier_path, output_path):
    # also need to pass in output_path
    subprocess.run(["bash", "loader-modelardb.sh", f"{modelardb_path}", f"{error_bound}", f"{verifier_path}", f"{output_path}"])


if __name__ == '__main__':

    db = MyDB("./output.db")
    conn = db.create_connection()
    db.create_table(conn, delete=True)
    db.create_table(conn)

    # iterate over bunch of files. use regex to get required elements and write them to db
    run_script(MODELARDB_PATH, ERROR_BOUND, VERIFIER_PATH, OUTPUT_PATH)

    parser = OutputParser(DATA_PATH, OUTPUT_PATH, ERROR_BOUND)

    file_size_list = parser.parse_file_size_ver()
   
    segments_output_list = parser.parse_segment_size()

    errors_output_list = parser.parse_errors()
    # now insert data to db
    for data in file_size_list:
        db.insert_metrics(conn, data, 0)

    for data in segments_output_list:
        db.insert_metrics(conn, data, 1)

    for data in errors_output_list:
        db.insert_metrics(conn, data, 2)

    db.select_table(conn, "segment_size")
    print("File_size and actual error table: ")
    db.select_table(conn, "file_size")

    print("Error table:")
    db.select_table(conn, "error_table")

    conn.close()
