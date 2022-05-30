"""Unit tests for the Hex application."""

import filecmp
import os
import subprocess


from hex import __version__

_EXTENSIONS_BIN = ['bin', 'dat', 'raw']
_EXTENSIONS_IHEX = ['a43', 'a90', 'h86', 'hex', 'hxh', 'hxl', 'ihe', 'ihex', 'ihx',
                    'mcs', 'obh', 'obl', 'p00', 'p89', 'p9d', 'pc8', 'pff', 'pFF']
_EXTENSIONS_SREC_16 = ['s1', 's19']
_EXTENSIONS_SREC_24 = ['s2', 's28']
_EXTENSIONS_SREC = ['exo', 'mot', 'mxt', 's', 's3', 's37', 'srec', 'sx'] + \
    _EXTENSIONS_SREC_16 + _EXTENSIONS_SREC_24
_TIMEOUT = 5000


def runhex(*args):
    """Helper function to run hex.py on the command line and capture the results."""
    command = ['python', 'src/hex.py']
    if args:
        command += args
    result = subprocess.run(command, capture_output=True, timeout=_TIMEOUT, check=False)
    stdout = str(result.stdout, encoding='utf-8').splitlines()
    if len(stdout) < 2:
        stdout = '' if len(stdout) == 0 else stdout[0]
    stderr = str(result.stderr, encoding='utf-8').splitlines()
    if len(stderr) < 2:
        stderr = '' if len(stderr) == 0 else stderr[0]
    return (stdout, stderr, result.returncode)


def create_file(filename):
    """Create an empty file with the specified filename."""
    if os.path.isfile(filename):
        return
    with open(filename, 'w', encoding='utf-8'):
        pass


class Test0CommandLine():
    """Unit tests focused on handling of command-line argument options."""

    @staticmethod
    def test_no_arguments():
        """Hex without command-line arguments should show how to get help information."""
        stdout, stderr, returncode = runhex()
        assert stdout == 'Use "hex --help" for options.'
        assert stderr == 'WARNING: No input memory.'
        assert returncode == 0

    @staticmethod
    def test_help():
        """Hex help option should show help text."""
        stdout, stderr, returncode = runhex('-h')
        assert stdout == [
            'usage: hex.py [-h] [--version] [--last-start-address] [-d DATA[@ADDR]',
            '              [DATA[@ADDR] ...]] [-v VAL[@ADDR] [VAL[@ADDR] ...]] [-f DATA]',
            '              [-k [ADDR-ADDR ...]] [-r [ADDR-ADDR ...]] [-o outfile[@ADDR]]',
            '              [--overwrite] [-B] [-I] [-S]',
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
            '  --last-start-address  use start address from the last input file',
            '  -d DATA[@ADDR] [DATA[@ADDR] ...], --data DATA[@ADDR] [DATA[@ADDR] ...]',
            '                        write (big-endian) DATA at ADDR or 0',
            '  -v VAL[@ADDR] [VAL[@ADDR] ...], --value VAL[@ADDR] [VAL[@ADDR] ...]',
            '                        write (little-endian) VAL at ADDR or 0',
            '  -f DATA, --fill DATA  fill unused memory with repeating (big-endian) DATA',
            '  -k [ADDR-ADDR ...], --keep [ADDR-ADDR ...]',
            '                        keep data in ADDR-ADDR and discard the rest',
            '  -r [ADDR-ADDR ...], --remove [ADDR-ADDR ...]',
            '                        remove data in ADDR-ADDR and keep the rest',
            '  -o outfile[@ADDR], --output outfile[@ADDR]',
            '                        the file to create with optional relocation ADDR',
            '  --overwrite           overwrite the output file if it exists',
            '  -B, --binary          force binary output (only valid with -o option)',
            '  -I, --ihex            force Intel Hex output',
            '  -S, --srec            force Motorola S output'
        ]
        assert stderr == ''
        assert returncode == 0

    @staticmethod
    def test_version():
        """Hex version option should show version of hex."""
        stdout, stderr, returncode = runhex('--version')
        assert stdout == f'hex.py version {__version__}'
        assert stderr == ''
        assert returncode == 0

    @staticmethod
    def test_missing_input_file():
        """Hex should generate an error message if a specified input does not exist."""
        stdout, stderr, returncode = runhex('tests/files/missing.s19')
        assert stdout == ''
        assert stderr == 'ERROR: No such file or directory'
        assert returncode == 1


