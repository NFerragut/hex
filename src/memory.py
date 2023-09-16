"""memory.py -- The memory from hex and binary files."""

import re

from exception import HexError
from segment import Segment
from segments import Segments

FORMAT_BIN = '01'
FORMAT_DUMP = 'hexdump'
FORMAT_IHEX = 'ihex'
FORMAT_SREC = 'srec'
FORMAT_SREC_WITH_REC_COUNT = 'srec+count'

_IHEX_DATA = 0
_IHEX_END_OF_FILE = 1
_IHEX_EXTENDED_SEGMENT_ADDRESS = 2
_IHEX_START_SEGMENT_ADDRESS = 3
_IHEX_EXTENDED_LINEAR_ADDRESS = 4
_IHEX_START_LINEAR_ADDRESS = 5
_IHEX_UNSUPPORTED = 6

_SREC_HEADER = 0
_SREC_A16_DATA = 1
_SREC_A24_DATA = 2
_SREC_A32_DATA = 3
_SREC_REC_INVALID = 4
_SREC_A16_COUNT = 5
_SREC_A24_COUNT = 6
_SREC_A32_START = 7
_SREC_A24_START = 8
_SREC_A16_START = 9
_SREC_UNSUPPORTED = 10
_SREC_FLIP_VALUE = 10

_EXPECTED_SREC_ADDRESS_LENGTH = {
    _SREC_HEADER: 2,
    _SREC_A16_DATA: 2,
    _SREC_A24_DATA: 3,
    _SREC_A32_DATA: 4,
    _SREC_A16_COUNT: 2,
    _SREC_A24_COUNT: 3,
    _SREC_A32_START: 4,
    _SREC_A24_START: 3,
    _SREC_A16_START: 2
}

_EXPECTED_IHEX_DATA_COUNT = {
    _IHEX_END_OF_FILE: 0,
    _IHEX_EXTENDED_SEGMENT_ADDRESS: 2,
    _IHEX_START_SEGMENT_ADDRESS: 4,
    _IHEX_EXTENDED_LINEAR_ADDRESS: 2,
    _IHEX_START_LINEAR_ADDRESS: 4
}


class FileContentError(HexError):
    """Base error for errors found in hex files."""

    def __init__(self, message, column_number=None, line_number=None, filename=''):
        super().__init__(message)
        self.filename = filename
        self.column_number = column_number
        self.line_number = line_number
        self.line_text = ''

    def __str__(self):
        out = []
        if self.filename:
            out.append(f'In file "{self.filename}"')
            if self.line_number is not None:
                out[0] += f' (line {self.line_number})'
            if self.line_text:
                out.append(self.line_text)
                if self.column_number is not None:
                    column_indent = ' ' * self.column_number
                    out.append(f'{column_indent}^^')
        out.append(self.args[0])
        message = '\n       '.join(out)
        return f'ERROR: {message}'


class BadRecordTypeError(FileContentError):
    """A record with an unsupported record type was found."""

    def __init__(self, record_type, column_number):
        super().__init__(
            f'Invalid record type: {record_type} is not a valid record type',
            column_number=column_number)


class ChecksumError(FileContentError):
    """The checksum does not match the hex data."""

    def __init__(self, expected_checksum, actual_checksum, column_number):
        super().__init__(
            f'Invalid checksum: calculated 0x{expected_checksum:02X}, '
            f'but record has 0x{actual_checksum:02X}',
            column_number=column_number)


class RecordLengthError(FileContentError):
    """The length field does not match the length of the hex data."""

    def __init__(self, expected_count, actual_count, column_number):
        super().__init__(
            f'Invalid byte count: record has 0x{expected_count:02X} bytes, '
            f'but count set to 0x{actual_count:02X} bytes',
            column_number=column_number)


class RecordTypeLengthError(FileContentError):
    """The length field does not match the expected length for the record type."""

    def __init__(self, record_type, expected_count, actual_count, column_number):
        super().__init__(
            f'Invalid byte count: record type {record_type} '
            f'expects 0x{expected_count:02X} bytes; actual 0x{actual_count:02X} bytes',
            column_number=column_number)


class StartAddressError(FileContentError):
    """The start address conflicts with a previous start address."""


