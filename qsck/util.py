"""Misc utility functions to make serialize/deserialize work."""

from datetime import datetime, timezone


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

