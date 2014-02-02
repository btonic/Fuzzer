#Fuzzer
Fuzzer is a simple to use Python package designed to make fuzz testing simple and fast.
##Build Status
[![Build Status](https://travis-ci.org/ThatITNinja/Fuzzer.png?branch=master)](https://travis-ci.org/ThatITNinja/Fuzzer)
======
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

We are then able to use the `.initialize()` function to actually create the database file (defaults to `fuzzerdb.db`), as well as the database table that Fuzzer will use for it's storage (optional, covered later).

If you assign the `database` parameter to another location, it will use that location. Likewise, if you assign the `table_name` parameter to another table, it will use that value.

```python
>>> fuzz_instance.initialize()
```

Running this will create the database file `fuzzerdb.db` if it does not exist, as well as create the table `attempts(month -> [00-12])(day -> [00-31])(year -> [00-99])` if that does not exist already. If the database file exists, but the table does not, the table will be created. If the table does exist, then it will simply use that.

Now we can begin generating values. To begin, we can simply use the `.fuzz()` generator supplied by `Fuzzer`. By default this will generate sequential strings of a length of 5. To generate the first 100 results, we can use:

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

However, notice how `result` in this example is not a `string`. Instead it is a `Result` instance. The result instance has the `.value` variable set to the generated string, and allows use of the `.success()` and `.fail()` functions to define the status of the attempt. These functions do not have to be used, but they provide access to `Fuzzer`'s database insertion queue.

If you decide to use `.success()` or `.fail()`, the attempt will automatically be added to an insertion pool in the SQL backend engine, awaiting insertion into the database. In order to insert all values in the pool to the database, you must call `fuzz_instance.commit_to_datbaase()`. The flow is shown below:

```
Fuzzer.fuzz -> Result -> Result.success() or Result.fail() -> Result added to insertion pool -> Fuzzer.commit_to_database() -> Results inserted into database
```

The following parameters can be altered for the `fuzz()` function for refinement of values returned.

* `random_generation` is set to either `True` or `False`. If this is true, then instead of sequential values being generated, the `random` module will be used to generate each character in the string returned.
* `prohibit` is set to a list of characters you wish to disallow in the generated values. If you wish to allow everything, this is set to `None`.
* `length` is the length of the string to be generated.
* `output_format` is the format in which you want your results. This defaults to `"{fuzzed_string}"`, however this can be changed to any string as long as `{fuzzed_string}` is present in it. This string will have the generated string formatted into it using `.format(fuzzed_string=...)` so it is required that `{fuzzed_string}` is present somewhere inside of it.
* `character_evaluator` is the function used to translate each integer value to a character. This function should recieve one value and return a string. The default function is `chr()`.
* `maximum` is the maximum value that each index can reach. The default is `255`. If you change this to be higher than `255` with other default values, this will raise an error because `chr` can only translate to ASCII values.