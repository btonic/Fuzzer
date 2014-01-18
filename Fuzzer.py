import sqliteengine as SQLEngine
import random

class Fuzzer(object):
    def __init__(self, database = ":memory:", cache_tablenames = True):
        self.sql_engine = SQLEngine.SQLiteEngine(database, cache_tablenames = cache_tablenames)

    def initialize(self):
        """
        Initialize the database, if there is not already one.
        """
        try:
            self.sql_engine.create_database("attempts",
                                           ("attempt_id","INTEGER PRIMARY KEY"),
                                           ("attempted", "TEXT"),
                                           ("prohibited","TEXT"),
                                           ("successful","BOOL"),
                                           ("created_at","TEXT")
                                           )
        except TableAlreadyExists:
            pass
        return True
    def fuzz(self, random = False, prohibit = None, length = 5, output_format = "{fuzzed_string}"):
      prohibited_chars = False
      if prohibit != None:
        if type(prohibit) == type(list()):
          prohibited_characters = list(prohibit)
          prohibited_chars = True
        else:
          raise TypeError("List was expected for `prohibit` parameter.")
      loop_template = 
      """\
      {outer_indentation}for {loop_variable} in {iterator}:
      {inner_indentation}{loop_code}
      """

      prohibit_template =
      """\
      if {loop_variable} in {prohibited_list}: continue;\n
      """

      conjugation_template =
      """\
      self.sql_engine.append_to_pool({item}, {table_name})
      yield {variable_conjugation}
      """

      final = ""
      indent = "    "
      if not random:
          if prohibited_chars:
              for depth_level in range(length):
                  final += loop_template.format(
                           outer_indentation = indent * depth_level,
                           inner_indentation = indent * (depth_level + 1),
                           loop_variable     = "var%s" % str(depth_level),
                           iterator          = "range(0,256)"
                           loop_code         = prohibit_template.format(
                                               loop_variable =   "var%s" % str(depth_level),
                                               prohibited_list = prohibited_characters
                                               )\
                                               if depth_level != length else \
                                               \
                                               prohibit_template.format(
                                               loop_variable =   "var%s" % str(depth_level),
                                               prohibited_list = prohibited_characters
                                               ) + \
                                               conjugation_template.format(
                                               variable_conjugation = output_format.format(fuzzed_string = "+".join(list("chr(%s)" % ("var"+str(d_level)) for d_level in range(length) )))
                                               )


                           )
      else:
        #impliment random code