class Test0ReadInputFiles():
    """Unit tests focused on reading input files."""

    @staticmethod
    def test_read_srec16():
        """Hex should read a file with SREC16 format."""
        stdout, stderr, returncode = runhex('tests/files/alphabet.s19')
        assert stdout == [
            '00000300  41 42 43 44 45 46 47 48  49 4a 4b 4c 4d 4e 4f 50  |ABCDEFGHIJKLMNOP|',
            '00000310  51 52 53 54 55 56 57 58  59 5a                    |QRSTUVWXYZ|',
            '00008000  61 62 63 64 65 66 67 68  69 6a 6b 6c 6d 6e 6f 70  |abcdefghijklmnop|',
            '00008010  71 72 73 74 75 76 77 78  79 7a                    |qrstuvwxyz|'
        ]
        assert stderr == ''
        assert returncode == 0

    @staticmethod
    def test_read_srec24():
        """Hex should read a file with SREC24 format."""
        stdout, stderr, returncode = runhex('tests/files/alphabet.s28')
        assert stdout == [
            '00000200  41 42 43 44 45 46 47 48  49 4a 4b 4c 4d 4e 4f 50  |ABCDEFGHIJKLMNOP|',
            '00000210  51 52 53 54 55 56 57 58  59 5a                    |QRSTUVWXYZ|',
            '00800000  61 62 63 64 65 66 67 68  69 6a 6b 6c 6d 6e 6f 70  |abcdefghijklmnop|',
            '00800010  71 72 73 74 75 76 77 78  79 7a                    |qrstuvwxyz|'
        ]
        assert stderr == ''
        assert returncode == 0

    @staticmethod
    def test_read_srec32():
        """Hex should read a file with SREC32 format."""
        stdout, stderr, returncode = runhex('tests/files/alphabet.s37')
        assert stdout == [
            '00000100  41 42 43 44 45 46 47 48  49 4a 4b 4c 4d 4e 4f 50  |ABCDEFGHIJKLMNOP|',
            '00000110  51 52 53 54 55 56 57 58  59 5a                    |QRSTUVWXYZ|',
            '80000000  61 62 63 64 65 66 67 68  69 6a 6b 6c 6d 6e 6f 70  |abcdefghijklmnop|',
            '80000010  71 72 73 74 75 76 77 78  79 7a                    |qrstuvwxyz|'
        ]
        assert stderr == ''
        assert returncode == 0

    @staticmethod
    def test_read_fail_on_multiple_start_addresses():
        """Hex should fail if input files have multiple start addresses."""
        stdout, stderr, returncode = runhex('tests/files/alphabet.s37',
                                            'tests/files/alphabet.s28')
        assert stdout == ''
        assert stderr == [
            'ERROR: In file "tests/files/alphabet.s28"',
            '       The start address (0x200000) conflicts with '
            'a previously defined start address (0x20000000)'
        ]
        assert returncode == 1

    @staticmethod
    def test_read_overwrite_previous_start_address():
        """Hex with last start address option should use the last of multiple start addresses."""
        stdout, stderr, returncode = runhex('tests/files/alphabet.s37',
                                            'tests/files/alphabet.s28',
                                            '--last-start-address', '-S')
        assert stdout == [
            'S00600004844521B',
            'S315000001004142434445464748494A4B4C4D4E4F5061',
            'S30F000001105152535455565758595A88',
            'S315000002004142434445464748494A4B4C4D4E4F5060',
            'S30F000002105152535455565758595A87',
            'S315008000006162636465666768696A6B6C6D6E6F70E2',
            'S30F008000107172737475767778797AC9',
            'S315800000006162636465666768696A6B6C6D6E6F70E2',
            'S30F800000107172737475767778797AC9',
            'S70500200000DA'
        ]
        assert stderr == ''
        assert returncode == 0

    @staticmethod
    def test_read_ihex():
        """Hex should read a file with IHEX format."""
        stdout, stderr, returncode = runhex('tests/files/alphabet.hex')
        assert stdout == [
            '00000100  41 42 43 44 45 46 47 48  49 4a 4b 4c 4d 4e 4f 50  |ABCDEFGHIJKLMNOP|',
            '00000110  51 52 53 54 55 56 57 58  59 5a                    |QRSTUVWXYZ|',
            '80000000  61 62 63 64 65 66 67 68  69 6a 6b 6c 6d 6e 6f 70  |abcdefghijklmnop|',
            '80000010  71 72 73 74 75 76 77 78  79 7a                    |qrstuvwxyz|'
        ]
        assert stderr == ''
        assert returncode == 0

    @staticmethod
    def test_read_binary():
        """Hex should read a binary file."""
        stdout, stderr, returncode = runhex('tests/files/alphabet.bin')
        assert stdout == [
            '00000000  41 42 43 44 45 46 47 48  49 4a 4b 4c 4d 4e 4f 50  |ABCDEFGHIJKLMNOP|',
            '00000010  51 52 53 54 55 56 57 58  59 5a 61 62 63 64 65 66  |QRSTUVWXYZabcdef|',
            '00000020  67 68 69 6a 6b 6c 6d 6e  6f 70 71 72 73 74 75 76  |ghijklmnopqrstuv|',
            '00000030  77 78 79 7a                                       |wxyz|'
        ]
        assert stderr == ''
        assert returncode == 0

    @staticmethod
    def test_read_and_relocate():
        """Input file with address should relocate the memory to the specified address."""
        stdout, stderr, returncode = runhex('tests/files/alphabet.s37@8100')
        assert stdout == [
            '00008100  41 42 43 44 45 46 47 48  49 4a 4b 4c 4d 4e 4f 50  |ABCDEFGHIJKLMNOP|',
            '00008110  51 52 53 54 55 56 57 58  59 5a                    |QRSTUVWXYZ|',
            '80008000  61 62 63 64 65 66 67 68  69 6a 6b 6c 6d 6e 6f 70  |abcdefghijklmnop|',
            '80008010  71 72 73 74 75 76 77 78  79 7a                    |qrstuvwxyz|'
        ]
        assert stderr == ''
        assert returncode == 0

    @staticmethod
    def test_read_and_relocate_out_of_range():
        """Input file with address should show an error if memory is not 32-bit addressable."""
        stdout, stderr, returncode = runhex('tests/files/alphabet.s37@810000E7')
        assert stdout == ''
        assert stderr == 'ERROR: Memory address is too high (up to 0x101000000)'
        assert returncode == 1


