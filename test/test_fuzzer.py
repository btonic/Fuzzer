import fuzzer
import unittest
import sqlite3
import os

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
    def test_sequential_fuzz_default(self):
        """
        Test to make sure that the fuzzer works as expected (proper output).
        """
        self.fuzzer.initialize()


        for number, result in enumerate(self.fuzzer.sequential_fuzz()):
            if number >= 600:
                break
            for character in result.value:
                self.assertTrue(
                    ord(character) in range(256),
                    msg="Default parameters should return ASCII characters."
                )
    def test_sequential_fuzz_prohibited(self):
        """
        Test to make sure that no unwanted characters are included
        in the value returned.
        """
        self.fuzzer.initialize()
        prohibited = ["a", "b"]
        for number, result in enumerate(
                                   self.fuzzer.sequential_fuzz(
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
    def test_sequential_fuzz_format(self):
        """
        Test to make sure that the output is in the required format.
        """
        self.fuzzer.initialize()
        for index, result in enumerate(
                                  self.fuzzer.sequential_fuzz(
                                       output_format="test: {fuzzed_string}"
                                  )
                              ):
            if index >= 600:
                break
            self.assertTrue(
                result.value.startswith("test:"),
                msg="result should be in the specified format."
            )
    def test_sequential_fuzz_length(self):
        """
        Test to make sure that the fuzzer is creating the proper sized string.
        """
        self.fuzzer.initialize()
        for index, result in enumerate(
                                  self.fuzzer.sequential_fuzz(
                                       length=6
                                  )
                              ):
            if index >= 600:
                break
            self.assertTrue(
                len(result.value) == 6,
                msg="result should be the specified length."
            )
    def test_sequential_fuzz_evaluator(self):
        """
        Test to make sure that custom evaluators work as expected.
        """
        self.fuzzer.initialize()
        def testing_evaluator(value):
            return chr(value)
        for number, result in enumerate(
                                  self.fuzzer.sequential_fuzz(
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
    def test_sequential_fuzz_minimum(self):
        """
        Test to make sure that the result is generated with the proper minimum
        character value.
        """
        self.fuzzer.initialize()

        for index, result in enumerate(
                                 self.fuzzer.sequential_fuzz(
                                      minimum=25
                                 )
                              ):
            if index >= 600:
                break
            for character in result.value:
                self.assertTrue(
                    ord(character) in range(25,255),
                    msg="All characters should be greater than the minimum."
                )
    def test_sequential_fuzz_maximum(self):
        """
        Test to make sure that the result is generated with the proper maximum
        character value.
        """
        self.fuzzer.initialize()

        for index, result in enumerate(
                                 self.fuzzer.sequential_fuzz(
                                      maximum=245
                                 )
                              ):
            if index >= 600:
                break
            for character in result.value:
                self.assertTrue(
                    ord(character) <= 245,
                    msg="All characters should be under the maximum value."
                )

    def test_random_fuzz(self):
        """
        Test to make sure that generated characters are valid.
        """
        self.fuzzer.initialize()

        for number, result in enumerate(
                                  self.fuzzer.random_fuzz()
                              ):
            if number >= 600:
                break
            for character in result.value:
                self.assertTrue(
                    ord(character) in range(256),
                    msg="Random character should be in ASCII range."
                )
    def test_random_fuzz_prohibit(self):
        """
        Test to make sure that generated characters are not in the prohibited
        list.
        """
        self.fuzzer.initialize()

        prohibited = ["a", "b"]
        for number, result in enumerate(
                                  self.fuzzer.random_fuzz(
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
    def test_random_fuzz_evaluator(self):
        """
        Test to make sure that the evaluator is being used.
        """
        self.fuzzer.initialize()

        for index, result in enumerate(
                                  self.fuzzer.random_fuzz(
                                       character_evaluator=chr
                                  )
                              ):
            if index >= 600:
                break
            for character in result.value:
                self.assertTrue(
                    ord(character) in range(256),
                    msg="The proper character evaluator should be used."
                )
    def test_random_fuzz_length(self):
        """
        Test to make sure that the proper length of string is generated.
        """
        self.fuzzer.initialize()

        for index, result in enumerate(
                                 self.fuzzer.random_fuzz(
                                      length=6
                                 )
                              ):
            if index >= 600:
                break
            self.assertTrue(
                len(result.value) == 6,
                msg="result should be the specified length."
            )
    def test_random_fuzz_format(self):
        """
        Test to make sure that the proper format is being used for results.
        """
        self.fuzzer.initialize()

        for index, result in enumerate(
                                 self.fuzzer.random_fuzz(
                                      output_format="test:{fuzzed_string}"
                                 )
                              ):
            if index >= 600:
                break
            self.assertTrue(
                result.value.startswith("test:"),
                msg="The result should be in the correct format."
            )
    def test_random_fuzz_minimum(self):
        """
        Test to make sure that the result is generated from the proper minimum
        value.
        """
        self.fuzzer.initialize()

        for index, result in enumerate(
                                 self.fuzzer.random_fuzz(
                                      minimum=25
                                 )
                              ):
            if index >= 600:
                break
            for character in result.value:
                self.assertTrue(
                    ord(character) >= 25 < 255,
                    msg="All characters should be greater than the minimum."
                )
    def test_random_fuzz_maximum(self):
        """
        Test to make sure that the result is generated with the proper maximum
        value.
        """
        self.fuzzer.initialize()

        for index, result in enumerate(
                                 self.fuzzer.random_fuzz(
                                      maximum=245
                                 )
                              ):
            if index >= 600:
                break
            for character in result.value:
                self.assertTrue(
                    ord(character) <= 245,
                    msg="All characters should be greater than the minimum."
                )
    @unittest.skip("TO BE DEPRECATED. DOES NOT MATCH FINAL DESIGN.")
    def test_tail(self):
        """
        Test to make sure that tailng from the database works.
        """
        self.fuzzer.initialize()

        temp = []
        for number, result in enumerate(
                                  self.fuzzer.fuzz()
                              ):
            if number >= 600:
                break
            temp.append(result.value)
            result.success()
        self.fuzzer.commit_to_database()

        for result in self.fuzzer.tail(self.fuzzer.table_name):
            self.assertTrue(
                result in temp,
                msg="The result is invalid."
            )
    @unittest.skip("TO BE DEPRECATED. DOES NOT MATCH FINAL DESIGN.")
    def test_tail_prohibited(self):
        """
        Test to make sure that tailing based on prohibited column works.
        """
        self.fuzzer.initialize()
        temp = []
        prohibited = ["a", "b"]
        for number, result in enumerate(
                                  self.fuzzer.fuzz()
                              ):
            if number >= 600:
                break
            temp.append(result.value)
            result.success()
        self.fuzzer.commit_to_database()

        for result in self.fuzzer.tail(
                           self.fuzzer.table_name,
                           prohibit=prohibited
                            ):
            self.assertTrue(
                result in temp,
                msg="The result should be present."
            )
    @unittest.skip("TO BE DEPRECATED. DOES NOT MATCH FINAL DESIGN.")
    def test_tail_used_for(self):
        """
        Test to make sure that tailing based on used_for column works.
        """
        self.fuzzer.initialize()

        temp = []
        used_for = "example"
        for number, result in enumerate(
                                  self.fuzzer.fuzz()
                              ):
            if number >= 600:
                break
            temp.append(result.value)
            result.success(used_for="example")
        self.fuzzer.commit_to_database()

        for result in self.fuzzer.tail(
                           self.fuzzer.table_name,
                           used_for=used_for
                            ):
            self.assertTrue(
                result in temp,
                msg="The result should be present."
            )
    @unittest.skip("TO BE DEPRECATED. DOES NOT MATCH FINAL DESIGN.")
    def test_tail_length(self):
        """
        Test to make sure that tailing based on length column works.
        """
        self.fuzzer.initialize()

        temp = []
        for number, result in enumerate(
                                  self.fuzzer.fuzz()
                              ):
            if number >= 600:
                break
            temp.append(result.value)
            result.success()
        self.fuzzer.commit_to_database()

        for result in self.fuzzer.tail(
                           self.fuzzer.table_name,
                           length=5
                            ):
            self.assertTrue(
                result in temp,
                msg="The result should be present."
            )
            self.assertTrue(
                len(result) == 5,
                msg="The result should be the proper length."
            )


if __name__ == '__main___':
	unittest.main()