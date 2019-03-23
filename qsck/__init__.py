"""
qsck -- The shitty ".qs" file (de-)serializer
=============================================

"""

from datetime import datetime


def serialize(identifier: str, timestamp: datetime,
              key_value_pairs: [(str, str)]) -> str:
    """Format input parameters as a .qs-style row -- the simple part! :)"""

    pass


def deserialize(qs_row: str) -> (str, datetime, [(str, str)]):
    """Parse `qs_row`, return as a identifier-timestamp-key_value_pairs 3-tuple.
    """

    pass
