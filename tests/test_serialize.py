
from collections import OrderedDict
from datetime import datetime, timezone

from pytest import raises

from qsck import serialize


def test_serialize_is_a_function():
    assert hasattr(serialize, '__call__')


def test_it_formats_identifier_and_timestamp_as_unix_epoch():
    identifier = 'LOG'
    some_key_value_pairs = [("It's Caturday?", 'YES')]

    dt_timestamp = datetime(2019, 3, 23, 1, 2, 3, tzinfo=timezone.utc)
    str_timestamp = "1553302923"
    int_timestamp = int(str_timestamp)

    for timestamp in (dt_timestamp, str_timestamp, int_timestamp):
        qs_row = serialize(identifier, timestamp, some_key_value_pairs)

        assert qs_row.startswith("LOG,1553302923,It's Caturday?=")


def test_it_rejects_future_and_far_past_and_mistyped_timestamps():
    identifier = 'GOL'

    far_past_timestamp = datetime(1999, 12, 31, 0, 0, 0, tzinfo=timezone.utc)
    with raises(AssertionError):
        serialize(identifier, far_past_timestamp, [])

    future_timestamp = int(datetime.utcnow().timestamp() + 30)
    with raises(AssertionError):
        serialize(identifier, future_timestamp, [])

    text_timestamp = 'First day of April, 2015'
    with raises(ValueError):
        serialize(identifier, text_timestamp, [])

    mistyped_timestamp = [2019, 1, 3, 16, 1, 30]
    with raises(TypeError):
        serialize(identifier, mistyped_timestamp, [])


def test_it_rejects_malformatted_and_mistyped_key_value_pairs():
    identifier = 'LOG'
    timestamp = datetime.utcnow()

    malformatted_key_value_pairs = [('hey', 'you'), ("i'm", "one", "too many")]

    with raises(ValueError):
        serialize(identifier, timestamp, malformatted_key_value_pairs)

    mistyped_key_value_pair = [("here's a boolean", False)]

    with raises(TypeError):
        serialize(identifier, timestamp, mistyped_key_value_pair)


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
    key_value_pairs_with_list_values = [
        ('howdy', None),
        ('empty', []),
        ('my_nest', [('sub_key1', 'foo'), ('sk2', 'bar')]),
        ('nest2', [('a', '1')]),
        ('otherStuff', 'ok')
    ]

    qs_row = serialize(identifier, timestamp, key_value_pairs_with_list_values)

    assert ',empty={},my_nest={sub_key1=foo, sk2=bar},nest2={a=1},oth' in qs_row


def test_it_does_the_nested_key_value_formatting_on_root_level_dict_values():
    identifier = 'LOG'
    timestamp = datetime.utcnow()
    key_value_pairs_with_dict_values = [
        ('howdy', None),
        ('empty', {}),
        ('nest3', OrderedDict([('k31', 2.0), ('k32', 0)])),
        ('nest4', {'y': 3, 'x': 1}),
        ('moarStuff', '!')
    ]

    qs_row = serialize(identifier, timestamp, key_value_pairs_with_dict_values)

    assert ',empty={},nest3={"k31":2.0,"k32":0},nest4={"y":3,"x":1},m' in qs_row


def test_each_output_records_ends_with_newline():
    identifier = 'FOO'
    timestamp = datetime.utcnow()
    some_key_value_pairs = [('theOnly', 'One')]

    qs_row = serialize(identifier, timestamp, some_key_value_pairs)

    assert qs_row.endswith(',theOnly=One\n')
