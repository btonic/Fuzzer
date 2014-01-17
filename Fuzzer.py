import sqliteengine as SQLEngine
import random

class Fuzzer(object):
    def __init__(self, database = ":memory:", cache_tablenames = True):
        self.sql_engine = SQLEngine.SQLiteEngine(database)

    def initialize(self):
        """
        Initialize the database, if there is not already one.
        """
        try:
            self.sql_engine.create_database("attempts",
                                           ("attempt_id","PRIMARY KEY"),
                                           ("attempted", "TEXT"),
                                           ("successful","BOOL"),
                                           ("created_at","TEXT")
                                           )
        except TableAlreadyExists:
            pass
        return True

