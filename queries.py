# create statements

CREATE_FILE_SIZE_TABLE_SQL: str = """
CREATE TABLE IF NOT EXISTS file_size (
id integer PRIMARY KEY AUTOINCREMENT,
error_bound integer,
original_size integer, 
compressed_size integer, 
expected_size integer
);"""

CREATE_SEGMENT_SIZE_TABLE_SQL: str = """
CREATE TABLE IF NOT EXISTS segment_size (
id integer PRIMARY KEY,
time_series varchar,
error_bound integer,
model_type varchar,
data_point integer,
segment integer
);"""


CREATE_SEGMENT_SIZE_TABLE_SQL_OLD: str = """
CREATE TABLE IF NOT EXISTS segment_size (
id integer PRIMARY KEY,
time_series varchar,
error_bound integer,
pmc_data_points integer,
swing_data_points integer,
gorilla_data_points integer,
pmc_segments integer,
swing_segments integer,
gorilla_segments integer
);"""


CREATE_ERROR_TABLE_SQL: str = """
CREATE TABLE IF NOT EXISTS error_table (
id integer PRIMARY KEY,
time_series varchar,
error_bound integer,
average_error double,
maximum_error double,
difference_count integer,
count integer
);"""


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
# drop statements
DROP_TABLE_SEGMENT_SIZE_TABLE_QUERY = """DROP TABLE IF EXISTS segment_size;"""

DROP_TABLE_FILE_SIZE_TABLE_QUERY = """DROP TABLE IF EXISTS file_size;"""

DROP_TABLE_ERROR_TABLE_QUERY = """DROP TABLE IF EXISTS error_table;"""

# Insert statements
INSERT_SEGMENT_SIZE_QUERY = """
INSERT INTO segment_size (id, time_series, error_bound, model_type, data_point, segment)
VALUES (?,?,?,?,?,?)
"""

INSERT_FILE_SIZE_QUERY = """
INSERT INTO file_size (id, error_bound, original_size, compressed_size, expected_size)
VALUES (?,?,?,?,?);
"""

INSERT_ACTUAL_ERROR_QUERY = """
INSERT INTO error_table (id, time_series, error_bound, average_error, maximum_error, difference_count, count)
VALUES (?,?,?,?,?,?,?);
"""

INSERT_FILE_SIZE_QUERY_OLD = """
INSERT INTO file_size (id, original_size, compressed_size_0, expected_0, compressed_size_1, expected_1,
 compressed_size_5, expected_5, compressed_size_10, expected_10)
VALUES (?,?,?,?,?,?,?,?,?,?);
"""