class Memory:
    """The memory extracted from the input files."""

    def __init__(self, source: str = None, *, overwrite_data=False):
        self._header: list[bytes] = []
        self._segments: Segments = Segments()
        self._start_address: int = None
        if source is not None:
            self.read(str(source), overwrite_data=overwrite_data)

    @property
    def is_empty(self) -> bool:
        """Return True if the memory contains no data."""
        return self._segments.span == 0

    @property
    def header(self) -> bytes:
        """Get the header bytes read from the Motorola S input file(s).

        Returns all header bytes read from the Motorola S input files. The header bytes are
        concatenated together using tab characters (b'\\t').
        """
        return b'\t'.join(self._header)

    @property
    def start_address(self) -> int:
        """Get the start address of the firmware represented by the memory."""
        return self._start_address

    @start_address.setter
    def start_address(self, value):
        """Set the start address of the firmware represented by the memory."""
        if value is None:
            self._start_address = None
            return
        self._start_address = int(value)

    @property
    def segments(self) -> Segments:
        """Get the list of Segment objects that make up the memory."""
        return self._segments

    def add(self, memory, *, overwrite=False, last_start=False):
        """Add the memory of another Memory object to this one."""
        segments = []
        if isinstance(memory, Segment):
            segments = [memory]
        elif isinstance(memory, Segments):
            segments = memory._segments
        elif isinstance(memory, Memory):
            self.extend_header(memory.header)
            if memory.start_address is not None and memory.start_address != self.start_address:
                if self.start_address is None or last_start:
                    self.start_address = memory.start_address
                else:
                    raise StartAddressError(f'The start address (0x{memory.start_address:X}) '
                                            'conflicts with a previously defined '
                                            f'start address (0x{self.start_address:X})')
            segments = memory._segments
        else:
            raise TypeError(f'Don\'t know how to add type "{type(memory).__name__}" to Memory.')
        self._segments.add(segments, overwrite=overwrite)

    def clear(self):
        """Clear the memory and its properties."""
        self.__init__()

    def extend_header(self, value: bytes):
        """Extend the header text with the specified value."""
        if value:
            try:
                self._header.remove(value)
            except ValueError:
                pass
            self._header.append(value)

    def moveto(self, address: int):
        """Move all the memory to a new location."""
        self._segments.addrlo = address

    def read(self, filename: str, *, overwrite_data=False):
        """Read an input file's data.

        Clears any previously loaded data.
        Automatically detects the format of the input file. Supported file formats are:
          - Motorola S
          - Intel Hex
          - Binary

        filename = Name of the input file

        overwrite_data = Allows new data to overwrite older data
        """
        force_binary = False
        with open(filename, 'rb') as fin:
            binary = fin.read()
        try:
            text = binary.decode('utf-8', 'strict')
            self.read_srec(text, overwrite_data=overwrite_data)
            if not self._segments:
                self.read_ihex(text, overwrite_data=overwrite_data)
                if not self._segments:
                    force_binary = True
        except UnicodeDecodeError:
            force_binary = True
        if force_binary:
            self.read_binary(binary)

    def read_binary(self, binary):
        """Replace memory with binary data."""
        seg = Segment(binary)
        self.clear()
        self._segments.add(seg)

    def read_ihex(self, ihex: str, *, overwrite_data=False):
        """Replace memory with Intel Hex data loaded from text.

        ihex = text for a Intel Hex file.

        overwrite_data = Allows new data to overwrite older data
        """
        self.clear()
        self.start_address = None
        extended_address = 0
        for line_number, line_text in enumerate(ihex.splitlines(), 1):
            found = re.search(r':([0-9A-Fa-f]{2})+', line_text)
            if not found:
                continue
            try:
                rectype, address, data = _parse_ihex_line(found[0])
                if rectype == _IHEX_DATA:
                    segment = Segment(data, extended_address + address)
                    self._segments.add(segment, overwrite=overwrite_data)
                elif rectype == _IHEX_EXTENDED_SEGMENT_ADDRESS:
                    extended_address = int.from_bytes(data, byteorder='big') << 4
                elif rectype == _IHEX_START_SEGMENT_ADDRESS:
                    self._start_address = (int.from_bytes(data[:2], byteorder='big') << 4 +
                                           int.from_bytes(data[2:], byteorder='big'))
                elif rectype == _IHEX_EXTENDED_LINEAR_ADDRESS:
                    extended_address = int.from_bytes(data, byteorder='big') << 16
                elif rectype == _IHEX_START_LINEAR_ADDRESS:
                    self._start_address = int.from_bytes(data, byteorder='big')
                # elif rectype == IHEX_END_OF_FILE:
                #     Do not force "END_OF_FILE" to be the last record.
                # else:
                #     Do not cause failure if rectype is invalid.
            except FileContentError as error:
                error.line_text = line_text.rstrip()
                error.line_number = line_number
                raise

    def read_srec(self, srec: str, *, overwrite_data=False):
        """Replace memory with Motorola S data loaded from text.

        srec = text for a Motorola S file.

        overwrite_data = Allows new data to overwrite older data
        """
        self.clear()
        self.start_address = None
        for line_number, line_text in enumerate(srec.splitlines(), 1):
            found = re.search(r'S[0-9A-Fa-f]([0-9A-Fa-f]{2})+', line_text)
            if not found:
                continue
            try:
                rectype, address, data = _parse_srec_line(found[0])
                if rectype == _SREC_HEADER:
                    self._header = [data]
                elif rectype in [_SREC_A16_DATA, _SREC_A24_DATA, _SREC_A32_DATA]:
                    segment = Segment(data, address)
                    self._segments.add(segment, overwrite=overwrite_data)
                elif rectype in [_SREC_A16_START, _SREC_A24_START, _SREC_A32_START]:
                    self.start_address = address
                # elif rectype in [_SREC_A16_COUNT, _SREC_A24_COUNT]:
                #     Do not cause failure if record count is wrong.
                # else:
                #     Do not cause failure if rectype is invalid.
            except FileContentError as error:
                error.line_text = line_text.rstrip()
                error.line_number = line_number
                raise

    def write(self, fout, *, bytes_per_line=16, output_format=''):
        """Write memory to a file.

        The format of the output file is based on the filename extension, but it can be overridden
        by the format parameter. If the filename extension does not result in any specific file
        format then the unix hexdump format is used.

        filename = Name of the output file.

        bytes_per_line = The number of bytes to write on each line.

        output_format = Override the output format. Valid values are 'binary', 'hexdump', 'ihex',
            and 'srec'.
        """
        if output_format == FORMAT_BIN:
            self.write_binary(fout)
        elif output_format == FORMAT_SREC:
            self.write_srec(fout, bytes_per_line=bytes_per_line)
        elif output_format == FORMAT_SREC_WITH_REC_COUNT:
            self.write_srec(fout, bytes_per_line=bytes_per_line, show_count=True)
        elif output_format == FORMAT_IHEX:
            self.write_ihex(fout, bytes_per_line=bytes_per_line)
        else:
            self.write_hexdump(fout)

    def write_binary(self, fout):
        """Write the memory to a binary file."""
        for seg in self._segments:
            fout.write(seg.data)

    def write_hexdump(self, fout):
        """Write the memory to a binary file."""
        for seg in self._segments:
            for subseg in seg.split(16):
                print(_dumptext(subseg.addrlo, subseg.data), file=fout)

    def write_ihex(self, fout, *, bytes_per_line=16):
        """Write the memory to an Intel Hex file."""
        extaddr = 0
        for seg in self._segments:
            for subseg in seg.split(bytes_per_line):
                address_hiword = int(subseg.addrlo / 65536)
                if extaddr != address_hiword:
                    extaddr = address_hiword
                    addrbytes = extaddr.to_bytes(2, byteorder='big')
                    print(_ihextext(_IHEX_EXTENDED_LINEAR_ADDRESS, 0, addrbytes), file=fout)
                address_loword = subseg.addrlo & 65535
                print(_ihextext(_IHEX_DATA, address_loword, subseg.data), file=fout)
        if isinstance(self._start_address, int):
            addrbytes = self._start_address.to_bytes(4, byteorder='big')
            print(_ihextext(_IHEX_START_LINEAR_ADDRESS, 0, addrbytes), file=fout)
        print(_ihextext(_IHEX_END_OF_FILE, 0, b''), file=fout)

    def write_srec(self, fout, *, bytes_per_line=16, show_count=False):
        """Write the memory to a Motorola S file."""
        reccount = 0
        if self._header:
            print(_srectext(_SREC_HEADER, 0, self.header), file=fout)
        start_address = self._start_address if self._start_address else 0
        bits = max(self._segments.addrhi.bit_length(), start_address.bit_length())
        rectype = _SREC_A16_DATA if bits <= 16 else \
            (_SREC_A24_DATA if bits <= 24 else _SREC_A32_DATA)
        for seg in self._segments:
            for subseg in seg.split(bytes_per_line):
                print(_srectext(rectype, subseg.addrlo, subseg.data), file=fout)
                reccount += 1
        if show_count:
            rec_for_reccount = _SREC_A16_COUNT if reccount < 65536 else _SREC_A24_COUNT
            print(_srectext(rec_for_reccount, reccount, b''), file=fout)
        if self._start_address is not None:
            print(_srectext(_SREC_FLIP_VALUE - rectype, self.start_address, b''), file=fout)


