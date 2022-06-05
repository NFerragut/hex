"""segments.py -- Segments class definition

A Segments object represents a list of Segment objects.
"""

import itertools
from typing import Iterator

from segment import Segment

_SEGMENTS_ARE_ADJACENT = 0
_SEGMENTS_HAVE_GAP = 1
_SEGMENTS_OVERLAP = -1


class Segments:
    """A list of Segment objects."""

    def __init__(self, segments: list[Segment] = None, overwrite=False):
        self._segments: list[Segment] = []
        self.add(segments, overwrite)

    @property
    def addrhi(self) -> int:
        """Get the end address of the segment."""
        if self._segments:
            return self._segments[-1].addrhi
        return 0

    @property
    def addrlo(self) -> int:
        """Get the starting address of the first segment."""
        if self._segments:
            return self._segments[0].addrlo
        return 0

    @addrlo.setter
    def addrlo(self, value: int):
        """Set the starting address of the first segment."""
        offset = int(value) - self.addrlo
        for seg in self._segments:
            seg.addrlo += offset

    @property
    def span(self) -> int:
        """Get the number of bytes spanned by the segments."""
        if self._segments:
            return self._segments[-1].addrhi - self._segments[0].addrlo
        return 0

    def add(self, segments, overwrite=False):
        """Add segment(s) to the list.

        Any adjacent or overlapping segments will be combined.
        The list will be orderd from lowest to highest address when done.
        """
        if segments is None:
            return
        if isinstance(segments, Segment):
            segments = [segments]
        self._segments.sort(key=lambda x: x.addrlo)
        for segment in segments:
            if segment.size == 0:
                continue
            segment = Segment(segment)  # use a copy
            segment = self._join_connected_segments(segment, overwrite)
            self._insert_disconnected_segment(segment)

    def _join_connected_segments(self, segment, overwrite) -> Segment:
        for seg in reversed(self._segments):
            gap = _compare_segments(seg, segment)
            if gap != _SEGMENTS_HAVE_GAP:
                self._segments.remove(seg)
                seg.add(segment, overwrite)
                segment = seg
        return segment

    def _insert_disconnected_segment(self, segment):
        for index, seg in enumerate(self._segments):
            if segment.addrlo < seg.addrlo:
                self._segments.insert(index, segment)
                return
        self._segments.append(segment)

    def clear(self):
        """Remove all segments from the list of segments."""
        self._segments.clear()

    def fill(self, fill: bytes):
        """Fill gaps between segments with the fill pattern."""
        for seglo, seghi in itertools.pairwise(self._segments):
            gap_width = seghi.addrlo - seglo.addrhi
            fill_repetitions = int(gap_width / len(fill)) + 1
            gapdata = fill * fill_repetitions
            gap = Segment(gapdata[:gap_width], seglo.addrhi)
            self.add(gap)

    def getrange(self, addrlo: int, addrhi: int):
        """Get the memory in the specified range."""
        keepers = []
        for seg in self._segments:
            if seg.addrhi <= addrlo or addrhi <= seg.addrlo:
                continue
            if addrlo <= seg.addrlo and seg.addrhi <= addrhi:
                keepers.append(seg)
            else:
                subseg = seg.subsegment(addrlo, addrhi)
                if subseg.size:
                    keepers.append(subseg)
        return keepers

    def __iter__(self) -> Iterator[Segment]:
        """Returns an iterator for the list of segments."""
        return self._segments.__iter__()

    def __len__(self) -> int:
        """Return the number of items in the list of segments."""
        return len(self._segments)

    def remove(self, addrlo: int, addrhi: int):
        """Remove the memory in the specified range."""
        keepers = []
        for seg in self._segments:
            if addrlo <= seg.addrlo and seg.addrhi <= addrhi:
                continue
            if seg.addrhi <= addrlo or addrhi <= seg.addrlo:
                keepers.append(seg)
            else:
                segrange = range(seg.addrlo, seg.addrhi)
                if addrlo in segrange:
                    subseg = seg.subsegment(seg.addrlo, addrlo)
                    if subseg:
                        keepers.append(subseg)
                if addrhi in segrange:
                    subseg = seg.subsegment(addrhi, seg.addrhi)
                    if subseg:
                        keepers.append(subseg)
        self._segments = keepers


def _compare_segments(seg1: Segment, seg2: Segment):
    """Determine the space between two segments.

    Returns _SEGMENTS_HAVE_GAP if there is unspecified memory space between the segments.
    Returns _SEGMENTS_OVERLAP if the sagments share some of the same memory space.
    Returns _SEGMENTS_ARE_ADJACENT if one segment starts where the other one ends.
    """
    if seg1.addrlo == seg2.addrhi or seg2.addrlo == seg1.addrhi:
        return _SEGMENTS_ARE_ADJACENT
    if seg1.addrlo < seg2.addrhi and seg2.addrlo < seg1.addrhi:
        return _SEGMENTS_OVERLAP
    return _SEGMENTS_HAVE_GAP
