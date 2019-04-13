"""
qsck -- The shitty ".qs" file (de-)serializer
=============================================

"""

import re
from collections import OrderedDict
from datetime import datetime

import ujson

from .util import (_validate_and_cast_timestamp_to_epoch_str,
                   _reconstruct_comma_values, _reconstruct_key_value_pairs)


def serialize(identifier: str, timestamp, key_value_pairs: []) -> str:
    """Format input parameters as a .qs-style row -- the simple part! :)"""

    components = [identifier,
                  _validate_and_cast_timestamp_to_epoch_str(timestamp)]

    for idx, pair in enumerate(key_value_pairs):
        try:
            key, value = pair
        except ValueError as unpack_err:
            raise ValueError(f'Error unpacking {pair!r} at index {idx} record '
                             f'({str(unpack_err)}')

        if isinstance(value, str):
            components.append(f'{key}={value}')
        elif value is None:
            components.append(f'{key}=(null)')
        elif isinstance(value, list):
            subcomponents = []
            for sub_key, sub_value in value:
                if not isinstance(sub_value, list):
                    subcomponents.append(f'{sub_key}={sub_value}')
                else:
                    level2_nested = ', '.join(
                        [f'{k}: {v}' for k, v in sub_value])
                    subcomponents.append(f'{sub_key}=[{level2_nested}]')
            components.append('%s={%s}' % (key, ', '.join(subcomponents)))
        elif isinstance(value, (dict, OrderedDict)):
            components.append('%s=%s' % (key, ujson.dumps(value)))
        else:
            raise TypeError(f'Unsupported data type in {pair!r}')

    str_output = ','.join(components) + '\n'
    return re.sub(r'(\d\.\d+[1-9])0+e\+(\d+)', r'\1E\2', str_output)


def deserialize(qs_row: str) -> (str, datetime, []):
    """Parse `qs_row`, return as a identifier-timestamp-key_value_pairs 3-tuple.
    """

    input_components = qs_row.rstrip().split(',')
    if len(input_components) < 3:
        raise AssertionError(f'Malformatted input row {qs_row!r}')

    identifier, timestamp = input_components[:2]

    components = _reconstruct_comma_values(input_components[2:])

    key_value_thingies = _reconstruct_key_value_pairs(components)

    return identifier, timestamp, key_value_thingies
