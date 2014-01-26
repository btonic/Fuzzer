import sqlite3
from threading import Lock

class SQLiteEngine(object):
    """
    SQL engine backend for multithreaded use. Allows for in-memory storage to
    mass-commit.
    """
    def __init__(self, database_path, tables_to_cache=False):

        self.tables_to_cache = tables_to_cache
        self.connection = Connection(database_path)
        self.cursor = self.connection.cursor()
        self.cached_tablenames = []

        self.pool_lock = Lock()
        self.pool_lock_activated = False
        self.insert_pool = []

        if self.tables_to_cache:
            self.cache_tablenames()

    def create_database(self, table_name, *columns):
        """
        Create a table in the database if one does not exist.
        """
        table_exists = self.table_exists(table_name)
        if not table_exists:
            query = "CREATE TABLE %s" % table_name
            query += "(" + ",".join(["%s %s" % (column, column_type)
                                    for column, column_type in
                                    [tup for tup in columns]
                                    ])
            query += ");"
            self.cursor.execute(query)
            if self.tables_to_cache:
                self.cached_tablenames = self.cache_tablenames()
        if table_exists:
            raise TableAlreadyExists("Table: `%s` already exists." % table_name)
        return True

    def cache_tablenames(self):
        """
        Create an in-memory list of all table names.
        Prevents another read from the DB from being necessary.
        """
        table_names = []
        for table in self.all_tables():
            table_names.append(table[0])
        if not self.tables_to_cache:
            self.tables_to_cache = True
        self.cached_tablenames = table_names

    def table_exists(self, table_name):
        """
        Search for a table name in the database.
        """
        query = "SELECT name FROM sqlite_master\
                 WHERE type = 'table' AND name = ?;"
        if len(self.cursor.execute(query, (table_name,)).fetchall()) == 1:
            return True
        else:
            return False

    def all_tables(self):
        """
        Return the name of all tables in the database.
        """
        query = "SELECT name FROM sqlite_master \
                 WHERE type = 'table'"
        return self.cursor.execute(query).fetchall()

    def append_to_pool(self, item, table_name):
        """
        Append an item to the list to be entered into the DB.
        Column =>    dictionary key
        Value  =>    dictionary value
        tablename => added explicitly.
        """
        if type(item) != type(dict()):
            raise TypeError("`item` must be type: `dict`.")
        new_item = item.copy()
        if new_item.get("__table_name") != None:
            raise ItemKeyReserved("`__table_name` is a reserved key.")
        new_item["__table_name"] = table_name
        while self.pool_lock_activated:
            pass
        self.insert_pool.append(new_item)
        return True

    def commit_pool(self):
        """
        Insert all items currently in the pool to the database.
        """
        current_pool = list(self.insert_pool)
        for item in current_pool:
            table_exists = True
            if self.tables_to_cache:
                if item["__table_name"] in self.cached_tablenames:
                    pass
                else:
                    table_exists = False
            else:
                if self.table_exists(item["__table_name"]):
                    pass
                else:
                    table_exists = False
            if not table_exists:
                raise InvalidTablename("The table `%s` does not exist."
                                       % item["__table_name"])

            columns = set(list(item.keys())) - set(["__table_name"])
            column_values = list(item.get(value) for value in columns)
            query = "INSERT INTO %s" % item["__table_name"] + \
                    "(" + ",".join(columns) + ")"
            query += "VALUES (" + (",".join(
                             list("?" for x in range(len(columns)))))+\
                             ")"
            self.cursor.execute(query, column_values)

        if self.pool_lock.acquire():
            self.pool_lock_activated = True
            self.insert_pool = list(value for value in current_pool
                                    if value not in self.insert_pool)
            self.pool_lock_activated = False
            self.pool_lock.release()
        return True

class Connection(object):
    """
    Connection provides a simple connection method to simplify SQL statement
    execution.
    """
    def __init__(self, database, commit_after_execute=True):
        self.database = sqlite3.connect(database)
        self.connection = self.database.cursor()
        self.commit_after_execute = commit_after_execute
    def execute(self, sql_query, *args):
        """
        Execute an sql query and commit immediately afterwards.
        """
        self.connection.execute(sql_query, *args)
        if self.commit_after_execute:
            self.database.commit()
        return self.connection
    def cursor(self):
        """
        Return self because execute is accessable through the class already.
        """
        return self

class GeneralException(Exception):
    """
    Baseclass for all exceptions raised by SQLiteEngine.
    """
    def __init__(self, message):
        self.message = message
    def __repr__(self):
        return repr(self.message)
    def __str__(self):
        return str(self.message)

class InvalidTablename(GeneralException):
    """
    Raised when an invalid table is found.
    """
    pass
class TableAlreadyExists(GeneralException):
    """
    Raised when a table is being made but one already exists.
    """
    pass
class ItemKeyReserved(GeneralException):
    """
    Raised when the __table_name is used in an item.
    """
    pass