class Test1ModifyMemoryOptions():
    """Unit tests focused on modifying bytes using command-line options."""

    @staticmethod
    def test_create_data():
        """Create data option should insert data in memory at address 0."""
        stdout, stderr, returncode = runhex('-d', '4142434445464748494A4b4C4d')
        assert stdout == \
            '00000000  41 42 43 44 45 46 47 48  49 4a 4b 4c 4d           |ABCDEFGHIJKLM|'
        assert stderr == ''
        assert returncode == 0

    @staticmethod
    def test_create_data_at_address():
        """Create data option with address should insert data in memory at the specified address."""
        stdout, stderr, returncode = runhex('-d', '4142434445464748494A4b4C4d4E4f50@FfFFfFF0')
        assert stdout == \
            'fffffff0  41 42 43 44 45 46 47 48  49 4a 4b 4c 4d 4e 4f 50  |ABCDEFGHIJKLMNOP|'
        assert stderr == ''
        assert returncode == 0

    @staticmethod
    def test_create_data_at_address_out_of_range():
        """Create data option should show an error if memory is not 32-bit addressable."""
        stdout, stderr, returncode = runhex('-d', '4142434445464748494A4b4C4d4E4f50@FFFFFFFC')
        assert stdout == ''
        assert stderr == 'ERROR: Memory address is too high (up to 0x10000000B)'
        assert returncode == 1

    @staticmethod
    def test_create_value():
        """Create value option should insert little-endian value in memory at address 0."""
        stdout, stderr, returncode = runhex('-v', '12345678')
        assert stdout == '00000000  78 56 34 12                                       |xV4.|'
        assert stderr == ''
        assert returncode == 0

    @staticmethod
    def test_create_value_at_address():
        """Create value option with address should insert value in memory at specified address."""
        stdout, stderr, returncode = runhex('-v', '12345678@FfFFfFFc')
        assert stdout == 'fffffffc  78 56 34 12                                       |xV4.|'
        assert stderr == ''
        assert returncode == 0

    @staticmethod
    def test_create_value_at_address_out_of_range():
        """Create value option should show an error if memory is not 32-bit addressable."""
        stdout, stderr, returncode = runhex('-v', '12345678@FFFFFFFD')
        assert stdout == ''
        assert stderr == 'ERROR: Memory address is too high (up to 0x100000000)'
        assert returncode == 1

    @staticmethod
    def test_fill():
        """Fill option should fill memory gaps."""
        stdout, stderr, returncode = runhex('tests/files/alpha-gap.s37', '-f', '3A2d29')
        assert stdout == [
            '7fffffd0  41 42 43 44 45 46 47 48  49 4a 4b 4c 4d 4e 4f 50  |ABCDEFGHIJKLMNOP|',
            '7fffffe0  51 52 53 54 55 56 57 58  59 5a 3a 2d 29 3a 2d 29  |QRSTUVWXYZ:-):-)|',
            '7ffffff0  3a 2d 29 3a 2d 29 3a 2d  29 3a 2d 29 3a 2d 29 3a  |:-):-):-):-):-):|',
            '80000000  61 62 63 64 65 66 67 68  69 6a 6b 6c 6d 6e 6f 70  |abcdefghijklmnop|',
            '80000010  71 72 73 74 75 76 77 78  79 7a                    |qrstuvwxyz|'
        ]
        assert stderr == ''
        assert returncode == 0

    @staticmethod
    def test_keep():
        """Keep option should keep selected memory ranges and discard the rest."""
        stdout, stderr, returncode = runhex('tests/files/alphabet.s37',
                                            '-k', '100-103', '10c-8000000D', '80000016-80000019')
        assert stdout == [
            '00000100  41 42 43 44                                       |ABCD|',
            '0000010c  4d 4e 4f 50 51 52 53 54  55 56 57 58 59 5a        |MNOPQRSTUVWXYZ|',
            '80000000  61 62 63 64 65 66 67 68  69 6a 6b 6c 6d 6e        |abcdefghijklmn|',
            '80000016  77 78 79 7a                                       |wxyz|'
        ]
        assert stderr == ''
        assert returncode == 0

    @staticmethod
    def test_keep_single_byte():
        """Keep option should keep a single byte if range does not use dash ('-')."""
        stdout, stderr, returncode = runhex('tests/files/alphabet.s37',
                                            '-k', '100')
        assert stdout == \
            '00000100  41                                                |A|'
        assert stderr == ''
        assert returncode == 0

    @staticmethod
    def test_keep_with_empty_result():
        """Hex keep should generate an error message if all memory is discarded."""
        stdout, stderr, returncode = runhex('tests/files/alphabet.s37',
                                            '-k', '8000-20000')
        assert stdout == ''
        assert stderr == 'WARNING: No output memory.'
        assert returncode == 0

    @staticmethod
    def test_remove():
        """Remove option should remove selected memory ranges and keep the rest."""
        stdout, stderr, returncode = runhex('tests/files/alphabet.s37',
                                            '-r', '104-10B', '116-80000003', '8000000e-80000015')
        assert stdout == [
            '00000100  41 42 43 44                                       |ABCD|',
            '0000010c  4d 4e 4f 50 51 52 53 54  55 56                    |MNOPQRSTUV|',
            '80000004  65 66 67 68 69 6a 6b 6c  6d 6e                    |efghijklmn|',
            '80000016  77 78 79 7a                                       |wxyz|'
        ]
        assert stderr == ''
        assert returncode == 0

    @staticmethod
    def test_remove_single_byte():
        """Remove option should remove a single byte if range does not use dash ('-')."""
        stdout, stderr, returncode = runhex('tests/files/alphabet.s37',
                                            '-r', '100')
        assert stdout == [
            '00000101  42 43 44 45 46 47 48 49  4a 4b 4c 4d 4e 4f 50 51  |BCDEFGHIJKLMNOPQ|',
            '00000111  52 53 54 55 56 57 58 59  5a                       |RSTUVWXYZ|',
            '80000000  61 62 63 64 65 66 67 68  69 6a 6b 6c 6d 6e 6f 70  |abcdefghijklmnop|',
            '80000010  71 72 73 74 75 76 77 78  79 7a                    |qrstuvwxyz|'
        ]
        assert stderr == ''
        assert returncode == 0

    @staticmethod
    def test_remove_with_empty_result():
        """Hex remove should generate an error message if all memory is removed."""
        stdout, stderr, returncode = runhex('tests/files/alphabet.s37',
                                            '-r', '0-90000000')
        assert stdout == ''
        assert stderr == 'WARNING: No output memory.'
        assert returncode == 0