def _dumptext(address: int, data: bytes) -> str:
    """Return a hex dump record"""
    hextext = data.hex(' ').ljust(47)
    datatext = ''.join([chr(ascii) if ascii in range(32, 127) else '.'
                        for ascii in data])
    return f'{address:08x}  {hextext[:24]} {hextext[24:]}  |{datatext}|'


def _ihextext(rectype, address: int, data: bytes) -> str:
    """Return an Intel Hex record."""
    count = len(data)
    address = address.to_bytes(2, byteorder='big')
    record = bytes([count, *address, rectype, *data])
    checksum = (0 - sum(record)) & 255
    record += bytes([checksum])
    return ':' + record.hex().upper()


def _srectext(rectype, address: int, data: bytes) -> str:
    """Return a Motorola S record."""
    address_length = _EXPECTED_SREC_ADDRESS_LENGTH[rectype]
    count = address_length + len(data) + 1
    address = address.to_bytes(address_length, byteorder='big')
    record = bytes([count, *address, *data])
    checksum = (sum(record) & 255) ^ 255
    record += bytes([checksum])
    return f'S{str(rectype)}' + record.hex().upper()


def _parse_srec_line(hextext: str) -> tuple[int, int, bytes]:
    """Decode a line of Motorola S formatted text."""
    record = bytes.fromhex('0' + hextext[1:])
    recordsum = (sum(record[1:]) & 255)
    if recordsum != 255:
        checksum = record[-1]
        expected_checksum = ((recordsum - checksum) & 255) ^ 255
        colnum = len(hextext) - 2
        raise ChecksumError(expected_checksum, checksum, colnum)
    count = record[1]
    expected_count = len(record) - 2
    if count != expected_count:
        raise RecordLengthError(expected_count, count, 2)
    rectype = record[0]
    if rectype == _SREC_REC_INVALID or rectype >= _SREC_UNSUPPORTED:
        raise BadRecordTypeError(rectype, 0)
    address_length = _EXPECTED_SREC_ADDRESS_LENGTH[rectype]
    expected_count = address_length + 1
    if rectype >= _SREC_A16_COUNT and count != expected_count:
        raise RecordTypeLengthError(rectype, expected_count, count, 2)
    address = int.from_bytes(record[2:address_length + 2], byteorder='big')
    data = record[address_length + 2:-1]
    return (rectype, address, data)


def _parse_ihex_line(hextext: str) -> tuple[int, int, bytes]:
    """Decode a line of Intel Hex formatted text."""
    record = bytes.fromhex(hextext[1:])
    recordsum = (sum(record) & 255)
    if recordsum != 0:
        checksum = record[-1]
        expected_checksum = (checksum - recordsum) & 255
        colnum = len(hextext) - 2
        raise ChecksumError(expected_checksum, checksum, colnum)
    count = record[0]
    expected_count = len(record) - 5
    if count != expected_count:
        raise RecordLengthError(expected_count, count, 1)
    rectype = record[3]
    if rectype >= _IHEX_UNSUPPORTED:
        raise BadRecordTypeError(rectype, 7)
    if rectype != 0:
        expected_count = _EXPECTED_IHEX_DATA_COUNT[rectype]
        if count != expected_count:
            raise RecordTypeLengthError(rectype, expected_count, count, 1)
    address = int.from_bytes(record[1:3], byteorder='big')
    data = record[4:-1]
    return (rectype, address, data)
