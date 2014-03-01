#Fuzzer
Fuzzer is a Python package designed to make fuzz testing simple and fast.
##Build Status [![Build Status](https://travis-ci.org/ThatITNinja/Fuzzer.png?branch=master)](https://travis-ci.org/ThatITNinja/Fuzzer)

Installation
======
To install Fuzzer, run:

```bash
git clone git@github.com:ThatITNinja/Fuzzer.git
python setup.py install
```


Then to make sure that it is installed(and importable), run:

```python
>>> import fuzzer
>>>
```


Usage
======
For the most part, Fuzzer is pretty smart. To begin using it, you must first import it.

```python
>>> import fuzzer
```

Now you can begin using all that Fuzzer has to offer. Lets start off with creating a database. To do this, we initialize a `Fuzzer` instance.

```python
>>> fuzz_instance = fuzzer.Fuzzer()
```

We can then use the `.initialize()` function to actually create the database file (defaults to `fuzzerdb.db`), as well as the database table that `Fuzzer` will use for it's storage (optional, covered later).

If you assign the `database` parameter to another location, it will use that location. Likewise, if you assign the `table_name` parameter to another table, it will use that value.

```python
>>> fuzz_instance.initialize()
```

Running this will create the database file specified in the initialization of the `Fuzzer` instance if it does not exist, as well as create the table if that does not exist already. If the database file exists, but the table does not, the table will be created. If the table does exist, then it will simply use that.

Now we can begin generating values. To begin, we can simply use the `.sequential_fuzz()` generator supplied by `Fuzzer`. By default this will generate sequential strings of a length of 5. To generate the first 100 results, we can use:

```python
>>> for index, result in enumerate(fuzz_instance.fuzz()):
...     if index == 100:
...         break
...     print repr(result.value)
...
'\x00\x00\x00\x00\x00'
'\x00\x00\x00\x00\x01'
'\x00\x00\x00\x00\x02'
'\x00\x00\x00\x00\x03'
'\x00\x00\x00\x00\x04'
#more values...
```

However, notice how `result` in this example is not a `string`. Instead it is a `Result` instance. The `Result` instance has the `.value` variable set to the generated string, and allows use of the `.success()` and `.fail()` functions to define the status of the attempt. These functions do not have to be used, but they provide access to `Fuzzer`'s database insertion queue.

If you decide to use `.success()` or `.fail()`, the attempt will automatically be added to an insertion pool in the SQL backend engine, awaiting insertion into the database. In order to insert all values in the pool to the database, you must call `fuzz_instance.commit_to_datbaase()`. The flow is shown below:

```
Fuzzer.fuzz -> Result -> Result.success() or Result.fail() -> Result added to insertion pool -> Fuzzer.commit_to_database() -> Results inserted into database
```

The following parameters can be passed to the `sequential_fuzz()` function for refinement of generated results.

* `prohibit`: This is a list of strings (only one character long each) that will not be allowed in the generated value. If a character in prohibit is found in the generated value, then the value will not be yielded, and it will be skipped.
* `length`: This is how long the generated value should be.
* `output_format`: This is how the fuzzer should yield the value. This is formatted with `.format()` so anywhere in the format that you wish to have the value, simply use `{fuzzed_string}`.
* `character_evaluator`: This is the function that the fuzzer uses to convert the internal number to a string value. If you wish to define your own, it must accept only one required parameter, and return only one character.
* `minimum`: This is the minimum value for the fuzzer. This means, if you start with a `minimum` of `5` and a `length` of `2`, then you will begin with `[2,2]` and it will continue up to the maximum, then reset to the minimum once carrying is completed: `[2,3],[2,4]...[2,maximum],[3,2]...`.
* `maximum`: This is the maximum value for the fuzzer. If any value in the fuzzer reaches this, it will be reset to the `minimum` value.


Now, what if you want to randomly generate these values instead of generating them sequentially? Well, `.random_fuzz()` has you covered. It works exactly like `.sequential_fuzz()`, except for a slight difference in some of its parameters meanings:

* `minimum`: This is the minimum value possible to show up in the result. Nothing lower will be generated.
* `maximum`: This is the maximum value possible to show up in the result. Nothing higher will be generated.

Now that we can generate the values, define if they can work or not, why do we store them in a database? Well, so that we can use it later, or use it asynchrously. If you store the generated values in the database (using `.success()` or `.fail()`), we can use the function `.tail()` to iterate and watch a specific table in the database. This works by ordering the database, then iterating through the present rows and yielding them as a `Result` object. You can then use the `.success()` and `.fail()` functions appropriately. However, once all the rows have been iterated, the `.tail()` function will continue to watch the database and yield any new values added to the database (returned as a `Result` object). The `.tail()` function accepts the following parameters:

* `table_name`: This is the table to iterate and follow.
* `select_conditions`: This is what you will use to filter the values returned. For example, if you want all successful attempts, you would use `select_conditions={"successful":"True"}`.
* `order_by`: This is how you wish to order the iteration of values. This *DOES NOT* apply to watching the database, it only applies to the iteration of existing values.


##Thread Safety
All of the functions available through a `Fuzzer` instance are thread safe. For instance, you can use `fuzz_obj.sequential_fuzz()` in one thread, and `fuzz_obj.tail(...)` in another thread and not have to worry about resource management.
