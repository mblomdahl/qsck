
qsck
====

Python library for serializing and deserializing a wonky format referred to
as ".qs" files. For full format specification, please read through
[tests.test_serialize](https://github.com/mblomdahl/qsck/blob/master/tests/test_serialize.py)
test suite and extrapolate.


Quick Start
-----------

**Use Python ≥ 3.6 only.** To install it, simply:

    pip3 install qsck


### Serializing Data

Via Python:

    python3 -c "import qsck; print(qsck.serialize('LOG', '1553302923', [
        ('first_key', 'some value'),
        ('2nd_key', [('attr1', 'foo'), ('attr2', 'bar')]),
        ('3rd_key', {'subKey1': '-3', 'subKey2': None}),
        ('4th_key', None)
    ]))"


Out comes a ".qs" record, like so:

    LOG,1553302923,first_key=some value,2nd_key={attr1=foo, attr2=bar},3rd_key={"subKey1":"-3","subKey2":null},4th_key=(null)


The library also supports serializing data by passing in a JSON file via
the command-line tool `qs-format`, one record per line:

    qs-format my-records.json > my-records.qs


## Deserializing Data

Via Python:

    python3 -c "import pprint, qsck; pprint.pprint(qsck.deserialize(
        'LOG,1553302923,first_key=some value,2nd_key={attr1=foo, \
        attr2=bar},3rd_key={\"subKey1\":\"-3\",\"subKey2\":null},4th_key=(null)'))"


Out comes a friendly Python collection:

    ('LOG',
     '1553302923',
     [('first_key', 'some value'),
      ('2nd_key', [('attr1', 'foo'), ('attr2', 'bar')]),
      ('3rd_key', {'subKey1': '-3', 'subKey2': None}),
      ('4th_key', None)])


The library-provided `qs-parse` command-line tool supports deserializing a whole
".qs" log file, emitting one JSON record per input line to stdout:

    qs-parse my-records.qs > my-records.json 


Contributing
------------

Really? Very welcome. Do the usual fork-and-submit-PR thingy.

Running the tests:

    python setup.py test


Distributing:

    pip3 install --upgrade twine wheel setuptools
    python setup.py sdist bdist_wheel
    twine upload dist/*


Changelog
---------

### `0.2` – Deserialize Added

Adds support for de-serializing ".qs" records.


### `0.1` – Initial Release

Supports serializing ".qs" records.

