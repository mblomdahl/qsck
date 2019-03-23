
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


def test_it_formats_null_values_as_funky_strings():
    identifier = 'LOG'
    timestamp = datetime.utcnow()
    key_value_pairs_with_none_values = [
        ('good_ideas', None), ('bad ideas', 'plenty'), ('newType', None)]

    qs_row = serialize(identifier, timestamp, key_value_pairs_with_none_values)

    assert ',good_ideas=(null),bad ideas=plenty,newType=(null)' in qs_row


def test_it_does_the_nested_key_value_formatting_on_root_level_list_values():
    identifier = 'LOG'
    timestamp = datetime.utcnow()
    key_value_pairs_with_none_values = [
        ('howdy', None),
        ('my_nest', [('sub_key1', 'foo'), ('sk2', 'bar')]),
        ('nest2', [('a', '1')]),
        ('otherStuff', 'ok')
    ]

    qs_row = serialize(identifier, timestamp, key_value_pairs_with_none_values)

    assert ',my_nest={sub_key1=foo, sk2=bar},nest2={a=1},otherStuff=' in qs_row
