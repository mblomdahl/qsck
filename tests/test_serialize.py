
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


def test_it_formats_level2_nested_tuple_content_scenario_1():
    identifier = 'LOG'
    timestamp = '1554930014'
    key_value_pairs = [
        ('_model', 'SM-N960U'),
        ('event6_data', 'connectivity'),
        ('event6_time', '1554907386248'),
        ('event6_vars', [
            ('isDocked', 'true'),
            ('reason', 'radioTurnedOff'),
            ('networkInfo', [
                ('type', 'MOBILE[LTE] - MOBILE[LTE]'),
                ('state', 'DISCONNECTED/DISCONNECTED'),
                ('roaming', 'false')
            ]),
            ('noConnect', 'true'),
            ('networkType', '0'),
            ('extraInfo', '')
        ]),
        ('fw_inc', 'N960USS1ARJ9'),
        ('fw_int', '27')
    ]

    qs_row = serialize(identifier, timestamp, key_value_pairs)

    assert qs_row == (
        'LOG,1554930014,_model=SM-N960U,event6_data=connectivity,'
        'event6_time=1554907386248,event6_vars={isDocked=true, '
        'reason=radioTurnedOff, networkInfo=[type: MOBILE[LTE] - MOBILE[LTE], '
        'state: DISCONNECTED/DISCONNECTED, roaming: false], noConnect=true, '
        'networkType=0, extraInfo=},fw_inc=N960USS1ARJ9,fw_int=27\n'
    )


def test_it_formats_level2_nested_tuple_content_scenario_2():
    identifier = 'LOG'
    timestamp = '1554930014'
    key_value_pairs = [
        ('event6_data', 'connect'),
        ('event6_time', '1554907386248'),
        ('event6_vars', [
            ('networkInfo', [('type', 'MOBILE[LTE]')])
        ]),
        ('fw_int', '27')
    ]

    qs_row = serialize(identifier, timestamp, key_value_pairs)

    assert qs_row == (
        'LOG,1554930014,event6_data=connect,event6_time=1554907386248,'
        'event6_vars={networkInfo=[type: MOBILE[LTE]]},fw_int=27\n'
    )


def test_it_formats_level2_nested_tuple_content_scenario_3():
    identifier = 'LOG'
    timestamp = '1554930014'
    key_value_pairs = [
        ('event6_data', 'connect'),
        ('event6_time', '1554907386248'),
        ('event6_vars', [
            ('networkInfo', [('type', 'MOBILE[LTE]'), ('roaming', 'false')])
        ])
    ]

    qs_row = serialize(identifier, timestamp, key_value_pairs)

    assert qs_row == (
        'LOG,1554930014,event6_data=connect,event6_time=1554907386248,'
        'event6_vars={networkInfo=[type: MOBILE[LTE], roaming: false]}\n'
    )


def test_it_formats_level2_nested_tuple_content_scenario_4():
    identifier = 'LOG'
    timestamp = '1554930014'
    key_value_pairs = [
        ('event6_data', 'connect'),
        ('event6_time', '1554907386248'),
        ('event6_vars', [
            ('networkInfo', [('roaming', 'false'),
                             ('type', 'MOBILE[LTE]'),
                             ('b', '3')])
        ])
    ]

    qs_row = serialize(identifier, timestamp, key_value_pairs)

    assert qs_row == (
        'LOG,1554930014,event6_data=connect,event6_time=1554907386248,'
        'event6_vars={networkInfo=[roaming: false, type: MOBILE[LTE], b: 3]}\n'
    )


def test_it_formats_level2_nested_tuple_content_scenario_5():
    identifier = 'LOG'
    timestamp = '1554930014'
    key_value_pairs = [
        ('event6_data', 'connect'),
        ('event6_time', '1554907386248'),
        ('event6_vars', [
            ('networkInfo', [('roaming', 'false'),
                             ('network type', '28'),
                             ('apn type', 'ims,ia,tim,'),
                             ('subtype', '13')])
        ])
    ]

    qs_row = serialize(identifier, timestamp, key_value_pairs)

    assert qs_row == (
        'LOG,1554930014,event6_data=connect,event6_time=1554907386248,'
        'event6_vars={networkInfo=[roaming: false, network type: 28, '
        'apn type: ims,ia,tim,, subtype: 13]}\n'
    )


def test_it_formats_event_data_fields_with_funky_chars_in():
    identifier = 'LOG'
    timestamp = '1554930194'
    key_value_pairs = [
        ('_model', 'moto z3'),
        ('display', 'olson_vzw-userdebug 9 PDV29.178 06fda cfg,test-keys'),
        ('event0_data', 'attract_started_intent'),
        ('event33_data', 'Played: 92127-01.01.mp3'),
        ('event33_time', '1554927685047'),
        ('event34_data', 'Stopped: Sicko Mode (Extra Clean Radio Edit) by '
                         'Travis Scott Featuring Drake, Juicy J And Swae Lee'),
        ('event34_time', '1554927722941')
    ]

    qs_row = serialize(identifier, timestamp, key_value_pairs)

    assert qs_row == (
        'LOG,1554930194,_model=moto z3,'
        'display=olson_vzw-userdebug 9 PDV29.178 06fda cfg,test-keys,'
        'event0_data=attract_started_intent,'
        'event33_data=Played: 92127-01.01.mp3,'
        'event33_time=1554927685047,'
        'event34_data=Stopped: Sicko Mode (Extra Clean Radio Edit) by '
        'Travis Scott Featuring Drake, Juicy J And Swae Lee,'
        'event34_time=1554927722941\n'
    )
