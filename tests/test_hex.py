"""Unit tests for the Hex application."""

import filecmp
import os

from run_application import RunApplication

from hex import __version__

_EXTENSIONS_BIN = ['bin']
_EXTENSIONS_IHEX = ['hex', 'pc8']
_EXTENSIONS_SREC_16 = ['s1', 's19']
_EXTENSIONS_SREC_24 = ['s2', 's28']
_EXTENSIONS_SREC = ['s', 's3', 's37']


def create_file(filename):
    """Create an empty file with the specified filename."""
    if os.path.isfile(filename):
        return
    with open(filename, 'w', encoding='utf-8'):
        pass


class Test0CommandLine():
    """Unit tests focused on handling of command-line argument options."""

    @staticmethod
    def test_no_arguments(app: RunApplication):
        """Hex without command-line arguments should show how to get help information."""
        app.run()
        assert app.stdout == ''
        assert app.stderr == 'WARNING: No input memory -- use "hex --help" for options'
        assert app.returncode == 0

    @staticmethod
    def test_help(app: RunApplication, opt_help):
        """Hex help option should show help text."""
        app.run(opt_help)
        assert app.stdoutlines == [
            'usage: hex.py [-h] [--version] [-a] [-d] [-f DATA] [-k [ADDR-ADDR ...]]',
            '              [-r [ADDR-ADDR ...]] [-v VAL[@ADDR] [VAL[@ADDR] ...]]',
            '              [-w DATA[@ADDR] [DATA[@ADDR] ...]] [-l MB] [-o outfile[@ADDR]]',
            '              [--overwrite] [-B] [-I] [-S] [-c]',
            '              [infile[@ADDR] ...]',
            '',
            'A command-line utility for manipulating hex and binary files.',
            '',
            'positional arguments:',
            '  infile[@ADDR]         input file with optional relocation ADDR',
            '',
            'options:',
            '  -h, --help            show this help message and exit',
            '  --version             show version and exit',
            '  -a, --overwrite-start-address',
            '                        use start address from the last input file',
            '  -d, --overwrite-data  allow newer overlapping data to overwrite older data',
            '  -f DATA, --fill DATA  fill unused memory with repeating (big-endian) DATA',
            '  -k [ADDR-ADDR ...], --keep [ADDR-ADDR ...]',
            '                        keep data in ADDR-ADDR and discard the rest',
            '  -r [ADDR-ADDR ...], --remove [ADDR-ADDR ...]',
            '                        remove data in ADDR-ADDR and keep the rest',
            '  -v VAL[@ADDR] [VAL[@ADDR] ...], --write-value VAL[@ADDR] [VAL[@ADDR] ...]',
            '                        write (little-endian) VAL at ADDR or 0',
            '  -w DATA[@ADDR] [DATA[@ADDR] ...], --write-data DATA[@ADDR] [DATA[@ADDR] ...]',
            '                        write (big-endian) DATA at ADDR or 0',
            '  -l MB, --limit MB     set memory range limit in Megabytes (default 32 MB)',
            '  -o outfile[@ADDR], --output outfile[@ADDR]',
            '                        the file to create with optional relocation ADDR',
            '  --overwrite           overwrite the output file if it exists',
            '  -B, --binary          force binary output (with -o option only)',
            '  -I, --ihex            force Intel Hex output',
            '  -S, --srec            force Motorola S output',
            '  -c, --record-count    generate a record count (Motorola S output only)',
        ]
        assert app.stderr == ''
        assert app.returncode == 0

    @staticmethod
    def test_version(app: RunApplication):
        """Hex version option should show version of hex."""
        app.run('--version')
        assert app.stdout == f'hex.py version {__version__}'
        assert app.stderr == ''
        assert app.returncode == 0


