#!/usr/bin/env python

"""Display a subsection of input, starting with a matching pattern.

With no input file, or when file is -, read standard input.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import click
import gzip
import bz2
import re
import signal
import sys


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
                    help='start after number of matches.')
@click.option('-n', '--line-number',
                    default=False, is_flag=True,
                    help='print line number with output lines.')
@click.option('-x', '--exclude-match',
                    default=False, is_flag=True,
                    help='exclude matching line.')
def main(pattern, filenames, fixed_string, ignore_case,
         exclude_match, line_number, max_count):
    """Display input starting with a line matching PATTERN."""
    global exit_code
    exit_code = 1
    is_match = pattern_matcher(pattern, fixed_string, ignore_case)
    lines = text_file_input(filenames)
    if line_number:
        lines = (':'.join((str(i), l)) for i, l in enumerate(lines, 1))
    selected_lines = fromthis(is_match, lines, exclude_match, max_count)
    for line in selected_lines:
        print(line)
    return exit_code


def fromthis(is_match, input_stream, exclude_match, max_count):
    """Display input starting with a matching pattern."""
    global exit_code
    for line in input_stream:
        if is_match(line, max_count):
            exit_code = 0
            if not exclude_match:
                yield line
            break
    for line in input_stream:
        yield line


def count_matches(match_function):
    """Return True only if the required number of matches is reached."""
    def counter(line, max_count, persistent={'count': 0}):
        result = match_function(line)
        if result:
            persistent['count'] += 1
        return True if persistent['count'] == max_count else False
    return counter


def pattern_matcher(pattern, fixed_string, ignore_case):
    """Return a custom function for pattern matching."""
    regex_flags = re.IGNORECASE if ignore_case else 0

    @count_matches
    def match_regex(line, regex=re.compile(pattern, regex_flags)):
        return bool(regex.search(line))

    @count_matches
    def match_fixed_string_ignore_case(line, pattern=pattern):
        return pattern.upper() in line.upper()

    @count_matches
    def match_fixed_string_match_case(line, pattern=pattern):
        return pattern in line

    if not fixed_string:
        match_function = match_regex
    elif ignore_case:
        match_function = match_fixed_string_ignore_case
    else:
        match_function = match_fixed_string_match_case
    return match_function


def text_file_input(filenames):
    """Generate input from files or standard input."""
    if filenames:
        file_handles = open_files(filenames)
    else:
        file_handles = (iter(sys.stdin.readline, ''), )
    for file_handle in file_handles:
        for line in file_handle:
            yield line.rstrip()


def open_files(filenames):
    """Return a filehandle for each provided filename."""
    for filename in filenames:
        file_open = file_opener(filename)
        with file_open(filename, 'rt') as filehandle:
            yield filehandle


def file_opener(filename):
    """Return a file open function based on file extension."""
    if filename.endswith('.gz'):
        return gzip.open
    if filename.endswith('.bz2'):
        return bz2.open
    else:
        return open


if __name__ == '__main__':
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)  # IOError: Broken pipe
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # KeyboardInterrupt: Ctrl-C
    sys.exit(main())
