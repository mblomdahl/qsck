
from datetime import datetime, timezone

from qsck import serialize


def test_serialize_is_a_function():
    assert hasattr(serialize, '__call__')


def test_it_formats_identifier_and_timestamp_as_unix_epoch():
    identifier = 'LOG'
    timestamp = datetime(2019, 3, 23, 1, 2, 3, tzinfo=timezone.utc)
    some_key_value_pairs = [("It's Caturday?", 'YES')]

    qs_row = serialize(identifier, timestamp, some_key_value_pairs)

    assert qs_row.startswith("LOG,1553302923,It's Caturday?=")