class Test0ReadInputFiles():
    """Unit tests focused on reading input files."""

    @staticmethod
    def test_missing_input_file(app: RunApplication):
        """Hex should generate an error message if a specified input does not exist."""
        app.run('tests/files/missing.s19')
        assert app.stdout == ''
        assert app.stderr == 'ERROR: No such file or directory: "tests/files/missing.s19"'
        assert app.returncode == 1

    @staticmethod
    def test_read_srec16(app: RunApplication):
        """Hex should read a file with SREC16 format."""
        app.run('tests/files/alphabet.s19')
        assert app.stdoutlines == [
            '00000300  41 42 43 44 45 46 47 48  49 4a 4b 4c 4d 4e 4f 50  |ABCDEFGHIJKLMNOP|',
            '00000310  51 52 53 54 55 56 57 58  59 5a                    |QRSTUVWXYZ|',
            '00008000  61 62 63 64 65 66 67 68  69 6a 6b 6c 6d 6e 6f 70  |abcdefghijklmnop|',
            '00008010  71 72 73 74 75 76 77 78  79 7a                    |qrstuvwxyz|'
        ]
        assert app.stderr == ''
        assert app.returncode == 0

    @staticmethod
    def test_read_srec24(app: RunApplication):
        """Hex should read a file with SREC24 format."""
        app.run('tests/files/alphabet.s28')
        assert app.stdoutlines == [
            '00000200  41 42 43 44 45 46 47 48  49 4a 4b 4c 4d 4e 4f 50  |ABCDEFGHIJKLMNOP|',
            '00000210  51 52 53 54 55 56 57 58  59 5a                    |QRSTUVWXYZ|',
            '000f0000  61 62 63 64 65 66 67 68  69 6a 6b 6c 6d 6e 6f 70  |abcdefghijklmnop|',
            '000f0010  71 72 73 74 75 76 77 78  79 7a                    |qrstuvwxyz|'
        ]
        assert app.stderr == ''
        assert app.returncode == 0

    @staticmethod
    def test_read_srec32(app: RunApplication):
        """Hex should read a file with SREC32 format."""
        app.run('tests/files/alphabet.s37')
        assert app.stdoutlines == [
            '00000100  41 42 43 44 45 46 47 48  49 4a 4b 4c 4d 4e 4f 50  |ABCDEFGHIJKLMNOP|',
            '00000110  51 52 53 54 55 56 57 58  59 5a                    |QRSTUVWXYZ|',
            '01f00000  61 62 63 64 65 66 67 68  69 6a 6b 6c 6d 6e 6f 70  |abcdefghijklmnop|',
            '01f00010  71 72 73 74 75 76 77 78  79 7a                    |qrstuvwxyz|'
        ]
        assert app.stderr == ''
        assert app.returncode == 0

    @staticmethod
    def test_read_srec32_overlap_same(app: RunApplication):
        """Hex should ignore overlapping data that is the same as existing data."""
        app.run('tests/files/alphabet.s37', 'tests/files/alpha-overlap-same.s37')
        assert app.stdoutlines == [
            '00000100  41 42 43 44 45 46 47 48  49 4a 4b 4c 4d 4e 4f 50  |ABCDEFGHIJKLMNOP|',
            '00000110  51 52 53 54 55 56 57 58  59 5a                    |QRSTUVWXYZ|',
            '01f00000  61 62 63 64 65 66 67 68  69 6a 6b 6c 6d 6e 6f 70  |abcdefghijklmnop|',
            '01f00010  71 72 73 74 75 76 77 78  79 7a                    |qrstuvwxyz|'
        ]
        assert app.stderr == ''
        assert app.returncode == 0

    @staticmethod
    def test_read_srec32_overlap_diff_error(app: RunApplication):
        """Hex should fail on overlapping data that is different from existing data."""
        app.run('tests/files/alphabet.s37', 'tests/files/alpha-overlap-diff.s37')
        assert app.stdout == ''
        assert app.stderrlines == [
            'ERROR: In file "tests/files/alpha-overlap-diff.s37"',
            '       The data at 0x108 (0x31) conflicts with previously defined data (0x49)',
            '       Consider using the --overwrite-data option'
        ]
        assert app.returncode == 1

    @staticmethod
    def test_read_srec32_allow_overlap_diff(app: RunApplication, opt_overwrite_data):
        """Hex with allow overlap option should accept overlapping data that is different."""
        app.run('tests/files/alphabet.s37', 'tests/files/alpha-overlap-diff.s37',
                opt_overwrite_data)
        assert app.stdoutlines == [
            '00000100  41 42 43 44 45 46 47 48  31 32 33 34 35 36 37 38  |ABCDEFGH12345678|',
            '00000110  51 52 53 54 55 56 57 58  59 5a                    |QRSTUVWXYZ|',
            '01f00000  61 62 63 64 65 66 67 68  69 6a 6b 6c 6d 6e 6f 70  |abcdefghijklmnop|',
            '01f00010  71 72 73 74 75 76 77 78  79 7a                    |qrstuvwxyz|'
        ]
        assert app.stderr == ''
        assert app.returncode == 0

    @staticmethod
    def test_read_fail_on_multiple_start_addresses(app: RunApplication):
        """Hex should fail if input files have multiple start addresses."""
        app.run('tests/files/alphabet.s37',
                'tests/files/alphabet.s28')
        assert app.stdout == ''
        assert app.stderrlines == [
            'ERROR: In file "tests/files/alphabet.s28"',
            '       The start address (0x200000) conflicts with '
            'a previously defined start address (0x20000000)'
        ]
        assert app.returncode == 1

    @staticmethod
    def test_read_overwrite_previous_start_address(app: RunApplication,
                                                   opt_overwrite_start_address, opt_srec):
        """Hex with last start address option should use the last of multiple start addresses."""
        app.run('tests/files/alphabet.s37',
                'tests/files/alphabet.s28',
                opt_overwrite_start_address, opt_srec)
        assert app.stdoutlines == [
            'S00600004844521B',
            'S315000001004142434445464748494A4B4C4D4E4F5061',
            'S30F000001105152535455565758595A88',
            'S315000002004142434445464748494A4B4C4D4E4F5060',
            'S30F000002105152535455565758595A87',
            'S315000F00006162636465666768696A6B6C6D6E6F7053',
            'S30F000F00107172737475767778797A3A',
            'S31501F000006162636465666768696A6B6C6D6E6F7071',
            'S30F01F000107172737475767778797A58',
            'S70500200000DA'
        ]
        assert app.stderr == ''
        assert app.returncode == 0

    @staticmethod
    def test_read_ihex(app: RunApplication):
        """Hex should read a file with IHEX format."""
        app.run('tests/files/alphabet.hex')
        assert app.stdoutlines == [
            '00000100  41 42 43 44 45 46 47 48  49 4a 4b 4c 4d 4e 4f 50  |ABCDEFGHIJKLMNOP|',
            '00000110  51 52 53 54 55 56 57 58  59 5a                    |QRSTUVWXYZ|',
            '01f00000  61 62 63 64 65 66 67 68  69 6a 6b 6c 6d 6e 6f 70  |abcdefghijklmnop|',
            '01f00010  71 72 73 74 75 76 77 78  79 7a                    |qrstuvwxyz|'
        ]
        assert app.stderr == ''
        assert app.returncode == 0

    @staticmethod
    def test_read_ihex_segment_address(app: RunApplication):
        """Hex should read a file with IHEX format and a segment address record."""
        app.run('tests/files/ihex16-seg-addr.hex')
        assert app.stdoutlines == [
            '00000100  41 42 43 44 45 46 47 48  49 4a 4b 4c 4d 4e 4f 50  |ABCDEFGHIJKLMNOP|',
            '00000110  51 52 53 54 55 56 57 58  59 5a                    |QRSTUVWXYZ|',
            '000ff000  61 62 63 64 65 66 67 68  69 6a 6b 6c 6d 6e 6f 70  |abcdefghijklmnop|',
            '000ff010  71 72 73 74 75 76 77 78  79 7a                    |qrstuvwxyz|'
        ]
        assert app.stderr == ''
        assert app.returncode == 0

    @staticmethod
    def test_read_binary(app: RunApplication):
        """Hex should read a binary file."""
        app.run('tests/files/alphabet.bin')
        assert app.stdoutlines == [
            '00000000  41 42 43 44 45 46 47 48  49 4a 4b 4c 4d 4e 4f 50  |ABCDEFGHIJKLMNOP|',
            '00000010  51 52 53 54 55 56 57 58  59 5a 61 62 63 64 65 66  |QRSTUVWXYZabcdef|',
            '00000020  67 68 69 6a 6b 6c 6d 6e  6f 70 71 72 73 74 75 76  |ghijklmnopqrstuv|',
            '00000030  77 78 79 7a                                       |wxyz|'
        ]
        assert app.stderr == ''
        assert app.returncode == 0

    @staticmethod
    def test_read_and_relocate(app: RunApplication):
        """Input file with address should relocate the memory to the specified address."""
        app.run('tests/files/alphabet.s37@8100')
        assert app.stdoutlines == [
            '00008100  41 42 43 44 45 46 47 48  49 4a 4b 4c 4d 4e 4f 50  |ABCDEFGHIJKLMNOP|',
            '00008110  51 52 53 54 55 56 57 58  59 5a                    |QRSTUVWXYZ|',
            '01f08000  61 62 63 64 65 66 67 68  69 6a 6b 6c 6d 6e 6f 70  |abcdefghijklmnop|',
            '01f08010  71 72 73 74 75 76 77 78  79 7a                    |qrstuvwxyz|'
        ]
        assert app.stderr == ''
        assert app.returncode == 0

    @staticmethod
    def test_read_and_relocate_out_of_range(app: RunApplication):
        """Input file with address should show an error if memory is not 32-bit addressable."""
        app.run('tests/files/alphabet.s37@FE100100')
        assert app.stdout == ''
        assert app.stderr == 'ERROR: Address used (0x100000019) exceeds 32-bit address space'
        assert app.returncode == 1

    @staticmethod
    def test_read_srec_checksum_error(app: RunApplication):
        """Input SREC file with a checksum error should show the error."""
        app.run('tests/files/bad-checksum.s37')
        assert app.stdout == ''
        assert app.stderrlines == [
            'ERROR: In file "tests/files/bad-checksum.s37" (line 4)',
            '       S31501F000006162636465666768696A6B6C6D6E6F7072',
            '                                                   ^^',
            '       Invalid checksum: calculated 0x71, but record has 0x72'
        ]
        assert app.returncode == 1

    @staticmethod
    def test_read_srec_record_too_long(app: RunApplication):
        """Input SREC file record with too many bytes should show an error."""
        app.run('tests/files/long-record.s37')
        assert app.stdout == ''
        assert app.stderrlines == [
            'ERROR: In file "tests/files/long-record.s37" (line 5)',
            '       S30F01F000107172737475767778797A5800',
            '         ^^',
            '       Invalid byte count: record has 0x10 bytes, but count set to 0x0F bytes'
        ]
        assert app.returncode == 1

    @staticmethod
    def test_read_srec_invalid_record_type(app: RunApplication):
        """Input SREC file with invalid record type should show an error."""
        app.run('tests/files/bad-record-type.s37')
        assert app.stdout == ''
        assert app.stderrlines == [
            'ERROR: In file "tests/files/bad-record-type.s37" (line 6)',
            '       S4030004F8',
            '       ^^',
            '       Invalid record type: 4 is not a valid record type'
        ]
        assert app.returncode == 1

    @staticmethod
    def test_read_srec_fixed_length_record_count_wrong(app: RunApplication):
        """Input SREC file with fixed-length record should show an error if wrong length."""
        app.run('tests/files/short-start.s37')
        assert app.stdout == ''
        assert app.stderrlines == [
            'ERROR: In file "tests/files/short-start.s37" (line 6)',
            '       S704200000DB',
            '         ^^',
            '       Invalid byte count: record type 7 expects 0x05 bytes; actual 0x04 bytes',
        ]
        assert app.returncode == 1

    @staticmethod
    def test_read_ihex_checksum_error(app: RunApplication):
        """Input IHEX file with a checksum error should show the error."""
        app.run('tests/files/bad-checksum.hex')
        assert app.stdout == ''
        assert app.stderrlines == [
            'ERROR: In file "tests/files/bad-checksum.hex" (line 4)',
            '       :100000006162636465666768696A6B6C6D6E6F7069',
            '                                                ^^',
            '       Invalid checksum: calculated 0x68, but record has 0x69'
        ]
        assert app.returncode == 1

    @staticmethod
    def test_read_ihex_record_too_long(app: RunApplication):
        """Input IHEX file record with too many bytes should show an error."""
        app.run('tests/files/long-record.hex')
        assert app.stdout == ''
        assert app.stderrlines == [
            'ERROR: In file "tests/files/long-record.hex" (line 5)',
            '       :0A0010007172737475767778797A4F00',
            '        ^^',
            '       Invalid byte count: record has 0x0B bytes, but count set to 0x0A bytes'
        ]
        assert app.returncode == 1

    @staticmethod
    def test_read_ihex_invalid_record_type(app: RunApplication):
        """Input IHEX file with invalid record type should show an error."""
        app.run('tests/files/bad-record-type.hex')
        assert app.stdout == ''
        assert app.stderrlines == [
            'ERROR: In file "tests/files/bad-record-type.hex" (line 3)',
            '       :0200000601F007',
            '              ^^',
            '       Invalid record type: 6 is not a valid record type'
        ]
        assert app.returncode == 1

    @staticmethod
    def test_read_ihex_fixed_length_record_count_wrong(app: RunApplication):
        """Input IHEX file with fixed-length record should show an error if wrong length."""
        app.run('tests/files/short-start.hex')
        assert app.stdout == ''
        assert app.stderrlines == [
            'ERROR: In file "tests/files/short-start.hex" (line 6)',
            '       :03000005200000D8',
            '        ^^',
            '       Invalid byte count: record type 5 expects 0x04 bytes; actual 0x03 bytes',
        ]
        assert app.returncode == 1


