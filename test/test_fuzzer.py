import fuzzer
import unittest, sqlite3, os

class TestFuzzer(unittest.TestCase):
    def setUp(self):
        self.fuzzer = fuzzer.Fuzzer(database="test_fuzzer_db.db")
        self.connection = sqlite3.connect("test_fuzzer_db.db")
    def tearDown(self):
        self.connection.close()
        os.remove("test_fuzzer_db.db")
    def test_initialize(self):
        """
        Test to make sure that database is created for the fuzzer.
        """
        self.assertTrue(
            self.fuzzer.initialize()
        )

        check_cursor = self.connection.cursor()

        self.assertTrue(
            len(
                check_cursor.execute(
                    "SELECT name FROM sqlite_master\
                     WHERE type='table';"
                ).fetchall()
            ) == 1,
            msg="The table should be created for the fuzzer."
        )
    def test_fuzz_default(self):
        """
        Test to make sure that the fuzzer works as expected (proper output).
        """
        self.fuzzer.initialize()


        for number, result in enumerate(self.fuzzer.fuzz()):
            if number >= 600:
                break
            for character in result.value:
                self.assertTrue(
                    ord(character) in range(256),
                    msg="Default parameters should return ASCII characters."
                )
    def test_fuzz_prohibited(self):
        """
        Test to make sure that no unwanted characters are included
        in the value returned.
        """
        self.fuzzer.initialize()
        prohibited = ["a", "b"]
        for number, result in enumerate(
                                   self.fuzzer.fuzz(
                                        prohibit=prohibited
                                   )
                              ):
            if number >= 600:
                break
            for character in result.value:
                self.assertTrue(
                    character not in prohibited,
                    msg="A prohibited character was in the result."
                )
    def test_fuzz_custom_evaluator(self):
        """
        Test to make sure that custom evaluators work as expected.
        """
        self.fuzzer.initialize()
        def testing_evaluator(value):
            return chr(value)
        for number, result in enumerate(
                                  self.fuzzer.fuzz(
                                       character_evaluator=testing_evaluator
                                  )
                              ):
            if number >= 600:
                break
            for character in result.value:
                self.assertTrue(
                    ord(character) in range(256),
                    msg="A custom character_evaluator should work."
                )
    def test_fuzz_random(self):
        """
        Test to make sure that generated characters are valid.
        """
        self.fuzzer.initialize()

        for number, result in enumerate(
                                  self.fuzzer.fuzz(
                                       random_generation=True
                                  )
                              ):
            if number >= 600:
                break
            for character in result.value:
                self.assertTrue(
                    ord(character) in range(256),
                    msg="Random character should be in ASCII range."
                )
    def test_fuzz_random_prohibit(self):
        """
        Test to make sure that generated characters are not in the prohibited
        list.
        """
        self.fuzzer.initialize()

        prohibited = ["a", "b"]
        for number, result in enumerate(
                                  self.fuzzer.fuzz(
                                       random_generation=True,
                                       prohibit=prohibited
                                  )
                              ):
            if number >= 600:
                break
            for character in result.value:
                self.assertTrue(
                    character not in prohibited,
                    msg="Generated characters should not be in prohibited list."
                )
    def test_tail(self):
        """
        Test to make sure that tailng from the database works.
        """
        self.fuzzer.initialize()



        for number, result in enumerate(
                                  self.fuzzer.tail()
                              )






if __name__ == '__main___':
	unittest.main()