class Test2FormatOutput():
    """Unit tests focused on formatting the output content."""

    @staticmethod
    def test_srec_option():
        """Hex SREC option should show SREC format on console."""
        stdout, stderr, returncode = runhex('tests/files/alphabet.hex', '-S')
        assert stdout == [
            'S315000001004142434445464748494A4B4C4D4E4F5061',
            'S30F000001105152535455565758595A88',
            'S315800000006162636465666768696A6B6C6D6E6F70E2',
            'S30F800000107172737475767778797AC9',
            'S70520000000DA'
        ]
        assert stderr == ''
        assert returncode == 0

    @staticmethod
    def test_srec_with_no_start():
        """Hex should generate SREC32 without start address if none given."""
        stdout, stderr, returncode = runhex('tests/files/alphabet-nostart.hex', '-S')
        assert stdout == [
            'S315000001004142434445464748494A4B4C4D4E4F5061',
            'S30F000001105152535455565758595A88',
            'S315800000006162636465666768696A6B6C6D6E6F70E2',
            'S30F800000107172737475767778797AC9',
        ]
        assert stderr == ''
        assert returncode == 0

    @staticmethod
    def test_ihex_option():
        """Hex IHEX option should show IHEX format on console."""
        stdout, stderr, returncode = runhex('tests/files/alphabet.s37', '-I')
        assert stdout == [
            ':100100004142434445464748494A4B4C4D4E4F5067',
            ':0A0110005152535455565758595A8E',
            ':0200000480007A',
            ':100000006162636465666768696A6B6C6D6E6F7068',
            ':0A0010007172737475767778797A4F',
            ':0400000520000000D7',
            ':00000001FF'
        ]
        assert stderr == ''
        assert returncode == 0

    @staticmethod
    def test_ihex_with_no_start():
        """Hex should generate IHEX without start address if none given."""
        stdout, stderr, returncode = runhex('tests/files/alphabet-nostart.s37', '-I')
        assert stdout == [
            ':100100004142434445464748494A4B4C4D4E4F5067',
            ':0A0110005152535455565758595A8E',
            ':0200000480007A',
            ':100000006162636465666768696A6B6C6D6E6F7068',
            ':0A0010007172737475767778797A4F',
            ':00000001FF'
        ]
        assert stderr == ''
        assert returncode == 0

    @staticmethod
    def test_bin_option_on_console():
        """Hex should ignore binary option and show hex dump for console output."""
        stdout, stderr, returncode = runhex('tests/files/alphabet.s37', '-B')
        assert stdout == [
            '00000100  41 42 43 44 45 46 47 48  49 4a 4b 4c 4d 4e 4f 50  |ABCDEFGHIJKLMNOP|',
            '00000110  51 52 53 54 55 56 57 58  59 5a                    |QRSTUVWXYZ|',
            '80000000  61 62 63 64 65 66 67 68  69 6a 6b 6c 6d 6e 6f 70  |abcdefghijklmnop|',
            '80000010  71 72 73 74 75 76 77 78  79 7a                    |qrstuvwxyz|'
        ]
        assert stderr == ''
        assert returncode == 0


