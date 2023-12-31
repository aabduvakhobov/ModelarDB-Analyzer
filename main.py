import subprocess
import configparser

from db_loader import MyDB
from output_parser import OutputParser, SegmentAnalyzer

# TODO: go one level up and consider multiple databases
# TODO: create a list of parameters to iterate from
# creates sqlite database to store fetched data



def run_script(modelardb_path, error_bound, verifier_path, output_path):
    # also need to pass in output_path
    subprocess.run(["bash", "loader-modelardb.sh", f"{modelardb_path}", f"{error_bound}", f"{verifier_path}", f"{output_path}"])


if __name__ == '__main__':

    db = MyDB("./output.db")
    conn = db.create_connection()
    db.create_table(conn, delete=True)
    db.create_table(conn)
    
    config = configparser.ConfigParser()
    config.read("config.cfg")
    # iterate over bunch of files. use regex to get required elements and write them to db
    run_script(config["DEFAULT"]["MODELARDB_PATH"], config["INGESTION"]["ERROR_BOUND"], config["DEFAULT"]["VERIFIER_PATH"], config["INGESTION"]["OUTPUT_PATH"])

    parser = OutputParser(config["INGESTION"]["DATA_PATH"], config["INGESTION"]["OUTPUT_PATH"], config["INGESTION"]["ERROR_BOUND"])

    file_size_list = parser.parse_file_size_ver()
   
    segments_output_list = parser.parse_segment_size()

    errors_output_list = parser.parse_errors()
    
    actual_error_histogram_list = parser.parse_actual_error_histogram()
    
    # segment_analyser = SegmentAnalyzer(constants.OUTPUT_PATH, constants.ERROR_BOUND)    
    # cons_gorilla_segments = segment_analyser.run()
    # now insert data to db
    for data in file_size_list:
        db.insert_metrics(conn, data, 0)

    for data in segments_output_list:
        db.insert_metrics(conn, data, 1)

    for data in errors_output_list:
        db.insert_metrics(conn, data, 2)
        
    for data in actual_error_histogram_list:
        db.insert_metrics(conn, data, 4)
    
    
    # now insert data for badly compressed segments
    # for data in cons_gorilla_segments:
    #     db.insert_metrics(conn, data, 3)
    
    print("Segment table")
    db.select_table(conn, "segment_size")
    print("File_size and actual error table: ")
    db.select_table(conn, "file_size")

    print("Error table:")
    db.select_table(conn, "error_table")
    
    # print("Consecutive segments")
    # db.select_table(conn, "consecutive_gorilla_segments")
    
    print("Actual Error Histogram")
    db.select_table(conn, "actual_error_histogram")

    conn.close()
