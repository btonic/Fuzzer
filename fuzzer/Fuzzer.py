from types import NoneType
import fuzzer.sqlengines.sqliteengine as SQLiteEngine
import random
import datetime

class Fuzzer(object):
    """
    Fuzzer is used to either generate fuzzed values, or catch up and
    tail a previous fuzzer.

    Methods:

    public:
        __init__(self, database="fuzzerdb.db",
                 username=None, password=None,
                 cache_tablenames=True,
                 sql_engine=SQLiteEngine,
                 table_name=datetime.datetime.today().strftime(
                                                     "attempts%m%d%y"))
        initialize(self)
        commit_to_database(self)
        sequential_fuzz(self, prohibit=None, length=5,
                        output_format="{fuzzed_string}",
                        character_evaluator=chr,
                        minimum=0, maximum=255)
        random_fuzz(self, prohibit=None, length=5,
                    output_format="{fuzzed_string}",
                    character_evaluator=chr,
                    minimum=0, maximum=255)
    private:
        _increment(self, values, minimum=0,
                   maximum=255, reset=True)

    """
    def __init__(self, database="fuzzerdb.db",
                 username=None, password=None,
                 cache_tablenames=True,
                 sql_engine=SQLiteEngine,
                 table_name=datetime.datetime.today().strftime(
                                                     "attempts%m%d%y")):
        #needed so that we can catch exceptions thrown
        self.sql_engine_module = sql_engine
        #needed for persistant storage.
        self.sql_engine = sql_engine.SQLEngine(database,
                                               tables_to_cache=cache_tablenames)
        self.table_name = table_name
    def initialize(self):
        """
        Initialize the database table, if there is not already one.
        """
        try:
            self.sql_engine.create_database(
                           self.table_name,
                           ("attempt_id", "INTEGER PRIMARY KEY"),
                           ("attempted", "TEXT"),
                           ("prohibited", "TEXT"),
                           ("successful", "BOOL"),
                           ("created_at", "TEXT"),
                           ("updated_at", "TEXT")
                           )
        except self.sql_engine_module.TableAlreadyExists:
            pass
        return True
    def commit_to_database(self):
        """
        Trigger SQL engine to commit all values awaiting insertion.
        """
        self.sql_engine.commit_pool()

    def _increment(self, values, minimum=0,
                   maximum=255, reset=True):
        """
        Handles incrementation of a list in place.

        Arguments:

        values: This is the list that will be incremented. Should only
        be integers in the list.

        minimum: This is used for resetting values in the list once
        they have hit the maximum.

        maximum: This is used for determining if the list is completely
        incremented, as well as determining to reset or not.

        reset: This is used to tell the incrementor to reset a value at
        it's maximum or not.
        """
        if values[0] >= maximum:
            #first index hit its maximum, check if the rest are maxed
            done = False
            for value in values:
                if value < maximum:
                    #there is a value not maxed, incrementation continues
                    done = False
                    break
                elif value >= maximum:
                    done = True
            #all values have been maxed, finish the function
            if done:
                return True
        for index, value in enumerate(reversed(values)):
            if value >= maximum:
                if reset:
                    #reset the index and jump to next iteration
                    values[(len(values)-1)-index] = minimum
                    continue
            elif value < maximum:
                #increment, there still might be more to increment, so assume
                #not done.
                values[(len(values)-1)-index] += 1
                return False

    def sequential_fuzz(self, prohibit=None, length=5, 
                        output_format="{fuzzed_string}",
                        character_evaluator=chr,
                        minimum=0, maximum=255):
        """
        Generates all possibilities sequentially with a given length.

        Arguments:

        length: The length of the fuzzed string. Does not pertain to length
        of output_format.

        prohibit: A list of prohibited characters. Any results generated
        with a character in this list will be skipped and not returned.

        output_format: The format in which the fuzzed string sould be output.
        This requires the format variable `fuzzed_string` to be present in
        the string. The generated result will be formatted into this string
        anywhere that the `fuzzed_string` is located.

        character_evaluator: This is the function used to convert the internal
        number list into characters. This function can be replaced with any
        function that accepts one required parameter and returns one character.

        minimum: This is the minimum value of a number in the internal number
        list that will be generated. This directly translates into the lowest
        character that will be generated in the result.

        maximum: This is the maximum value of a number in the internal number
        list that will be generated. This directly translates into the highest
        character that will be generated in the result.

        """
        #make sure everything is the correct type to prevent undefined behavior
        if not isinstance(minimum, int):
            raise TypeError("`minimum` must be an integer.")
        if not isinstance(maximum, int):
            raise TypeError("`maximum` must be an integer.")
        if minimum > maximum:
            raise ValueError("`minimum` must be less than `maximum`")
        if maximum > 255 and character_evaluator == chr:
            raise TooHighForChr("`maximum` is too large for chr,\
                                 must be between 0 and 255.")
        if not isinstance(output_format, str):
            raise TypeError("output_format should be a string.")
        if not isinstance(prohibit, NoneType):
            if not isinstance(prohibit, list):
                raise TypeError("`prohibit` must be a list.")
            else:
                for value in prohibit:
                    if not isinstance(value, str):
                        raise TypeError("Values in prohibit must be a string.")
                    else:
                        if len(value) > 1:
                            raise ValueError("Values in prohibit must only be\
                                              one character long.")

        #if there are no prohibited characters, begin result generation
        if isinstance(prohibit, NoneType):
            #initialize the list with the minimum values
            temp_list = [minimum]*length
            #on every iteration, the list will be increased in place.
            #when the list can no longer be increased, iteration will stop.
            while not self._increment(temp_list,
                                      minimum=minimum, maximum=maximum):
                attempt = output_format.format(fuzzed_string="".join(
                list(character_evaluator(character) for character in temp_list))
                )
                yield Result(self, attempt, prohibited=prohibit)
        if not isinstance(prohibit, NoneType):
            #pass attempt is used as a flag to signal the yielding of a result.
            #if there is a prohibited character, it is set to true and the
            #result is skipped.
            pass_attempt = False
            #initialize the list with the minimum values
            temp_list = [minimum]*length
            #increase list values on every iteration.
            while not self._increment(temp_list,
                                      minimum=minimum, maximum=maximum):
                attempt = output_format.format(fuzzed_string="".join(
                list(character_evaluator(character) for character in temp_list))
                )
                #make sure that there is no prohibited character in the yielded
                #attempt
                for character in attempt:
                    if character in prohibit:
                        pass_attempt = True
                #if there is a prohibited character, skip the result and
                #continue iteration.
                if pass_attempt:
                    pass_attempt = False
                    continue
                else:
                    yield Result(self, attempt, prohibited=prohibit)

    def random_fuzz(self, prohibit=None, length=5, 
                    output_format="{fuzzed_string}",
                    character_evaluator=chr,
                    minimum=0, maximum=255):
        """
        Generates all possibilities randomly with a given length.

        Arguments:

        length: The length of the fuzzed string. Does not pertain to length
        of output_format.

        prohibit: A list of prohibited characters. Any results generated
        with a character in this list will be skipped and not returned.

        output_format: The format in which the fuzzed string sould be output.
        This requires the format variable `fuzzed_string` to be present in
        the string. The generated result will be formatted into this string
        anywhere that the `fuzzed_string` is located.

        character_evaluator: This is the function used to convert the internal
        number list into characters. This function can be replaced with any
        function that accepts one required parameter and returns one character.

        minimum: This is the minimum value of a number in the internal number
        list that will be generated. This directly translates into the lowest
        character that will be generated in the result. No character below
        this will be present in the output, despite it being randomly generated.
        (uses random.randrange())

        maximum: This is the maximum value of a number in the internal number
        list that will be generated. This directly translates into the highest
        character that will be generated in the result. No character higher
        than this will be present in the output, despite it being randomly
        generated.
        (uses random.randrange())
        """
        #make sure everything is the correct type to prevent undefined behavior
        if not isinstance(minimum, int):
            raise TypeError("`minimum` must be an integer.")
        if not isinstance(maximum, int):
            raise TypeError("`maximum` must be an integer.")
        if minimum > maximum:
            raise ValueError("`minimum` must be less than `maximum`.")
        if maximum > 255 and character_evaluator == chr:
            raise TooHighForChr("`maximum` is too large for chr,\
                                 must be between 0 and 255.")
        if not isinstance(prohibit, NoneType):
            if not isinstance(prohibit, list):
                raise TypeError("`prohibit` must be a list.")
            else:
                for value in prohibit:
                    if not isinstance(value, str):
                        raise TypeError("Values in prohibit must be a string.")
                    else:
                        if len(value) > 1:
                            raise ValueError("Values in prohibit must only be\
                                              one character long.")
        if not isinstance(output_format, str):
            raise TypeError("output_format should be a string.")

        if isinstance(prohibit, NoneType):
            while True:
                attempt = output_format.format(fuzzed_string="".join(
                #run the character evaluator on a random number between the
                #minimum and maximum for the length of the result specified
                list(character_evaluator(random.randrange(minimum, maximum))
                     for index in range(length))
                ))
                yield Result(self, attempt, prohibited=prohibit)
        if not isinstance(prohibit, NoneType):
            while True:
                #populate the list. each character will be replaced with
                #a randomly generated value between the minimum and maximum
                temp_list = [minimum]*length
                for index in range(length):
                    #done is used to define the status of the character
                    #generated. a character is done if it is not in the
                    #prohibited characters.
                    done = False
                    while not done:
                        #choose a random value between the minimum and maximum
                        char_value_attempt = random.randrange(minimum, maximum)
                        #test to make sure that it is not in the prohibited
                        #characters. if it is, choose another random value and
                        #try again.
                        if character_evaluator(char_value_attempt) in prohibit:
                            continue
                        else:
                            #the character is ok, assign the value in the temp
                            #list to the value and signify done to continue to
                            #next index.
                            temp_list[index] = char_value_attempt
                            done = True
                #all values in the temp list have been generated.
                #turn all the temp list into a string and yield it.
                attempt = "".join(
                list(character_evaluator(value) for value in temp_list
                ))
                yield Result(self, attempt, prohibited=prohibit)

    def tail(self, table_name, select_conditions={},
             order_by="created_at DESC"):
        """
        Iterate through a table in a given database. Once completed, watches
        that table for newly added rows.

        Arguments:

        table_name: The table to iterate through and watch.

        select_conditions: The conditions that will filter which results
        are returned.

        order_by: This is how the iterated results will be ordered. Once
        all values have been iterated, this order is no longer followed.
        Instead, the newest rows in the table are returned.
        """
        #make sure everything is the correct type to prevent undefined behavior
        if not isinstance(select_conditions, dict):
            raise TypeError("select_conditions must be a dict.")
        if not isinstance(order_by, str):
            raise TypeError("order_by must be a string.")

        #initiate the query
        query = "SELECT * FROM {table_name}".format(
                    table_name=table_name
                )
        #first_iteration is used to structure the SQL properly.
        #it is needed so that the where condition is placed
        #before any conditions conjugated by `AND`. if there
        #are no values in the select_conditions, none of this runs.
        first_iteration = True
        for keyword, condition in select_conditions.iteritems():
            if not isinstance(condition, NoneType)\
               and not isinstance(keyword, NoneType)\
               and not keyword == "":
                if first_iteration:
                    #initialize the conditions
                    query += " WHERE {keyword} = {condition}".format(
                            keyword=keyword,
                            #use repr so that strings are handled properly
                            condition=repr(condition)\
                                      if isinstance(condition, str)\
                                      else condition
                        )
                    first_iteration = False
                else:
                    #added to original conditions
                    query += " AND {keyword} = {condition}".format(
                            keyword=keyword,
                            #use repr so that strings are handled properly
                            condition=repr(condition)\
                                      if isinstance(condition, str)\
                                      else condition
                        )
        #order_set flag is used later when stripping the queries
        order_set = False
        if order_by == "":
            #end of query
            query += ";"
        else:
            #ordering of query
            order_set = True
            query_without_order = query
            query += " ORDER BY {order_by};".format(
                    order_by=order_by
                )
        #set as none so that it can be assigned upon iteration later.
        #it is used 
        last_result = None
        tail_from_id = False
        limit_by = " LIMIT 1;"
        while True:
            #after all values have been iterated currently in database,
            #this waits and watches the DB for any new rows added.
            if tail_from_id:
                if order_set:
                    #override the order, order by when it was created to
                    #grab latest entry
                    query = query_without_order + " ORDER BY attempt_id DESC"
                else:
                    #add our order to the query, there isnt one already
                    query = query.rstrip(";") + " ORDER BY attempt_id DESC"
                while True:
                    #convert out of a generator and pull the result.
                    #limited to 1.
                    result = list(
                                self.sql_engine.read_query(query + limit_by)
                             )[0]
                    #make sure that we arent comparing None to a DB result
                    if isinstance(last_result, NoneType):
                        last_result = result
                    else:
                        #skip yield if the result is the same as the previous one
                        if last_result == result:
                            pass
                        else:
                            #get the difference bteween the last result id
                            #and the current result id so that we can limit
                            #it by that many results (only newly added results)
                            limit_by = " LIMIT %s;" %\
                                       (last_result[0] - result[0])
                            last_result = result
                            yield Result(self, result[1], prohibited=result[2])
            else:
                for result in self.sql_engine.read_query(query):
                    last_result = result
                    yield Result(self, result[1], prohibited=result[2])
                #done iterating values at time of query. jump to watching db
                #starting from the last result's id
                tail_from_id = True



