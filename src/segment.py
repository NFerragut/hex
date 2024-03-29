"""segment.py -- Segment class definition

A Segment object represents consecutively defined bytes with a starting address.
"""

from exception import HexError

_ADDR32_RANGE = range(0, 0x100000000)

_SEGMENTS_OVERLAP = -1
_SEGMENTS_ARE_ADJACENT = 0
_SEGMENTS_HAVE_GAP = 1


class DataCollisionError(HexError):
    """Attempted to combine data segments that overlap without selecting the overwrite option."""

    def __init__(self, address, data_old, data_new):
        super().__init__()
        self.filename = ''
        self.address = address
        self.data_new = data_new
        self.data_old = data_old

    def __str__(self):
        out = [
            f'ERROR: In file "{self.filename}"',
            f'       The data at 0x{self.address:X} (0x{self.data_new:02X}) conflicts with '
                f'previously defined data (0x{self.data_old:02X})',
            '       Consider using the --overwrite-data option'
        ]
        return '\n'.join(out)


class NonSequentialDataError(HexError):
    """Segments can only be combined if they overlap or they have no gap between them."""


class Segment:
    """A memory segment with a start address and consecutively defined bytes."""

    def __init__(self, data=None, addrlo: int = 0):
        """Create a Segment object."""
        if isinstance(data, Segment):
            self._addrlo = data.addrlo
            self._data = data.data
        else:
            self._data = b''
            self.addrlo = addrlo
            self.data = data
        self._validate()

    def _validate(self):
        """Validate that the location of the data does not overflow the 32-bit address range."""
        if self._addrlo < 0:
            raise ValueError(f'ERROR: Address used ({self._addrlo}) is negative')
        datalen = len(self._data)
        addrlast = self._addrlo + (datalen - 1 if datalen > 0 else 0)
        if addrlast.bit_length() > 32:
            raise ValueError(f'ERROR: Address used (0x{addrlast:X}) exceeds 32-bit address space')

    @property
    def addrhi(self) -> int:
        """Get the end address of the segment."""
        return self._addrlo + len(self._data)

    @property
    def addrlo(self) -> int:
        """Get the starting address of the segment."""
        return self._addrlo

    @addrlo.setter
    def addrlo(self, value: int):
        """Set the starting address of the segment."""
        self._addrlo = 0 if value is None else int(value)
        self._validate()

    @property
    def data(self) -> bytes:
        """Get the data in the segment."""
        return self._data

    @data.setter
    def data(self, value: bytes):
        """Set the data in the segment."""
        if value is None:
            self._data = b''
        else:
            self._data = bytes(value)
        self._validate()

    @property
    def size(self) -> int:
        """Get the number of bytes in the segment."""
        return len(self._data)

    def add(self, segment: 'Segment', overwrite: bool = False) -> 'Segment':
        """Add another segment's data to self.

        segment = The Segment to add to self.
        overwrite = True to allow segment to overwrite self.

        Raises NonSequentialDataError if combining the segments results in a memory gap.
        Raises DataCollisionError if the segments overlap and overwrite is False.
        """
        if self.overlaps(segment):
            if not overwrite:
                conflict = self._conflicting_data(segment)
                if conflict is not None:
                    raise DataCollisionError(*conflict)
            if self.addrlo <= segment.addrlo:
                # Overlap:  1--2====2--1 where 1=self, 2=segment
                self.data = self.data[:segment.addrlo - self.addrlo] + \
                    segment.data + self.data[segment.addrhi - self.addrlo:]
            else:
                # Overlap:  2--1====2--1 where 1=self, 2=segment
                self.data = segment.data + \
                    self.data[segment.addrhi - self.addrlo:]
                self.addrlo = segment.addrlo
        elif self.isadjacent(segment):
            if self.addrlo < segment.addrlo:
                self.data += segment.data
            else:
                self.addrlo = segment.addrlo
                self.data = segment.data + self.data
        else:
            raise NonSequentialDataError(self, segment)
        return self

    def _conflicting_data(self, segment: 'Segment'):
        """Get ()address, new_data, old_data) for the first conflicting byte."""
        addrlo = max(self.addrlo, segment.addrlo)
        addrhi = min(self.addrhi, segment.addrhi)
        local = self.subsegment(addrlo, addrhi).data
        remote = segment.subsegment(addrlo, addrhi).data
        index = next((i
                      for i in range(len(local))
                      if local[i] != remote[i]), None)
        if index is None:
            return None
        return addrlo + index, local[index], remote[index]

    def isadjacent(self, segment: 'Segment') -> bool:
        """Return True if the specified segment is adjacent (no gaps) to this segment."""
        return segment.addrlo == self.addrhi or self.addrlo == segment.addrhi

    def overlaps(self, segment: 'Segment') -> bool:
        """Return True if the specified segment overlaps with this segment."""
        return segment.addrlo < self.addrhi and self.addrlo < segment.addrhi

    def subsegment(self, addrlo, addrhi) -> 'Segment':
        """Get a slice of the segment data in the specified range."""
        offsetlo = 0 if addrlo < self._addrlo else addrlo - self._addrlo
        if addrhi < self._addrlo:
            offsethi = 0
        elif addrhi < self.addrhi:
            offsethi = addrhi - self._addrlo
        else:
            offsethi = self.size
        if offsethi <= offsetlo:
            return Segment()
        return Segment(self._data[offsetlo:offsethi], max(addrlo, self._addrlo))

    def split(self, bytes_per_seg: int = 16) -> list['Segment']:
        """Split the segment into a list of one or more segments."""
        segments = [Segment(self.data[offset:offset + bytes_per_seg], self.addrlo + offset)
                    for offset in range(0, self.size, bytes_per_seg)]
        return segments
