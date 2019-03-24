"""Module providing the `qs-parse` command-line tool."""

import click
import ujson

from . import deserialize


@click.command()
@click.argument('input_qs_file', type=click.File())
def qs_parse(input_qs_file):
    """Reads ".qs" file, outputs one JSON record per input line to stdout."""

    for row in input_qs_file.readlines():
        input_record = deserialize(row)
        json_output = ujson.dumps(input_record)
        print(json_output)


if __name__ == '__main__':
    qs_parse()
