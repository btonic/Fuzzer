import fuzzer.sqliteengine as SQLEngine
import random, datetime

class Fuzzer(object):
    def __init__(self, database = ":memory:", cache_tablenames = True, table_name = "attempts"):
        self.sql_engine = SQLEngine.SQLiteEngine(database, tables_to_cache = cache_tablenames)
        self.table_name = table_name
    def initialize(self):
        """
        Initialize the database, if there is not already one.
        """
        try:
            self.sql_engine.create_database(self.table_name,
                                           ("attempt_id", "INTEGER PRIMARY KEY"),
                                           ("attempted",  "TEXT"),
                                           ("prohibited", "TEXT"),
                                           ("successful", "BOOL"),
                                           ("created_at", "TEXT"),
                                           ("updated_at", "TEXT")
                                           )
        except SQLEngine.TableAlreadyExists:
            pass
        return True
    def fuzz(self, random_generation = False, prohibit = None, length = 5, output_format = "'{fuzzed_string}'"):
      prohibited_chars = False
      if prohibit != None:
          if type(prohibit) == type(list()):
              prohibited_characters = list(prohibit)
              prohibited_chars = True
          else:
              raise TypeError("List was expected for `prohibit` parameter.")
      loop_template = \
      """
      {outer_indentation}for {loop_variable} in {iterator}:
      {inner_indentation}{loop_code}
      """

      prohibit_template = \
      """
      if chr({loop_variable}) in {prohibited_list}: continue;\n
      """

      conjugation_template = \
      """
      yield {variable_conjugation}
      """

      final = ""
      indent = "    "
      if not random_generation:
          if prohibited_chars:
              for depth_level in range(length):
                  final += loop_template.format(
                           outer_indentation = indent * depth_level,
                           inner_indentation = indent * (depth_level + 1),
                           loop_variable     = "var%s" % str(depth_level),
                           iterator          = "range(0,256)",
                           loop_code         = prohibit_template.format(
                                               loop_variable   = "var%s" % str(depth_level),
                                               prohibited_list = prohibited_characters
                                               )\
                                               if depth_level != length else \
                                               \
                                               prohibit_template.format(
                                               loop_variable   = "var%s" % str(depth_level),
                                               prohibited_list = prohibited_characters
                                               ) + \
                                               conjugation_template.format(
                                               variable_conjugation = output_format.format(fuzzed_string = "+".join(list("chr(%s)" % ("var"+str(d_level)) for d_level in range(length))))
                                               )
                           )
          else:
              for depth_level in range(length):
                  final += loop_template.format(
                           outer_indentation = indent * depth_level,
                           inner_indentation = indent * (depth_level + 1),
                           loop_variable     = "var%s" % str(depth_level),
                           iterator          = "range(0,256)",
                           loop_code         = prohibit_template.format(
                                               loop_variable   = "var%s" % str(depth_level),
                                               prohibited_list = prohibited_characters
                                               )\
                                               if depth_level != length else \
                                               conjugation_template.format(
                                               variable_conjugation = output_format.format(fuzzed_string = "+".join(list("chr(%s)" % ("var"+str(d_level)) for d_level in range(length))))
                                               )
                           )
      else:
        if prohibited_chars:
            for depth_level in range(length):
                #set character to a prohibited character so that we can generate
                #a character that is not prohibited.
                char = prohibited_characters[0]
                while char in prohibited_characters:
                    char = chr(random.randrange(0,256))
                    

class Result(object):
    def __init__(self, fuzzer_instance, attempt, prohibited):
        self.engine_instance = fuzzer_instance.sql_instance
        self.table_name = fuzzer_instance.table_name
        self.attempt = attempt
        self.prohibited = prohibited
        self.success = False
    def success(self):
        self.engine_instance.append_to_pool(self._generate_item(True), self.table_name)
    def fail(self):
        self.engine_instance.append_to_pool(self._generate_item(False), self.table_name)
    def _generate_item(self, success_value):
        return {"created_at": datetime.datetime.now().strftime("%c"),
                "updated_at": datetime.datetime.now().strftime("%c"),
                "prohibited": self.prohibited,
                "attempted" : self.attempt,
                "successful": success_value}