class Test1ModifyMemoryOptions():
    """Unit tests focused on modifying bytes using command-line options."""

    @staticmethod
    def test_create_data(app: RunApplication, opt_write_data):
        """Create data option should insert data in memory at address 0."""
        app.run(opt_write_data, '4142434445464748494A4b4C4d')
        assert app.stdout == \
            '00000000  41 42 43 44 45 46 47 48  49 4a 4b 4c 4d           |ABCDEFGHIJKLM|'
        assert app.stderr == ''
        assert app.returncode == 0

    @staticmethod
    def test_create_data_at_address(app: RunApplication, opt_write_data):
        """Create data option with address should insert data in memory at the specified address."""
        app.run(opt_write_data, '4142434445464748494A4b4C4d4E4f50@FfFFfFF0')
        assert app.stdout == \
            'fffffff0  41 42 43 44 45 46 47 48  49 4a 4b 4c 4d 4e 4f 50  |ABCDEFGHIJKLMNOP|'
        assert app.stderr == ''
        assert app.returncode == 0

    @staticmethod
    def test_create_data_at_multiple_addresses(app: RunApplication, opt_write_data):
        """Create multiple data with address should insert data in memory at specified address."""
        app.run(opt_write_data, 'ffeeddccbbaa@00', '665544332211@10')
        assert app.stdoutlines == [
            '00000000  ff ee dd cc bb aa                                 |......|',
            '00000010  66 55 44 33 22 11                                 |fUD3".|'
        ]
        assert app.stderr == ''
        assert app.returncode == 0

    @staticmethod
    def test_create_data_at_address_out_of_range(app: RunApplication, opt_write_data):
        """Create data option should show an error if memory is not 32-bit addressable."""
        app.run(opt_write_data, '4142434445464748494A4b4C4d4E4f50@FFFFFFFC')
        assert app.stdout == ''
        assert app.stderr == 'ERROR: Address used (0x10000000B) exceeds 32-bit address space'
        assert app.returncode == 1

    @staticmethod
    def test_create_value(app: RunApplication, opt_write_value):
        """Create value option should insert little-endian value in memory at address 0."""
        app.run(opt_write_value, '12345678')
        assert app.stdout == '00000000  78 56 34 12                                       |xV4.|'
        assert app.stderr == ''
        assert app.returncode == 0

    @staticmethod
    def test_create_value_at_address(app: RunApplication, opt_write_value):
        """Create value option with address should insert value in memory at specified address."""
        app.run(opt_write_value, '12345678@FfFFfFFc')
        assert app.stdout == 'fffffffc  78 56 34 12                                       |xV4.|'
        assert app.stderr == ''
        assert app.returncode == 0

    @staticmethod
    def test_create_value_at_address_out_of_range(app: RunApplication, opt_write_value):
        """Create value option should show an error if memory is not 32-bit addressable."""
        app.run(opt_write_value, '12345678@FFFFFFFD')
        assert app.stdout == ''
        assert app.stderr == 'ERROR: Address used (0x100000000) exceeds 32-bit address space'
        assert app.returncode == 1

    @staticmethod
    def test_fill(app: RunApplication, opt_fill):
        """Fill option should fill memory gaps."""
        app.run('tests/files/alpha-gap.s37', opt_fill, '3A2d29')
        assert app.stdoutlines == [
            '01efffd0  41 42 43 44 45 46 47 48  49 4a 4b 4c 4d 4e 4f 50  |ABCDEFGHIJKLMNOP|',
            '01efffe0  51 52 53 54 55 56 57 58  59 5a 3a 2d 29 3a 2d 29  |QRSTUVWXYZ:-):-)|',
            '01effff0  3a 2d 29 3a 2d 29 3a 2d  29 3a 2d 29 3a 2d 29 3a  |:-):-):-):-):-):|',
            '01f00000  61 62 63 64 65 66 67 68  69 6a 6b 6c 6d 6e 6f 70  |abcdefghijklmnop|',
            '01f00010  71 72 73 74 75 76 77 78  79 7a                    |qrstuvwxyz|'
        ]
        assert app.stderr == ''
        assert app.returncode == 0

    @staticmethod
    def test_keep(app: RunApplication, opt_keep):
        """Keep option should keep selected memory ranges and discard the rest."""
        app.run('tests/files/alphabet.s37',
                opt_keep, '100-103', '10c-01f0000D', '01f00016-01f00019')
        assert app.stdoutlines == [
            '00000100  41 42 43 44                                       |ABCD|',
            '0000010c  4d 4e 4f 50 51 52 53 54  55 56 57 58 59 5a        |MNOPQRSTUVWXYZ|',
            '01f00000  61 62 63 64 65 66 67 68  69 6a 6b 6c 6d 6e        |abcdefghijklmn|',
            '01f00016  77 78 79 7a                                       |wxyz|'
        ]
        assert app.stderr == ''
        assert app.returncode == 0

    @staticmethod
    def test_keep_single_byte(app: RunApplication, opt_keep):
        """Keep option should keep a single byte if range does not use dash ('-')."""
        app.run('tests/files/alphabet.s37', opt_keep, '100')
        assert app.stdout == \
            '00000100  41                                                |A|'
        assert app.stderr == ''
        assert app.returncode == 0

    @staticmethod
    def test_keep_whole_segment(app: RunApplication, opt_keep):
        """Keep option should keep a intact segment of the memory."""
        app.run('tests/files/alphabet.s37', opt_keep, '100-120')
        assert app.stdoutlines == [
            '00000100  41 42 43 44 45 46 47 48  49 4a 4b 4c 4d 4e 4f 50  |ABCDEFGHIJKLMNOP|',
            '00000110  51 52 53 54 55 56 57 58  59 5a                    |QRSTUVWXYZ|',
        ]
        assert app.stderr == ''
        assert app.returncode == 0

    @staticmethod
    def test_keep_with_empty_result(app: RunApplication, opt_keep):
        """Hex keep should generate an error message if all memory is discarded."""
        app.run('tests/files/alphabet.s37', opt_keep, '8000-20000')
        assert app.stdout == ''
        assert app.stderr == 'WARNING: No output memory -- all memory removed by user options'
        assert app.returncode == 0

    @staticmethod
    def test_remove(app: RunApplication, opt_remove):
        """Remove option should remove selected memory ranges and keep the rest."""
        app.run('tests/files/alphabet.s37',
                opt_remove, '104-10B', '116-1f00003', '01f0000e-01f00015')
        assert app.stdoutlines == [
            '00000100  41 42 43 44                                       |ABCD|',
            '0000010c  4d 4e 4f 50 51 52 53 54  55 56                    |MNOPQRSTUV|',
            '01f00004  65 66 67 68 69 6a 6b 6c  6d 6e                    |efghijklmn|',
            '01f00016  77 78 79 7a                                       |wxyz|'
        ]
        assert app.stderr == ''
        assert app.returncode == 0

    @staticmethod
    def test_remove_single_byte(app: RunApplication, opt_remove):
        """Remove option should remove a single byte if range does not use dash ('-')."""
        app.run('tests/files/alphabet.s37', opt_remove, '100')
        assert app.stdoutlines == [
            '00000101  42 43 44 45 46 47 48 49  4a 4b 4c 4d 4e 4f 50 51  |BCDEFGHIJKLMNOPQ|',
            '00000111  52 53 54 55 56 57 58 59  5a                       |RSTUVWXYZ|',
            '01f00000  61 62 63 64 65 66 67 68  69 6a 6b 6c 6d 6e 6f 70  |abcdefghijklmnop|',
            '01f00010  71 72 73 74 75 76 77 78  79 7a                    |qrstuvwxyz|'
        ]
        assert app.stderr == ''
        assert app.returncode == 0

    @staticmethod
    def test_remove_with_empty_result(app: RunApplication, opt_remove):
        """Hex remove should generate an error message if all memory is removed."""
        app.run('tests/files/alphabet.s37', opt_remove, '0-90000000')
        assert app.stdout == ''
        assert app.stderr == 'WARNING: No output memory -- all memory removed by user options'
        assert app.returncode == 0

    @staticmethod
    def test_equal_32m_default_memory_span(app: RunApplication):
        """Hex should not generate an error if memory span is equal to 32M."""
        app.run('--write-data', '00@0', 'ff@1ffffff')
        assert app.stdoutlines == [
            '00000000  00                                                |.|',
            '01ffffff  ff                                                |.|'
        ]
        assert app.stderr == ''
        assert app.returncode == 0

    @staticmethod
    def test_over_32m_default_memory_span(app: RunApplication):
        """Hex should generate an error if memory span is greater than 32M."""
        app.run('--write-data', '00@0', 'ff@2000000')
        assert app.stdout == ''
        assert app.stderr == 'ERROR: Data span (0x02000001 bytes) exceeds 32MB limit'
        assert app.returncode == 1

    @staticmethod
    def test_memory_span_equals_limit(app: RunApplication, opt_limit):
        """Hex limit should not generate an error message if memory span is equal to limit."""
        app.run('--write-data', '00@0', 'ff@fffff', opt_limit, '1')
        assert app.stdoutlines == [
            '00000000  00                                                |.|',
            '000fffff  ff                                                |.|'
        ]
        assert app.stderr == ''
        assert app.returncode == 0

    @staticmethod
    def test_memory_span_over_limit(app: RunApplication, opt_limit):
        """Hex limit should generate an error message if memory span is equal to limit."""
        app.run('--write-data', '00@0', 'ff@100000', opt_limit, '1')
        assert app.stdout == ''
        assert app.stderr == 'ERROR: Data span (0x00100001 bytes) exceeds 1MB limit'
        assert app.returncode == 1


