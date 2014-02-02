#Fuzzer
##Build Status
[![Build Status](https://travis-ci.org/ThatITNinja/Fuzzer.png?branch=master)](https://travis-ci.org/ThatITNinja/Fuzzer)
======
Fuzzer is a simple to use Python package designed to make fuzz testing simple and fast.


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
#95 more values...
```
