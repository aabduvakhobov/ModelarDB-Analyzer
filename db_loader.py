import sqlite3
from sqlite3 import Error
import queries


class MyDB:
    def __init__(
            self,
            db_file,
            create_table_sql=[queries.CREATE_FILE_SIZE_TABLE_SQL, queries.CREATE_SEGMENT_SIZE_TABLE_SQL],
            delete_table_sql=[queries.DROP_TABLE_SEGMENT_SIZE_QUERY, queries.DROP_TABLE_FILE_SIZE_QUERY],
            insert_query=[queries.INSERT_FILE_SIZE_QUERY, queries.INSERT_SEGMENT_SIZE_QUERY]
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

    def insert_metrics(self, conn, data, file_size=True):
        cur = conn.cursor()
        if file_size:
            cur.execute(self.insert_query[0], data)
        else:
            cur.execute(self.insert_query[1], data)
        conn.commit()

    def select_segments(self, conn):
        cur = conn.cursor()
        cur.execute("SELECT * FROM segment_size;")
        print(cur.fetchall())

    def select_file_size(self, conn):
        cur = conn.cursor()
        cur.execute("SELECT * FROM file_size;")
        print(cur.fetchall())
