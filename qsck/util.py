"""Misc utility functions to make serialize/deserialize work."""

from datetime import datetime, timezone
from re import match

import ujson


def _validate_and_cast_timestamp_to_epoch_str(timestamp) -> str:

    if isinstance(timestamp, datetime):
        int_timestamp = int(timestamp.timestamp())
    elif isinstance(timestamp, str):
        try:
            int_timestamp = int(timestamp)
        except ValueError:
            raise ValueError(f'Timestamp {timestamp!r} not castable to int')
    elif isinstance(timestamp, int):
        int_timestamp = timestamp
    else:
        raise TypeError(f'Timestamp {timestamp!r} is not of supported type')

    epoch_now = datetime.utcnow().timestamp()
    delta_now_timestamp = epoch_now - int_timestamp

    assert delta_now_timestamp >= 0, (f'Timestamp is {-delta_now_timestamp} s '
                                      f'head of now')

    y2k = datetime(2000, 1, 1, 0, 0, 0, tzinfo=timezone.utc).timestamp()
    delta_y2k_timestamp = y2k - int_timestamp

    assert delta_y2k_timestamp < 0, (f'Timestamp is {delta_y2k_timestamp} s '
                                     f'before year 2000')

    return str(int_timestamp)


def _reconstruct_comma_values(input_components: list) -> list:
    inside_level2_list = False
    output_components = []
    for idx, thing in enumerate(input_components):
        if '=[' in thing and thing.count('[') > thing.count(']'):
            inside_level2_list = True
        elif inside_level2_list:
            if thing.endswith(']}') or thing.count(']') > thing.count('['):
                inside_level2_list = False

            if thing == '' or (':' not in thing and '=' not in thing):
                if match(r'[\s\w]+:.*', output_components[-1]):
                    # Squash it.
                    output_components[-1] += ',' + thing
                    continue
        else:
            if ':' not in thing and '=' not in thing:
                if match(r'[\s\w]+=.+', output_components[-1]):
                    output_components[-1] += ',' + thing
                    continue

        output_components.append(thing)

    return output_components


def _get_nested_list_pair(nested_key_value_str: str) -> (str, str):
    nested_key_value_pair = nested_key_value_str.split('=')
    if len(nested_key_value_pair) != 2:
        raise AssertionError(f"Don't know what to do with "
                             f"{nested_key_value_str!r}")
    key, value = nested_key_value_pair
    key: str = key.lstrip()

    return key, value


def _get_level2_list_pair(level2_key_value_str: str) -> (str, str):
    level2_key_value_pair = level2_key_value_str.split(':')
    if len(level2_key_value_pair) != 2:
        raise AssertionError(f"Don't know what to do with "
                             f"{level2_key_value_str!r}")
    key, value = level2_key_value_pair

    return key.lstrip(), value.lstrip()