class Result(object):
    """
    Used to determine success or failure of an attempt, then submit value into
    engine insertion queue.
    """
    def __init__(self, fuzzer_instance, attempt, prohibited=None):
        #pull the fuzzer instances sql_engine so that we can append
        #values to it's pool
        self.engine_instance = fuzzer_instance.sql_engine
        self.table_name = fuzzer_instance.table_name
        self.value = attempt
        self.prohibited = prohibited
    def success(self):
        """
        Register with the SQL engine that the result should be entered as a
        success.
        """
        self.engine_instance.append_to_pool(self._generate_item(True),
                                            self.table_name)
    def fail(self):
        """
        Register with the SQL engine that the result should be entered as a
        failure.
        """
        self.engine_instance.append_to_pool(self._generate_item(False),
                                            self.table_name)
    def _generate_item(self, success_value):
        """
        Create the item to submit to the SQL engine.

        Arguments:

        success_value: Used as a flag for the result to define success
        or failure.
        """
        return {"created_at": datetime.datetime.now().strftime("%c"),
                "updated_at": datetime.datetime.now().strftime("%c"),
                "prohibited": "" if isinstance(self.prohibited, NoneType) \
                                 else self.prohibited,
                "attempted" : self.value,
                "successful": success_value}

class GeneralException(Exception):
    """
    Baseclass for all exceptions raised by Fuzzer.
    """
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return str(self.message)
    def __repr__(self):
        return repr(self.message)

class TooHighForChr(GeneralException):
    """
    Raised to handle a value being too large for `chr`.
    """
    pass
class MaximumIncrementReached(GeneralException):
    """
    Raised to alert that all elements of the list have reached their maximum.
    """
    pass
