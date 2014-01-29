import unittest
import fuzzer.sqliteengine as SQLEngine

class TestSQLiteEngine(unittest.TestCase):
    """
    Test the functions of the sqliteengine.
    """
    def setUp(self):
        self.engine = SQLEngine.SQLiteEngine()
        self.testing_table_name = "testing_table"
    def tearDown(self):
        self.engine.stop()

    def test_create_database(self):
        """
        Test to make sure that a database is able to be created, and invalid
        input is handled.
        """
        self.assertTrue(
            self.engine.create_database(self.testing_table_name,
			                           ("test_row", "INT")),
            msg="create_database should return true upon success."
        )

        self.assertRaises(
            SQLEngine.TableAlreadyExists,
            self.engine.create_database(self.testing_table_name,
                                       ("test_row", "INT")),
            msg="Duplicate databases passed without error."
        )

        self.assertTrue(
            len(
                self.engine.cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'\
                    AND name = ?;", self.testing_table_name).fetchall()
            ) == 1,
            msg="The table should be committed into the database."
        )
    def test_table_exists(self):
        """
        Test to make sure that table_exists is able to report a missing and
        existing table.
        """
        self.assertFalse(
            self.engine.table_exists(self.testing_table_name),
            msg=""
        )

        self.engine.create_database(self.testing_table_name,
                                   ("test_row", "INT"))

        self.assertTrue(
            self.engine.table_exists(self.testing_table_name),
            msg="Table should be in the database."
        )
    def test_cache_tablenames(self):
        """
        Test to make sure that table caching works and is complete.
        """
        self.assertTrue(
            self.testing_table_name not in self.engine.cached_tablenames,
            msg="Table should not be in cached tablenames."
        )

        self.engine.create_database(self.testing_table_name,
                                   ("test_row", "INT"))
        self.engine.cache_tablenames()

        self.assertTrue(
            self.testing_table_name in self.engine.cached_tablenames,
            msg="Table should be in cached tablenames."
        )
    def test_all_tables(self):
        """
        Test to make sure that all_tables returns all tables in the database.
        """
        self.assertTrue(
            len(self.engine.all_tables()) == 0,
            msg="There should be no tables until one is created."
        )

        self.engine.create_database(self.testing_table_name,
                                   ("test_row", "INT"))

        self.assertTrue(
            len(self.engine.all_tables()) == 1,
            msg="There should be one table in the database."
        )
    def test_append_to_pool(self):
        """
        Test to make sure that items make it to the pool when appended.
        """
        self.engine.create_database(self.testing_table_name,
                                   ("test_row", "INT"))

        self.assertTrue(
            self.engine.append_to_pool(
                {"test_row":20},
                self.testing_table_name),
            msg="append_to_pool should return True on success."
        )
        self.assertRaises(
            SQLEngine.ItemKeyReserved,
            self.engine.append_to_pool(
                {
                 "test_row":20,
                 "__table_name":"error"
                },
                self.testing_table_name
            ),
            msg="append_to_pool should raise an error, __table_name is in item."
        )
    def test_commit_to_pool(self):
        """
        Test to make sure all items in the pool are committed.
        """
        self.engine.create_database(self.testing_table_name,
                                   ("test_row", "INT"))

        self.assertTrue(
            len(self.engine.insert_pool) == 0,
            msg="Initial insert pool should have no elements."
        )

        self.engine.append_to_pool(
            {"test_row":20},
            self.testing_table_name
        )
        self.assertTrue(
            len(self.engine.insert_pool) == 1,
            msg="There should only be one element in the inser pool."
        )

        self.engine.commit_pool()

        self.assertTrue(
            len(self.engine.insert_pool) == 0,
            msg="There should be no elements in the insert pool after commit."
        )

class TestConnection(unittest.TestCase):
    """
    Test the connection used by the SQLiteEngine.
    """
    def setUp(self):
        self.connection = SQLEngine.Connection(":memory:")
        self.no_commit_connection = SQLEngine.Connection(":memory:")
        self.testing_table_name = "test_table"
    def tearDown(self):
        self.connection.close()
    def test_execute(self):
        """
        Mak sure that the execution passthrough works as expected.
        """
        self.connection.execute(
            "CREATE TABLE %s(testing_column INT);" %
            self.testing_table_name
        )
        self.connection.execute(
            "INSERT INTO %s VALUES (1);" %
            self.testing_table_name
        )
        self.assertTrue(
            len(
                self.connection.execute(
                    "SELECT * FROM %s;" %
                    self.testing_table_name
                ).fetchall()
            ) == 1,
            msg="The connection should commit immediately after execute."
        )
        self.no_commit_connection.execute(
            "INSERT INTO %s VALUES (2);" %
            self.testing_table_name
        )
        self.assertTrue(
            len(
                self.no_commit_connection.execute(
                    "SELECT * FROM %s" %
                    self.testing_table_name
                ).fetchall()
            ) == 1,
            msg="There should be no items committed by a no_commit_connection."
        )


if __name__ == "__main__":
    unittest.main()