def _reconstruct_key_value_pairs(key_value_components: list) -> list:

    parsed_components = []

    tmp_nesting_key = None
    tmp_nested_list_components, tmp_nested_dict_components = [], []
    parsing_nested_list, parsing_nested_dict = False, False

    tmp_level2_key = None
    tmp_level2_list_components = []
    parsing_level2_list = False

    for idx, thing in enumerate(key_value_components):
        try:
            if thing.count('=') == 1 and '={' not in thing \
                    and not any([parsing_nested_list, parsing_nested_dict]):
                key, value = thing.split('=')
                if value == '(null)':
                    value = None
                parsed_components.append((key, value))

            elif thing.count('={') == 1:  # Nested list or dict starting here.
                tmp_nesting_key, first_nested_pair = thing.split('={')

                if match(r'\s*[\w\d]+=.+', first_nested_pair):
                    parsing_nested_list = True

                    if first_nested_pair.count('=[') == 1:
                        # 2nd nested list starting here.
                        tmp_level2_key, first_level2_pair = \
                            first_nested_pair.lstrip().split('=[')

                        if match(r'\s*[\w\d]+:.*', first_level2_pair):
                            parsing_level2_list = True
                            key, value = _get_level2_list_pair(
                                first_level2_pair)

                            if value.endswith(']}') and \
                                    not value.count('[') == (
                                        value.count(']') + 1):
                                # Pack it up and reset local state, single-pair.
                                parsed_components.append(
                                    (tmp_nesting_key,
                                     [(tmp_level2_key, [(key, value[:-2])])])
                                )
                                parsing_level2_list = False
                                parsing_nested_list = False

                            elif value.endswith(']') and \
                                    not value.count('[') == value.count(']'):
                                tmp_nested_list_components.append(
                                    (tmp_level2_key, [(key, value[:-1])]))
                                parsing_level2_list = False

                            else:
                                # Add pair to level2 list.
                                tmp_level2_list_components.append((key, value))

                        elif first_level2_pair == ']':  # Empty nesting.
                            tmp_nested_list_components.append(
                                (tmp_level2_key, [])
                            )

                        else:
                            raise AssertionError(
                                f"Don't know what to do with first level 2 pair"
                                f" {first_level2_pair!r} in {tmp_level2_key!r}")

                    else:
                        key, value = _get_nested_list_pair(first_nested_pair)

                        if not value.endswith('}'):  # Add pair to nested list.
                            tmp_nested_list_components.append((key, value))

                        else:  # Pack it up and reset local state, single-pair.
                            parsed_components.append((tmp_nesting_key,
                                                      [(key, value[:-1])]))
                            parsing_nested_list = False

                elif match(r'".+":.+', first_nested_pair):
                    parsing_nested_dict = True
                    if not first_nested_pair.endswith('}'):
                        # Add to nested dict components.
                        tmp_nested_dict_components.append(first_nested_pair)
                    else:
                        # Pack it up and reset local state, single-pair case.
                        parsed_components.append(
                            (tmp_nesting_key, ujson.loads(
                                '{%s}' % first_nested_pair.rstrip('}')))
                        )
                        parsing_nested_dict = False

                elif first_nested_pair == '}':  # Empty nesting.
                    parsed_components.append((tmp_nesting_key, []))

                else:
                    raise AssertionError(f"L2a Don't know what to do with first"
                                         f" nested pair {first_nested_pair!r}")

            elif thing.endswith('}'):  # Nested list or dict ending here.
                last_nested_pair: str = thing.rstrip('}')

                if all([parsing_nested_list,
                        parsing_level2_list,
                        len(tmp_level2_list_components),
                        match(r'\s*[\s\w]+:.*]', last_nested_pair)]):
                    # Close level2 list and outer nested listing.
                    key, value = _get_level2_list_pair(last_nested_pair[:-1])
                    tmp_nested_list_components.append(
                        (tmp_level2_key,
                         tmp_level2_list_components + [(key, value)])
                    )
                    tmp_level2_list_components = []
                    parsing_level2_list = False

                    parsed_components.append(
                        (tmp_nesting_key,
                         tmp_nested_list_components.copy())
                    )
                    tmp_nested_list_components = []
                    parsing_nested_list = False

                elif all([parsing_nested_list, len(tmp_nested_list_components),
                          match(r'\s*[\w\d]+=.*', last_nested_pair)]):
                    # Close nested list.
                    key, value = _get_nested_list_pair(last_nested_pair)
                    parsed_components.append(
                        (tmp_nesting_key,
                         tmp_nested_list_components + [(key, value)])
                    )
                    tmp_nested_list_components = []
                    parsing_nested_list = False

                elif all([parsing_nested_dict, len(tmp_nested_dict_components),
                          match(r'\s*"\w+":.+', last_nested_pair)]):
                    # Close nested dict.
                    parsed_components.append(
                        (tmp_nesting_key, ujson.loads('{%s}' % ','.join(
                            tmp_nested_dict_components + [last_nested_pair])))
                    )
                    tmp_nested_dict_components = []
                    parsing_nested_dict = False

                else:
                    raise AssertionError(f"L2b Don't know what to do with "
                                         f"trailing {last_nested_pair!r}")

            elif parsing_nested_list:  # Add pair to nested list cmp.

                if thing.count('=[') == 1:  # 2nd nested list starting here.
                    tmp_level2_key, first_level2_pair = \
                        thing.lstrip().split('=[')

                    if match(r'\s*[\w\d]+:.*', first_level2_pair):
                        parsing_level2_list = True
                        key, value = _get_level2_list_pair(first_level2_pair)

                        if value.endswith(']') and \
                                not value.count('[') == value.count(']'):
                            # Pack it up and reset local state, single-pair.
                            tmp_nested_list_components.append(
                                (tmp_level2_key, [(key, value.rstrip(']'))]))
                            parsing_level2_list = False

                        else:
                            # Add pair to level2 list.
                            tmp_level2_list_components.append((key, value))

                    elif first_level2_pair == ']':  # Empty nesting.
                        tmp_nested_list_components.append((tmp_level2_key, []))

                    else:
                        raise AssertionError(
                            f"L3 Don't know what to do with first level 2 pair"
                            f" {first_level2_pair!r} in {tmp_level2_key!r}")

                elif parsing_level2_list:
                    key, value = _get_level2_list_pair(thing)
                    if value.endswith(']') and \
                            not value.count('[') == value.count(']'):
                        # Pack it up and reset local state.
                        tmp_nested_list_components.append(
                            (tmp_level2_key,
                             tmp_level2_list_components + [(key, value[:-1])])
                        )
                        tmp_level2_list_components = []
                        parsing_level2_list = False
                    else:
                        tmp_level2_list_components.append((key, value))

                else:
                    intermediate_nested_pair = thing

                    key, value = _get_nested_list_pair(intermediate_nested_pair)
                    tmp_nested_list_components.append((key, value))

            elif parsing_nested_dict:  # Add pair to nested list cmp.
                intermediate_nested_pair = thing
                tmp_nested_dict_components.append(intermediate_nested_pair)

            else:
                raise AssertionError(f"L2c Don't know what to do with {thing!r}")

        except Exception as parse_err:
            raise parse_err.__class__(f'L1 Error parsing {thing!r} at index '
                                      f'{idx} in {key_value_components!r} '
                                      f'({str(parse_err)}, FALLBACK)')

    return parsed_components
