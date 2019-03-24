from pytest import raises

from qsck import deserialize


def test_deserialize_is_a_function():
    assert hasattr(deserialize, '__call__')


def test_it_returns_a_3tuple_with_identifier_timestamp_and_pairs_list():
    qs_row = 'LOG,1546902289,_model=LG-M327'

    identifier, timestamp, key_value_pairs = deserialize(qs_row)

    assert identifier == 'LOG'

    assert timestamp == '1546902289'

    assert key_value_pairs == [('_model', 'LG-M327')]


def test_it_rejects_malformatted_qs_row():
    qs_row = 'LOG,1546902289'

    with raises(AssertionError):
        deserialize(qs_row)


def test_it_parses_nested_list_content():
    qs_row = (
        'LOG,1546902289,_model=LG-M327,'
        'event0_vars={subtype=disconnected},'
        'event10_vars={batteryPct=0.79, isCharging=false, subtype=connected, '
        'batteryTemp=310, chargeType=Not_Charging},'
        'event11_data=BATTERY_CHANGED,'
        'event11_time=1546901849405,'
        'event11_vars={batteryPct=0.78, batteryTemp=308},'
        '_rx_host=ip-10-0-1-215'
    )

    _, __, key_value_pairs = deserialize(qs_row)

    assert key_value_pairs == [
        ('_model', 'LG-M327'),
        ("event0_vars", [("subtype", "disconnected")]),
        ("event10_vars", [("batteryPct", "0.79"),
                          ("isCharging", "false"),
                          ("subtype", "connected"),
                          ("batteryTemp", "310"),
                          ("chargeType", "Not_Charging")]),
        ("event11_data", "BATTERY_CHANGED"),
        ("event11_time", "1546901849405"),
        ("event11_vars", [("batteryPct", "0.78"),
                          ("batteryTemp", "308")]),
        ("_rx_host", "ip-10-0-1-215")
    ]
