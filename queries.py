# create statements

CREATE_FILE_SIZE_TABLE_SQL: str = """
CREATE TABLE IF NOT EXISTS file_size (
id INTEGER PRIMARY KEY AUTOINCREMENT,
error_bound DOUBLE,
theoretical_size INTEGER,
actual_file_size INTEGER, 
compressed_size INTEGER,
models_size INTEGER,
metadata_size INTEGER,
gaps_size INTEGER,
expected_size INTEGER
);"""

CREATE_SEGMENT_SIZE_TABLE_SQL: str = """
CREATE TABLE IF NOT EXISTS segment_size (
id INTEGER PRIMARY KEY AUTOINCREMENT,
time_series VARCHAR,
error_bound DOUBLE,
model_type TEXT,
data_point INTEGER,
segment INTEGER,
median_segment_length DOUBLE
);"""

CREATE_ERROR_TABLE_SQL: str = """
CREATE TABLE IF NOT EXISTS error_table (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    time_series VARCHAR,
    error_bound DOUBLE,
    average_error DOUBLE,
    maximum_error DOUBLE,
    difference_count INTEGER,
    count INTEGER,
    mean_absolute_error DOUBLE
);"""


CREATE_BADLY_COMPRESSED_SQL: str = """
CREATE TABLE IF NOT EXISTS consecutive_gorilla_segments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tsid INTEGER NOT NULL,
    time_series TEXT NOT NULL,
    error_bound DOUBLE NOT NULL,
    data TEXT NOT NULL 
);
"""


CREATE_FILE_SIZE_TABLE_HOR_SQL: str = """
CREATE TABLE IF NOT EXISTS file_size (
id integer PRIMARY KEY AUTOINCREMENT,
original_size double, 
compressed_size_0 double, 
expected_0 double, 
compressed_size_1 double, 
expected_1 double, 
compressed_size_5 double, 
expected_5 double,  
compressed_size_10 double, 
expected_10 double
);"""

CREATE_SEGMENT_SIZE_TABLE_SQL_OLD: str = """
CREATE TABLE IF NOT EXISTS segment_size (
id integer PRIMARY KEY,
time_series varchar,
error_bound double,
pmc_data_points integer,
swing_data_points integer,
gorilla_data_points integer,
pmc_segments integer,
swing_segments integer,
gorilla_segments integer
);"""

# drop statements
DROP_TABLE_SEGMENT_SIZE_TABLE_QUERY = """DROP TABLE IF EXISTS segment_size;"""

DROP_TABLE_FILE_SIZE_TABLE_QUERY = """DROP TABLE IF EXISTS file_size;"""

DROP_TABLE_ERROR_TABLE_QUERY = """DROP TABLE IF EXISTS error_table;"""

DROP_TABLE_CONS_GORILLA_SEGMENTS_QUERY = "DROP TABLE IF EXISTS consecutive_gorilla_segments;"

# Insert statements
INSERT_SEGMENT_SIZE_QUERY = """
INSERT INTO segment_size (time_series, error_bound, model_type, data_point, segment, median_segment_length)
VALUES (?,?,?,?,?,?);
"""

INSERT_FILE_SIZE_QUERY = """
INSERT INTO file_size (error_bound, theoretical_size, actual_file_size, compressed_size, models_size, metadata_size, gaps_size, expected_size)
VALUES (?,?,?,?,?,?,?,?);
"""

INSERT_ACTUAL_ERROR_QUERY = """
INSERT INTO error_table (time_series, error_bound, average_error, maximum_error, difference_count, count, mean_absolute_error)
VALUES (?,?,?,?,?,?,?);
"""

INSERT_CONS_GORILLA_SEGMENTS_QUERY = """
INSERT INTO consecutive_gorilla_segments (tsid, time_series, error_bound, data)
VALUES (?,?,?,?);
"""
####################################################################
INSERT_FILE_SIZE_QUERY_OLD = """
INSERT INTO file_size (id, original_size, compressed_size_0, expected_0, compressed_size_1, expected_1,
 compressed_size_5, expected_5, compressed_size_10, expected_10)
VALUES (?,?,?,?,?,?,?,?,?,?);
"""