class Test2FormatOutput():
    """Unit tests focused on formatting the output content."""

    @staticmethod
    def test_srec_option(app: RunApplication, opt_srec):
        """Hex SREC option should show SREC format on console."""
        app.run('tests/files/alphabet.hex', opt_srec)
        assert app.stdoutlines == [
            'S315000001004142434445464748494A4B4C4D4E4F5061',
            'S30F000001105152535455565758595A88',
            'S31501F000006162636465666768696A6B6C6D6E6F7071',
            'S30F01F000107172737475767778797A58',
            'S70520000000DA'
        ]
        assert app.stderr == ''
        assert app.returncode == 0

    @staticmethod
    def test_srec_with_no_start(app: RunApplication, opt_srec):
        """Hex should generate SREC32 without start address if none given."""
        app.run('tests/files/alphabet-nostart.hex', opt_srec)
        assert app.stdoutlines == [
            'S315000001004142434445464748494A4B4C4D4E4F5061',
            'S30F000001105152535455565758595A88',
            'S31501F000006162636465666768696A6B6C6D6E6F7071',
            'S30F01F000107172737475767778797A58',
        ]
        assert app.stderr == ''
        assert app.returncode == 0

    @staticmethod
    def test_srec_with_record_count(app: RunApplication, opt_srec):
        """Hex should generate SREC32 with a record count."""
        app.run('tests/files/alphabet.hex', opt_srec, '--record-count')
        assert app.stdoutlines == [
            'S315000001004142434445464748494A4B4C4D4E4F5061',
            'S30F000001105152535455565758595A88',
            'S31501F000006162636465666768696A6B6C6D6E6F7071',
            'S30F01F000107172737475767778797A58',
            'S5030004F8',
            'S70520000000DA'
        ]
        assert app.stderr == ''
        assert app.returncode == 0

    @staticmethod
    def test_ihex_option(app: RunApplication, opt_ihex):
        """Hex IHEX option should show IHEX format on console."""
        app.run('tests/files/alphabet.s37', opt_ihex)
        assert app.stdoutlines == [
            ':100100004142434445464748494A4B4C4D4E4F5067',
            ':0A0110005152535455565758595A8E',
            ':0200000401F009',
            ':100000006162636465666768696A6B6C6D6E6F7068',
            ':0A0010007172737475767778797A4F',
            ':0400000520000000D7',
            ':00000001FF'
        ]
        assert app.stderr == ''
        assert app.returncode == 0

    @staticmethod
    def test_ihex_with_no_start(app: RunApplication, opt_ihex):
        """Hex should generate IHEX without start address if none given."""
        app.run('tests/files/alphabet-nostart.s37', opt_ihex)
        assert app.stdoutlines == [
            ':100100004142434445464748494A4B4C4D4E4F5067',
            ':0A0110005152535455565758595A8E',
            ':0200000401F009',
            ':100000006162636465666768696A6B6C6D6E6F7068',
            ':0A0010007172737475767778797A4F',
            ':00000001FF'
        ]
        assert app.stderr == ''
        assert app.returncode == 0

    @staticmethod
    def test_bin_option_on_console(app: RunApplication, opt_binary):
        """Hex should ignore binary option and show hex dump for console output."""
        app.run('tests/files/alphabet.s37', opt_binary)
        assert app.stdoutlines == [
            '00000100  41 42 43 44 45 46 47 48  49 4a 4b 4c 4d 4e 4f 50  |ABCDEFGHIJKLMNOP|',
            '00000110  51 52 53 54 55 56 57 58  59 5a                    |QRSTUVWXYZ|',
            '01f00000  61 62 63 64 65 66 67 68  69 6a 6b 6c 6d 6e 6f 70  |abcdefghijklmnop|',
            '01f00010  71 72 73 74 75 76 77 78  79 7a                    |qrstuvwxyz|'
        ]
        assert app.stderr == ''
        assert app.returncode == 0


