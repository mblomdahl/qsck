"""Module providing the `qs-format` command-line tool."""

import click
import ujson

from . import serialize


@click.command()
@click.argument('input_json_file', type=click.File())
def qs_format(input_json_file):
    """Reads JSON file with one record per line, outputs .qs records to stdout.
    """

    for row in input_json_file.readlines():
        input_record = ujson.loads(row)
        print(serialize(input_record[0], input_record[1], input_record[2]),
              end='')


if __name__ == '__main__':
    qs_format()
