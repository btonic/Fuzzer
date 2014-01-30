import fuzzer
import unittest

class TestFuzzer(unittest.TestCase):
    def setUp(self):
    	self.fuzzer=fuzzer.Fuzzer()
    def tearDown(self):
    	self.fuzzer.stop()
    def test_initialize(self):
        """
        Test to make sure that database is created for the fuzzer.
        """
    	self.assertTrue(
            self.fuzzer.initialize()
        )

        check_cursor = self.fuzzer.sql_engine.cursor

        self.assertTrue(
            len(
                check_cursor.execute(
                    "SELECT * from %s;" %
                    self.fuzzer.table_name
                ).fetchall()
            ) == 1,
            msg="The table should be created for the fuzzer."
        )
    def test_fuzz(self):
        """
        Test to make sure that the fuzzer works as expected (proper output).
        """
    	self.fuzzer.initialize()


        for number, result in enumerate(self.fuzzer.fuzz()):
            if number >= 600:
                self.fuzzer.stop()
                break
            for character in result.value:
                self.assertTrue(
                    ord(character) <= 256,
                    msg="Default fuzzer settings should only return ASCII values."
                )

        prohibited = ["a", "b"]
        for number, result in enumerate(
                                   self.fuzzer.fuzz(
                                        prohibit=prohibited
                                   )
                              )
            for character in restult.value:
                self.assertTrue(
                    character not in prohibited,
                    msg="A character in the result was not supposed to be present."
                )





if __name__ == '__main___':
	unittest.main()