class Test3WriteOutputFile():
    """Unit tests focused on writing the output file."""

    @staticmethod
    def test_format_srec16_output_by_extension(app: RunApplication, opt_output):
        """Hex should generate SREC16 output based on the outfile extension."""
        for ext in _EXTENSIONS_SREC_16:
            outfile = f'tests/files/output.{ext}'
            app.run('tests/files/alphabet.hex', opt_output, outfile, '--overwrite')
            assert app.stdout == ''
            assert app.stderr == ''
            assert app.returncode == 0
            assert filecmp.cmp(outfile, 'tests/files/alphabet-noheader.s37')
            os.remove(outfile)

    @staticmethod
    def test_format_srec24_output_by_extension(app: RunApplication, opt_output):
        """Hex should generate SREC24 output based on the outfile extension."""
        for ext in _EXTENSIONS_SREC_24:
            outfile = f'tests/files/output.{ext}'
            app.run('tests/files/alphabet.hex', opt_output, outfile, '--overwrite')
            assert app.stdout == ''
            assert app.stderr == ''
            assert app.returncode == 0
            assert filecmp.cmp(outfile, 'tests/files/alphabet-noheader.s37')
            os.remove(outfile)

    @staticmethod
    def test_format_srec32_output_by_extension(app: RunApplication, opt_output):
        """Hex should generate SREC32 output based on the outfile extension."""
        for ext in _EXTENSIONS_SREC:
            outfile = f'tests/files/output.{ext}'
            app.run('tests/files/alphabet.hex', opt_output, outfile, '--overwrite')
            assert app.stdout == ''
            assert app.stderr == ''
            assert app.returncode == 0
            assert filecmp.cmp(outfile, 'tests/files/alphabet-noheader.s37')
            os.remove(outfile)

    @staticmethod
    def test_write_file_force_srec_format(app: RunApplication, opt_output, opt_srec):
        """Hex write with SREC format option should ignore output filename extension."""
        outfile = 'tests/files/output.bin'
        app.run('tests/files/alphabet.hex', opt_output, outfile, '--overwrite', opt_srec)
        assert app.stdout == ''
        assert app.stderr == ''
        assert app.returncode == 0
        assert filecmp.cmp(outfile, 'tests/files/alphabet-noheader.s37')
        os.remove(outfile)

    @staticmethod
    def test_format_ihex_output_by_extension(app: RunApplication, opt_output):
        """Hex should generate IHEX output based on the outfile extension."""
        for ext in _EXTENSIONS_IHEX:
            outfile = f'tests/files/output.{ext}'
            app.run('tests/files/alphabet.s37', opt_output, outfile, '--overwrite')
            assert app.stdout == ''
            assert app.stderr == ''
            assert app.returncode == 0
            assert filecmp.cmp(outfile, 'tests/files/alphabet.hex')
            os.remove(outfile)

    @staticmethod
    def test_write_file_force_ihex_format(app: RunApplication, opt_output, opt_ihex):
        """Hex write with IHEX format option should ignore output filename extension."""
        outfile = 'tests/files/output.bin'
        app.run('tests/files/alphabet.s37', opt_output, outfile, '--overwrite', opt_ihex)
        assert app.stdout == ''
        assert app.stderr == ''
        assert app.returncode == 0
        assert filecmp.cmp(outfile, 'tests/files/alphabet.hex')
        os.remove(outfile)

    @staticmethod
    def test_format_hex_dump_output_by_extension(app: RunApplication, opt_output):
        """Hex should generate hex dump output based on the outfile extension."""
        for ext in ['png', 'txt', 'xml']:
            outfile = f'tests/files/output.{ext}'
            app.run('tests/files/alphabet.hex', opt_output, outfile, '--overwrite')
            assert app.stdout == ''
            assert app.stderr == ''
            assert app.returncode == 0
            assert filecmp.cmp(outfile, 'tests/files/alphabet.hexdump')
            os.remove(outfile)

    @staticmethod
    def test_format_binary_output_by_extension(app: RunApplication, opt_output):
        """Hex should generate binary output based on the outfile extension."""
        for ext in _EXTENSIONS_BIN:
            outfile = f'tests/files/output.{ext}'
            app.run('tests/files/alphabet.s37', opt_output, outfile, '--overwrite')
            assert app.stdout == ''
            assert app.stderr == ''
            assert app.returncode == 0
            assert filecmp.cmp(outfile, 'tests/files/alphabet.bin')
            os.remove(outfile)

    @staticmethod
    def test_write_file_force_binary_format(app: RunApplication, opt_output, opt_binary):
        """Hex write with binary format option should ignore output filename extension."""
        outfile = 'tests/files/output.hex'
        app.run('tests/files/alphabet.s37', opt_output, outfile, '--overwrite', opt_binary)
        assert app.stdout == ''
        assert app.stderr == ''
        assert app.returncode == 0
        assert filecmp.cmp(outfile, 'tests/files/alphabet.bin')
        os.remove(outfile)

    @staticmethod
    def test_write_file_exists_error(app: RunApplication, opt_output):
        """Hex write should not write the file and show an error if the output file exists."""
        outfile = 'tests/files/already-exists.txt'
        create_file(outfile)
        outstat = os.stat(outfile)
        app.run('tests/files/alphabet.s37', opt_output, outfile)
        assert app.stdout == ''
        assert app.stderr == \
            f'ERROR: "{outfile}" already exists. Use --overwrite option to overwrite.'
        assert app.returncode == 1
        assert os.stat(outfile) == outstat
        os.remove(outfile)

    @staticmethod
    def test_write_file_with_overwrite_option(app: RunApplication, opt_output):
        """Hex write with overwrite option should overwrite an existing file."""
        outfile = 'tests/files/output.s37'
        create_file(outfile)
        outstat = os.stat(outfile)
        app.run('tests/files/alphabet.s37', opt_output, outfile, '--overwrite')
        assert app.stdout == ''
        assert app.stderr == ''
        assert app.returncode == 0
        assert os.stat(outfile) != outstat
        assert filecmp.cmp(outfile, 'tests/files/alphabet.s37')
        os.remove(outfile)
