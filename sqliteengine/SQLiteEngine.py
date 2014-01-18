import sqlite3

class SQLiteEngine(object):
    def __init__(self, database_path, cache_tablenames = False):

        self.cache_tablenames = cache_tablenames
        self.connection = Connection(database_path)
        self.cursor = self.connection.cursor()

        self.insert_pool = []

        if self.cache_tablenames:
            self.cached_tablenames = self.cache_tablenames()
            
    def create_database(self, table_name, *columns):
        """
        Create a table in the database if one does not exist.
        """
        table_exists = self.table_exists(table_name)
        if not table_exists:
            query =  "CREATE TABLE %s" % table_name
            query += "(" + ",".join(["%s %s" % (column, column_type) for column, column_type in
                                     [tup for tup in columns]
                                    ])
            query += ");"
            self.cursor.execute(query)
            if self.cache_tablenames:
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
            table_names.append(table[0][0])
        return table_names

    def table_exists(self, table_name):
        """
        Search for a table name in the database.
        """
        query = "SELECT name FROM sqlite_master \
                 WHERE type = 'table' AND name = '?';"
        if len(self.cursor.execute(query, table_name)) == 1:
            return True
        else:
            return False

    def all_tables(self):
        """
        Return the name of all tables in the database.
        """
        query = "SELECT name FROM sqlite_master \
                 WHERE type = 'table'"
        return self.cursor.execute(query)

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
        self.insert_pool.append(new_item)
        return True

    def commit_pool(self):
        """
        Insert all items currently in the pool to the database.
        """
        for item in self.insert_pool:
            table_exists = True
            if self.cache_tablenames:
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
                raise InvalidTablename("The table `%s` does not exist." % item["__table_name"])

            columns = set(list(item.keys())) - set(["__table_name"])
            query =  "INSERT INTO %s" % item["__table_name"] + "(" + ",".join(columns) + ")"
            query += "VALUES (" + ",".join(list(item.get(value) for value in columns)) + ");"
            self.cursor.execute(query, column_values)
        return True

class Connection(object):
    def __init__(self,database, commit_after_execute = True):
        self.database = sqlite3.connect(database)
        self.connection = self.database.cursor
        self.commit_after_execute = commit_after_execute
    def execute(self,*args,**kwargs):
        """
        Execute an sql query and commit immediately afterwards.
        """
        self.connection.execute(args,kwargs)
        if self.commit_after_execute:
            self.database.commit()
    def cursor(self):
        """
        Return self because execute is accessable through the class already.
        """
        return self

class GeneralException(Exception):
    def __init__(self, message):
        self.message = message
    def __repr__(self):
        return repr(self.message)
    def __str__(self):
        return str(self.message)

class InvalidTableName(GeneralException):
    pass
class TableAlreadyExists(GeneralException):
    pass
class ItemKeyReserved(GeneralException):
    pass