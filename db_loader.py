import sqlite3
from sqlite3 import Error
import queries


class MyDB:
    def __init__(
            self,
            db_file,
            create_table_sql=[queries.CREATE_FILE_SIZE_TABLE_SQL, queries.CREATE_SEGMENT_SIZE_TABLE_SQL, queries.CREATE_ERROR_TABLE_SQL],
            delete_table_sql=[queries.DROP_TABLE_SEGMENT_SIZE_TABLE_QUERY, queries.DROP_TABLE_FILE_SIZE_TABLE_QUERY, queries.DROP_TABLE_ERROR_TABLE_QUERY],
            insert_query=[queries.INSERT_FILE_SIZE_QUERY, queries.INSERT_SEGMENT_SIZE_QUERY, queries.INSERT_ACTUAL_ERROR_QUERY]
    ):
        self.db_file = db_file
        self.create_table_sql = create_table_sql
        self.delete_table_sql = delete_table_sql
        self.insert_query = insert_query

    def create_connection(self):
        """ create a database connection to a SQLite database """
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            return conn
        except Error as e:
            print(e)
        return conn

    def create_table(self, conn, delete=False):
        """ create a table from the create_table_sql statement
        :param conn: Connection object
        :param self: a CREATE TABLE statement
        :return:
        """
        try:
            c = conn.cursor()
            if delete:
                for query in self.delete_table_sql:
                    c.executescript(query)
            else:
                for query in self.create_table_sql:
                    c.executescript(query)
        except Error as e:
            print(e)

    def insert_metrics(self, conn, data, query):
        # choose query from the list of insert queries
        cur = conn.cursor()
        cur.execute(self.insert_query[query], data)
        conn.commit()

    def select_table(self, conn, table_name):
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM {table_name};")
        records = cur.fetchall()
        for row in records:
            print(row)

    def run_query(self, conn, query):
        cur = conn.cursor()
        cur.execute(query)
        records = cur.fetchall()
        for row in records:
            print(row)
