import sqliteengine as SQLEngine
import sqlite3
#TEMPORARY UNTIL UNIT TESTS ARE WRITTEN.
def main():
    engine = SQLEngine.SQLiteEngine(":memory:")
    print "Table does not exists: ", not engine.table_exists("non_existant")
    engine.create_database("test",
    	                   ("col1","INT"),
    	                   ("col2","INT"))
    print "Table does exist: ", engine.table_exists("test")
    engine.cache_tablenames()
    print "Cached tablenames: ", engine.cached_tablenames
    print "All tables: ", engine.all_tables()
    engine.append_to_pool({"col1":200,"col2":400},"test")
    engine.commit_pool()



if __name__ == "__main__":
    main()