class Test3WriteOutputFile():
    """Unit tests focused on writing the output file."""

    @staticmethod
    def test_format_srec16_output_by_extension():
        """Hex should generate SREC16 output based on the outfile extension."""
        for ext in _EXTENSIONS_SREC_16:
            outfile = f'tests/files/output.{ext}'
            stdout, stderr, returncode = runhex('tests/files/alphabet.hex',
                                                '-o', outfile, '--overwrite')
            assert stdout == ''
            assert stderr == ''
            assert returncode == 0
            assert filecmp.cmp(outfile, 'tests/files/alphabet-noheader.s37')
            os.remove(outfile)

    @staticmethod
    def test_format_srec24_output_by_extension():
        """Hex should generate SREC24 output based on the outfile extension."""
        for ext in _EXTENSIONS_SREC_24:
            outfile = f'tests/files/output.{ext}'
            stdout, stderr, returncode = runhex('tests/files/alphabet.hex',
                                                '-o', outfile, '--overwrite')
            assert stdout == ''
            assert stderr == ''
            assert returncode == 0
            assert filecmp.cmp(outfile, 'tests/files/alphabet-noheader.s37')
            os.remove(outfile)

    @staticmethod
    def test_format_srec32_output_by_extension():
        """Hex should generate SREC32 output based on the outfile extension."""
        for ext in _EXTENSIONS_SREC:
            outfile = f'tests/files/output.{ext}'
            stdout, stderr, returncode = runhex('tests/files/alphabet.hex',
                                                '-o', outfile, '--overwrite')
            assert stdout == ''
            assert stderr == ''
            assert returncode == 0
            assert filecmp.cmp(outfile, 'tests/files/alphabet-noheader.s37')
            os.remove(outfile)

    @staticmethod
    def test_write_file_force_srec_format():
        """Hex write with SREC format option should ignore output filename extension."""
        outfile = 'tests/files/output.bin'
        stdout, stderr, returncode = runhex('tests/files/alphabet.hex',
                                            '-o', outfile, '--overwrite', '-S')
        assert stdout == ''
        assert stderr == ''
        assert returncode == 0
        assert filecmp.cmp(outfile, 'tests/files/alphabet-noheader.s37')
        os.remove(outfile)

    @staticmethod
    def test_format_ihex_output_by_extension():
        """Hex should generate IHEX output based on the outfile extension."""
        for ext in _EXTENSIONS_IHEX:
            outfile = f'tests/files/output.{ext}'
            stdout, stderr, returncode = runhex('tests/files/alphabet.s37',
                                                '-o', outfile, '--overwrite')
            assert stdout == ''
            assert stderr == ''
            assert returncode == 0
            assert filecmp.cmp(outfile, 'tests/files/alphabet.hex')
            os.remove(outfile)

    @staticmethod
    def test_write_file_force_ihex_format():
        """Hex write with IHEX format option should ignore output filename extension."""
        outfile = 'tests/files/output.bin'
        stdout, stderr, returncode = runhex('tests/files/alphabet.s37',
                                            '-o', outfile, '--overwrite', '-I')
        assert stdout == ''
        assert stderr == ''
        assert returncode == 0
        assert filecmp.cmp(outfile, 'tests/files/alphabet.hex')
        os.remove(outfile)

    @staticmethod
    def test_format_hex_dump_output_by_extension():
        """Hex should generate hex dump output based on the outfile extension."""
        for ext in ['png', 'txt', 'xml']:
            outfile = f'tests/files/output.{ext}'
            stdout, stderr, returncode = runhex('tests/files/alphabet.hex',
                                                '-o', outfile, '--overwrite')
            assert stdout == ''
            assert stderr == ''
            assert returncode == 0
            assert filecmp.cmp(outfile, 'tests/files/alphabet.hexdump')
            os.remove(outfile)

    @staticmethod
    def test_format_binary_output_by_extension():
        """Hex should generate binary output based on the outfile extension."""
        for ext in _EXTENSIONS_BIN:
            outfile = f'tests/files/output.{ext}'
            stdout, stderr, returncode = runhex('tests/files/alphabet.s37',
                                                '-o', outfile, '--overwrite')
            assert stdout == ''
            assert stderr == ''
            assert returncode == 0
            assert filecmp.cmp(outfile, 'tests/files/alphabet.bin')
            os.remove(outfile)

    @staticmethod
    def test_write_file_force_binary_format():
        """Hex write with binary format option should ignore output filename extension."""
        outfile = 'tests/files/output.hex'
        stdout, stderr, returncode = runhex('tests/files/alphabet.s37',
                                            '-o', outfile, '--overwrite', '-B')
        assert stdout == ''
        assert stderr == ''
        assert returncode == 0
        assert filecmp.cmp(outfile, 'tests/files/alphabet.bin')
        # with open(outfile, 'rb') as fin:
        #     contents = fin.read()
        # assert contents == b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
        os.remove(outfile)

    @staticmethod
    def test_write_file_exists_error():
        """Hex write should not write the file and show an error if the output file exists."""
        outfile = 'tests/files/already-exists.txt'
        create_file(outfile)
        outstat = os.stat(outfile)
        stdout, stderr, returncode = runhex('tests/files/alphabet.s37', '-o', outfile)
        assert stdout == ''
        assert stderr == f'ERROR: "{outfile}" already exists. Use --overwrite option to overwrite.'
        assert returncode == 1
        assert os.stat(outfile) == outstat
        os.remove(outfile)

    @staticmethod
    def test_write_file_with_overwrite_option():
        """Hex write with overwrite option should overwrite an existing file."""
        outfile = 'tests/files/output.s37'
        create_file(outfile)
        outstat = os.stat(outfile)
        stdout, stderr, returncode = runhex('tests/files/alphabet.s37',
                                            '-o', outfile, '--overwrite')
        assert stdout == ''
        assert stderr == ''
        assert returncode == 0
        assert os.stat(outfile) != outstat
        assert filecmp.cmp(outfile, 'tests/files/alphabet.s37')
        os.remove(outfile)
