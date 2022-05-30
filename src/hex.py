"""hex -- A command-line utility for manipulating hex and binary files."""

import argparse
import os
import re
import sys

from memory import FORMAT_BIN, FORMAT_IHEX, FORMAT_SREC, Memory, \
    FileContentError
from segment import Segment
from segments import Segments

__version__ = '0.1.0'
_PROGRAM = os.path.basename(sys.argv[0])
_DESCRIPTION = """
A command-line utility for manipulating hex and binary files.
"""
_EPILOG = """
"""


def main():
    """Accept command-line arguments to manipulate hex and/or binary files."""
    try:
        args = parse_cmdline()
        memory = Memory()
        read_input_files(memory, args.input, last_start=args.last_start_address)
        write_custom_data(memory, args.data, little_endian=False)
        write_custom_data(memory, args.value, little_endian=True)
        if memory.is_empty:
            print('WARNING: No input memory.', file=sys.stderr)
            print('Use "hex --help" for options.')
        else:
            fill_unused_memory(memory, args.fill)
            keep_ranges(memory, args.keep)
            remove_ranges(memory, args.remove)
            if memory.is_empty:
                print('WARNING: No output memory.', file=sys.stderr)
        write_output(memory, args.output, args.output_format, args.overwrite)
        sys.exit(0)
    except FileNotFoundError as err:
        print(f'ERROR: {err.args[1]}', file=sys.stderr)
    except FileExistsError as err:
        print(f'ERROR: {err.args[0]}', file=sys.stderr)
    except ValueError as err:
        print(f'ERROR: {err.args[0]}', file=sys.stderr)
    except FileContentError as err:
        print(f'ERROR: {str(err)}', file=sys.stderr)
    sys.exit(1)


def parse_cmdline():
    """Parse the application's command-line parameters"""
    parser = argparse.ArgumentParser(description=_DESCRIPTION, epilog=_EPILOG)
    parser.add_argument('--version',
                        action='version', version=f'{_PROGRAM} version {__version__}',
                        help='show version and exit')
    parser.add_argument('input',
                        nargs='*', metavar='infile[@ADDR]',
                        help='input file with optional relocation ADDR')
    parser.add_argument('--last-start-address',
                        action='store_true',
                        help='use start address from the last input file')
    parser.add_argument('-d', '--data',
                        nargs='+', metavar='DATA[@ADDR]', default=[],
                        help='write (big-endian) DATA at ADDR or 0')
    parser.add_argument('-v', '--value',
                        nargs='+', metavar='VAL[@ADDR]', default=[],
                        help='write (little-endian) VAL at ADDR or 0')
    parser.add_argument('-f', '--fill',
                        metavar='DATA',
                        help='fill unused memory with repeating (big-endian) DATA')
    parser.add_argument('-k', '--keep',
                        nargs='*', metavar='ADDR-ADDR', default=[],
                        help='keep data in ADDR-ADDR and discard the rest')
    parser.add_argument('-r', '--remove',
                        nargs='*', metavar='ADDR-ADDR', default=[],
                        help='remove data in ADDR-ADDR and keep the rest')
    parser.add_argument('-o', '--output',
                        metavar='outfile[@ADDR]',
                        help='the file to create with optional relocation ADDR')
    parser.add_argument('--overwrite',
                        action='store_true',
                        help='overwrite the output file if it exists')
    parser.add_argument('-B', '--binary',
                        action='store_true',
                        help='force binary output (only valid with -o option)')
    parser.add_argument('-I', '--ihex',
                        action='store_true',
                        help='force Intel Hex output')
    parser.add_argument('-S', '--srec',
                        action='store_true',
                        help='force Motorola S output')
    args = parser.parse_args()
    if args.srec:
        args.output_format = FORMAT_SREC
    elif args.ihex:
        args.output_format = FORMAT_IHEX
    elif args.binary:
        args.output_format = FORMAT_BIN
    else:
        args.output_format = ''
    return args


def read_input_files(memory: Memory, input_file_list: list, *,
                     overwrite=False, last_start=False):
    """Read input files, adjust starting address, and add to memory."""
    for input_file in input_file_list:
        try:
            # Groups:              1- -12-3-          -32
            found = re.fullmatch(r'(.+?)(@([0-9A-Fa-f]+))?', input_file.strip())
            memfile = Memory(found[1])
            if found[2]:
                address = int(found[3], base=16)
                memfile.moveto(address)
            memory.add(memfile, overwrite=overwrite, last_start=last_start)
        except FileContentError as err:
            err.filename = input_file
            raise


def write_custom_data(memory: Memory, custom_data_list: list, little_endian=False):
    """Create data segments and add to memory."""
    for custom_data in custom_data_list:
        data, addrlo = parse_data_at_addr(custom_data, little_endian=little_endian)
        segment = Segment(data, addrlo)
        memory.add(segment)


def fill_unused_memory(memory: Memory, pattern: str):
    """Fill unused memory with the fill pattern."""
    if pattern:
        data = bytes.fromhex(pattern)
        memory.segments.fill(data)


def keep_ranges(memory: Memory, ranges_list: list):
    """Keep the memory ranges -- discard the rest."""
    if ranges_list:
        keepers = Segments()
        for keep_range in ranges_list:
            addrlo, addrhi = parse_addr_range(keep_range)
            segments = memory.segments.getrange(addrlo, addrhi)
            keepers.add(segments)
        memory.segments.clear()
        memory.add(keepers)


def remove_ranges(memory: Memory, ranges_list: list):
    """Remove the memory ranges -- keep the rest."""
    for remove_range in ranges_list:
        addrlo, addrhi = parse_addr_range(remove_range)
        memory.segments.remove(addrlo, addrhi)


def parse_data_at_addr(param: str, little_endian=False) -> tuple[bytes, int]:
    """Parse a parameter with the DATA@ADDR pattern."""
    if '@' in param:
        datatext, addrtext = param.strip().split('@', 1)
    else:
        datatext = param.strip()
        addrtext = ''
    data = bytes.fromhex(datatext)
    if little_endian:
        data = data[::-1]
    if addrtext:
        addr = int(addrtext, base=16)
    else:
        addr = 0
    return data, addr


def parse_addr_range(param: str) -> tuple[int, int]:
    """Parse an address range as the addrlo and addrhi values."""
    if '-' in param:
        addrlotext, addrhitext = param.strip().split('-', 1)
    else:
        addrlotext = param.strip()
        addrhitext = addrlotext
    addrlo = int(addrlotext, base=16)
    addrhi = int(addrhitext, base=16) + 1
    return addrlo, addrhi


def write_output(memory: Memory, output_file: str, output_format='', overwrite=False):
    """Write the memory data to a file or the console."""
    if output_file:
        memory.write(output_file, output_format=output_format, overwrite=overwrite)
    elif output_format == FORMAT_SREC:
        memory.write_srec(sys.stdout)
    elif output_format == FORMAT_IHEX:
        memory.write_ihex(sys.stdout)
    else:
        memory.write_hexdump(sys.stdout)


if __name__ == '__main__':
    main()
