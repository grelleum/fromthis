#!/usr/bin/env python

"""Display a subsection of input, until a matching pattern.

With no input file, or when file is -, read standard input.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import click
import signal
import sys

import fromthis


@click.command()
@click.argument('pattern')
@click.argument('filenames', nargs=-1,
                type=click.Path(exists=True, dir_okay=False))
@click.option('-F', '--fixed-string',
                    default=False, is_flag=True,
                    help='fixed string match (default is regex)')
@click.option('-i', '--ignore-case',
                    default=False, is_flag=True,
                    help='ignore case distinctions')
@click.option('-m', '--max-count',
                    default=1,
                    help='stop after number of matches.')
@click.option('-n', '--line-number',
                    default=False, is_flag=True,
                    help='print line number with output lines.')
@click.option('-x', '--exclude-match',
                    default=False, is_flag=True,
                    help='exclude matching line.')
def main(pattern, filenames, fixed_string, ignore_case,
         exclude_match, line_number, max_count):
    """Display input until a line matching PATTERN."""
    global exit_code
    exit_code = 1
    is_match = fromthis.pattern_matcher(pattern, fixed_string, ignore_case)
    lines = fromthis.text_file_input(filenames)
    if line_number:
        lines = (':'.join((str(i), l)) for i, l in enumerate(lines, 1))
    selected_lines = tothis(is_match, lines, exclude_match, max_count)
    for line in selected_lines:
        print(line)
    return exit_code


def tothis(is_match, input_stream, exclude_match, max_count):
    """Display input until a line matching PATTERN."""
    global exit_code
    for line in input_stream:
        if is_match(line, max_count):
            exit_code = 0
            if not exclude_match:
                yield line
            break
        yield line


if __name__ == '__main__':
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)  # IOError: Broken pipe
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # KeyboardInterrupt: Ctrl-C
    sys.exit(main())
