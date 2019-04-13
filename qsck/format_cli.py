"""Module providing the `qs-format` command-line tool."""

import bz2
import gzip

import click
import ujson

from . import serialize


@click.command()
@click.argument('input_json_path', type=click.Path(exists=True, dir_okay=False))
def qs_format(input_json_path) -> None:
    """Reads JSON file with one record per line, outputs .qs records to stdout.
    """

    if input_json_path.endswith('.json.bz2'):
        input_json_file = bz2.open(input_json_path, 'rb')
    elif input_json_path.endswith('.json.gz'):
        input_json_file = gzip.open(input_json_path, 'rb')
    elif input_json_path.endswith('.json'):
        input_json_file = open(input_json_path, 'rb')
    else:
        raise TypeError(f'Unsupported file suffix for {input_json_path}, '
                        f'must be `.json`, `.json.bz2` or `.json.gz`.')

    for qs_row in input_json_file.readlines():
        input_record = ujson.loads(qs_row)
        print(serialize(input_record[0], input_record[1], input_record[2]),
              end='')


if __name__ == '__main__':
    qs_format()
