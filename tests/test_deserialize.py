
from qsck import deserialize


def test_deserialize_is_a_function():
    assert hasattr(deserialize, '__call__')

