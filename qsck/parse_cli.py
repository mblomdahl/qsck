"""Module providing the `qs-parse` command-line tool."""

import bz2
import gzip
import re
import traceback
import sys

import click
import ujson

from . import deserialize


@click.command()
@click.argument('input_qs_path', type=click.Path(exists=True, dir_okay=False))
def qs_parse(input_qs_path):
    """Reads ".qs" file, outputs one JSON record per input line to stdout."""

    if input_qs_path.endswith('.qs.bz2'):
        input_qs_file = bz2.open(input_qs_path, 'rb')
    elif input_qs_path.endswith('.qs.gz'):
        input_qs_file = gzip.open(input_qs_path, 'rb')
    elif input_qs_path.endswith('.qs'):
        input_qs_file = open(input_qs_path, 'rb')
    else:
        raise TypeError(f'Unsupported file suffix for {input_qs_path}, '
                        f'must be `.qs`, `.qs.bz2` or `.qs.gz`.')

    for idx, qs_row in enumerate(input_qs_file.readlines(), 1):
        # noinspection PyBroadException
        try:
            input_record = deserialize(qs_row.decode('utf-8'))
            json_output = ujson.dumps(input_record)
            print(re.sub(r'(\d\.\d+[1-9])0+e\+(\d+)', r'\1E\2', json_output))
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            exc_value.args = (
                (f'Error reconstructing pairs from row {idx} in '
                 f'{input_qs_path}, {qs_row!r} ({str(exc_value)})',)
            )
            print(''.join(traceback.format_exception(
                exc_type, exc_value, exc_traceback)), file=sys.stderr)


if __name__ == '__main__':
    qs_parse()
