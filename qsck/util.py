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


def _get_nested_list_pair(nested_key_value_str: str) -> (str, str):
    nested_key_value_pair = nested_key_value_str.split('=')
    if len(nested_key_value_pair) != 2:
        raise AssertionError(f"Don't know what to do with "
                             f"{nested_key_value_str!r}")
    key, value = nested_key_value_pair
    key: str = key.lstrip()

    return key, value


def _reconstruct_key_value_pairs(key_value_components: list) -> list:

    parsed_components = []

    tmp_nesting_key = None
    tmp_nested_list_components, tmp_nested_dict_components = [], []
    parsing_nested_list, parsing_nested_dict = False, False

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
                    key, value = _get_nested_list_pair(first_nested_pair)

                    if not value.endswith('}'):  # Add pair to nested list cmp.
                        tmp_nested_list_components.append((key, value))

                    else:  # Pack it up and reset local state, single-pair case.
                        parsed_components.append((tmp_nesting_key,
                                                  [(key, value.rstrip('}'))]))
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
                    raise AssertionError(f"Don't know what to do with first "
                                         f"nested pair {first_nested_pair!r}")

            elif thing.endswith('}'):  # Nested list or dict ending here.
                last_nested_pair: str = thing.rstrip('}')

                if all([parsing_nested_list, len(tmp_nested_list_components),
                        match(r'\s*[\w\d]+=.+', last_nested_pair)]):
                    key, value = _get_nested_list_pair(last_nested_pair)
                    parsed_components.append(
                        (tmp_nesting_key,
                         tmp_nested_list_components + [(key, value)])
                    )
                    tmp_nested_list_components = []
                    parsing_nested_list = False

                elif all([parsing_nested_dict, len(tmp_nested_dict_components),
                          match(r'\s*"\w+":.+', last_nested_pair)]):
                    parsed_components.append(
                        (tmp_nesting_key, ujson.loads('{%s}' % ','.join(
                            tmp_nested_dict_components + [last_nested_pair])))
                    )
                    tmp_nested_dict_components = []
                    parsing_nested_dict = False

                else:
                    raise AssertionError(f"Don't know what to do with "
                                         f"{last_nested_pair!r}")

            elif parsing_nested_list:  # Add pair to nested list cmp.
                intermediate_nested_pair = thing
                key, value = _get_nested_list_pair(intermediate_nested_pair)
                tmp_nested_list_components.append((key, value))

            elif parsing_nested_dict:  # Add pair to nested list cmp.
                intermediate_nested_pair = thing
                tmp_nested_dict_components.append(intermediate_nested_pair)

            else:
                raise AssertionError(f"Don't know what to do with {thing!r}")

        except Exception as parse_err:
            raise parse_err.__class__(f'Error parsing {thing!r} at index {idx} '
                                      f'({str(parse_err)})')

    return parsed_components
