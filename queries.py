CREATE_FILE_SIZE_TABLE_SQL: str = """
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


CREATE_SEGMENT_SIZE_TABLE_SQL: str = """
CREATE TABLE IF NOT EXISTS segment_size (
id integer PRIMARY KEY,
Signal varchar(45),
Error_bound integer,
PMC_data_points integer,
Swing_data_points integer,
Gorilla_data_points integer,
PMC_segments integer,
Swing_segments integer,
Gorilla_segments integer
);"""

DROP_TABLE_SEGMENT_SIZE_QUERY = """DROP TABLE IF EXISTS segment_size;"""

DROP_TABLE_FILE_SIZE_QUERY = """DROP TABLE IF EXISTS file_size;"""


INSERT_SEGMENT_SIZE_QUERY = """
INSERT INTO segment_size (id, Signal, Error_bound, PMC_data_points, Swing_data_points, 
Gorilla_data_points, PMC_segments, Swing_segments, Gorilla_segments)
VALUES (?,?,?,?,?,?,?,?,?);
"""
INSERT_FILE_SIZE_QUERY = """
INSERT INTO file_size (id, original_size, compressed_size_0, expected_0, compressed_size_1, expected_1,
 compressed_size_5, expected_5, compressed_size_10, expected_10)
VALUES (?,?,?,?,?,?,?,?,?,?);
"""