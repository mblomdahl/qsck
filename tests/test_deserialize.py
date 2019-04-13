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


def test_it_returns_none_values_from_funky_null_strings():
    qs_row = 'LOG,1546902289,_app_version=(null),_model=LG-M327'

    _, __, key_value_pairs = deserialize(qs_row)

    assert key_value_pairs == [('_app_version', None), ('_model', 'LG-M327')]


def test_it_parses_nested_list_content():
    qs_row = (
        'LOG,1546902289,_model=LG-M327,'
        '0event_vars={subtype=disconnected},'
        'event1_vars={},'
        'event_vars10={batteryPc1=0.79, isCharging=false, subtype=connected, '
        'batteryTemp=310, chargeTyp3=Not_Charging},'
        'event11_data=BATTERY_CHANGED,'
        'event11_time=1546901849405,'
        'event11_vars={batteryPct=0.78, batteryTemp=308},'
        '_rx_host=ip-10-0-1-215'
    )

    _, __, key_value_pairs_run1 = deserialize(qs_row)
    _, __, key_value_pairs_run2 = deserialize(qs_row)

    for key_value_pairs in [key_value_pairs_run1, key_value_pairs_run2]:
        assert key_value_pairs == [
            ('_model', 'LG-M327'),
            ('0event_vars', [('subtype', 'disconnected')]),
            ('event1_vars', []),
            ('event_vars10', [('batteryPc1', '0.79'),
                              ('isCharging', 'false'),
                              ('subtype', 'connected'),
                              ('batteryTemp', '310'),
                              ('chargeTyp3', 'Not_Charging')]),
            ('event11_data', 'BATTERY_CHANGED'),
            ('event11_time', '1546901849405'),
            ('event11_vars', [('batteryPct', '0.78'),
                              ('batteryTemp', '308')]),
            ('_rx_host', 'ip-10-0-1-215')
        ]


def test_it_parses_nested_dict_content():
    qs_row = (
        'LOG,1546902289,user=jenkins,'
        '1nfo_healthDat4={"battery_max":0.89,"battery_max_a1":1546898400064,'
        '"battery_min":0.78,"battery_min_at":1546901880022,'
        '"time_charging":0,"time_discharging":60},'
        'info_runDat4={"app_install_time":1545251927594},'
        'time=1546902289176'
    )

    _, __, key_value_pairs_run1 = deserialize(qs_row)
    _, __, key_value_pairs_run2 = deserialize(qs_row)

    for key_value_pairs in [key_value_pairs_run1, key_value_pairs_run2]:
        assert key_value_pairs == [
            ('user', 'jenkins'),
            ('1nfo_healthDat4', {"battery_max": 0.89,
                                 "battery_max_a1": 1546898400064,
                                 "battery_min": 0.78,
                                 "battery_min_at": 1546901880022,
                                 "time_charging": 0,
                                 "time_discharging": 60}),
            ('info_runDat4', {"app_install_time": 1545251927594}),
            ('time', '1546902289176')
        ]


def test_it_parses_level2_nested_tuple_content_scenario_1():
    qs_row = (
        'LOG,1554930014,_model=SM-N960U,event6_data=connectivity,'
        'event6_time=1554907386248,event6_vars={isDocked=true, '
        'reason=radioTurnedOff, networkInfo=[type: MOBILE[LTE] - MOBILE[LTE], '
        'state: DISCONNECTED/DISCONNECTED, roaming: false], noConnect=true, '
        'networkType=0, extraInfo=},fw_inc=N960USS1ARJ9,fw_int=27'
    )

    _, __, key_value_pairs = deserialize(qs_row)

    assert key_value_pairs == [
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


def test_it_parses_level2_nested_tuple_content_scenario_2():
    qs_row = (
        'LOG,1554930014,event6_data=connect,event6_time=1554907386248,'
        'event6_vars={networkInfo=[type: MOBILE[LTE]]},fw_int=27'
    )

    _, __, key_value_pairs = deserialize(qs_row)

    assert key_value_pairs == [
        ('event6_data', 'connect'),
        ('event6_time', '1554907386248'),
        ('event6_vars', [
            ('networkInfo', [('type', 'MOBILE[LTE]')])
        ]),
        ('fw_int', '27')
    ]


def test_it_parses_level2_nested_tuple_content_scenario_3():
    qs_row = (
        'LOG,1554930014,event6_data=connect,event6_time=1554907386248,'
        'event6_vars={networkInfo=[type: MOBILE[LTE], roaming: false]}'
    )

    _, __, key_value_pairs = deserialize(qs_row)

    assert key_value_pairs == [
        ('event6_data', 'connect'),
        ('event6_time', '1554907386248'),
        ('event6_vars', [
            ('networkInfo', [('type', 'MOBILE[LTE]'), ('roaming', 'false')])
        ])
    ]


def test_it_parses_level2_nested_tuple_content_scenario_4():
    qs_row = (
        'LOG,1554930014,event6_data=connect,event6_time=1554907386248,'
        'event6_vars={networkInfo=[roaming: false, type: MOBILE[LTE], b: 3]}'
    )

    _, __, key_value_pairs = deserialize(qs_row)

    assert key_value_pairs == [
        ('event6_data', 'connect'),
        ('event6_time', '1554907386248'),
        ('event6_vars', [
            ('networkInfo', [('roaming', 'false'),
                             ('type', 'MOBILE[LTE]'),
                             ('b', '3')])
        ])
    ]


def test_it_parses_level2_nested_tuple_content_scenario_5():
    qs_row = (
        'LOG,1554930014,event6_data=connect,event6_time=1554907386248,'
        'event6_vars={networkInfo=[roaming: false, network type: 28, '
        'apn type: ims,ia,tim,]}'
    )

    _, __, key_value_pairs = deserialize(qs_row)

    assert key_value_pairs == [
        ('event6_data', 'connect'),
        ('event6_time', '1554907386248'),
        ('event6_vars', [
            ('networkInfo', [('roaming', 'false'),
                             ('network type', '28'),
                             ('apn type', 'ims,ia,tim,')])
        ])
    ]


def test_it_parses_event_data_fields_with_funky_chars_in():
    qs_row = (
        'LOG,1554930194,_model=moto z3,'
        'display=olson_vzw-userdebug 9 PDV29.178 06fda cfg,test-keys,'
        'event0_data=attract_started_intent,'
        'event33_data=Played: 92127-01.01.mp3,'
        'event33_time=1554927685047,'
        'event34_data=Stopped: Sicko Mode (Extra Clean Radio Edit) by '
        'Travis Scott Featuring Drake, Juicy J And Swae Lee,'
        'event34_time=1554927722941'
    )

    _, __, key_value_pairs = deserialize(qs_row)

    assert key_value_pairs == [
        ('_model', 'moto z3'),
        ('display', 'olson_vzw-userdebug 9 PDV29.178 06fda cfg,test-keys'),
        ('event0_data', 'attract_started_intent'),
        ('event33_data', 'Played: 92127-01.01.mp3'),
        ('event33_time', '1554927685047'),
        ('event34_data', 'Stopped: Sicko Mode (Extra Clean Radio Edit) by '
         'Travis Scott Featuring Drake, Juicy J And Swae Lee'),
        ('event34_time', '1554927722941')
    ]
