from distutils.core import setup

setup(name='Fuzzer',
      version='1.0',
      description='A pure Python fuzz testing package.',
      author='ThatITNinja',
      url='https://github.com/ThatITNinja/Fuzzer',
      packages=['fuzzer', 'fuzzer.sqliteengine'],
     )