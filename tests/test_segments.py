"""Unit tests for the Segments class."""

import pytest

from segment import Segment, DataCollisionError
from segments import Segments


class Test0Constructor:
    """Unit tests for the Segments class constructor."""

    @staticmethod
    def test_params_missing_should_return_empty_segments():
        """Default Constructor should create an empty list of segments."""
        segments = Segments()
        assert segments.addrlo == 0
        assert segments.addrhi == 0
        assert segments.span == 0
        assert len(segments) == 0

    @staticmethod
    def test_overlapping_segs_without_overwrite_should_raise_error(seg12, seg14):
        """Constructor overlapping segments without overwrite should raise DataCollisionError."""
        # seg12     10|12->21|20
        # seg14     10|14----------------->43|40
        with pytest.raises(DataCollisionError):
            Segments([seg12, seg14], False)
        with pytest.raises(DataCollisionError):
            Segments([seg12, seg14])

    @staticmethod
    def test_overlapping_segs_with_overwrite_should_not_raise_error(seg12, seg14):
        """Constructor with overlapping segments with overwrite should create list of segments."""
        # seg12     10|12->21|20
        # seg14     10|14----------------->43|40
        Segments([seg12, seg14], True)


class TestAddMethod:
    """Unit tests for the add() method."""

    @staticmethod
    def test_add_none(segs):
        """Add None should not affect the Segments object."""
        # segs      10|12->21|20    30|31->40|40
        segs.add(None)
        assert segs.addrlo == 10
        assert segs.addrhi == 40
        assert segs.span == 30
        assert len(segs) == 2
        assert segs[0].addrlo == 10
        assert segs[0].addrhi == 20
        assert segs[0].size == 10
        assert segs[0].data == bytes(range(12, 22))
        assert segs[1].addrlo == 30
        assert segs[1].addrhi == 40
        assert segs[1].size == 10
        assert segs[1].data == bytes(range(31, 41))

    @staticmethod
    def test_add_empty_array(segs):
        """Add empty array should not affect the Segments object."""
        # segs      10|12->21|20    30|31->40|40
        segs.add([])
        assert segs.addrlo == 10
        assert segs.addrhi == 40
        assert segs.span == 30
        assert len(segs) == 2
        assert segs[0].addrlo == 10
        assert segs[0].addrhi == 20
        assert segs[0].size == 10
        assert segs[0].data == bytes(range(12, 22))
        assert segs[1].addrlo == 30
        assert segs[1].addrhi == 40
        assert segs[1].size == 10
        assert segs[1].data == bytes(range(31, 41))

    @staticmethod
    def test_add_adjacent_segment_after_segment(seg12, seg23):
        """Add adjacent segment should combine segments."""
        # seg12     10|12->21|20
        # seg23             20|21->30|30
        segs = Segments([seg12])
        segs.add(seg23, False)
        assert segs.addrlo == 10
        assert segs.addrhi == 30
        assert segs.span == 20
        assert len(segs) == 1

        segs = Segments([seg12])
        segs.add(seg23, True)
        assert segs.addrlo == 10
        assert segs.addrhi == 30
        assert segs.span == 20
        assert len(segs) == 1

        segs = Segments([seg12])
        segs.add(seg23)
        assert segs.addrlo == 10
        assert segs.addrhi == 30
        assert segs.span == 20
        assert len(segs) == 1

    @staticmethod
    def test_add_adjacent_segment_between_two_segments(segs, seg23):
        """Add adjacent segment should combine with lower and upper adjacent segments."""
        # segs      10|12->21|20    30|31->40|40
        # seg23             20|21->30|30
        segs.add(seg23)
        assert segs.addrlo == 10
        assert segs.addrhi == 40
        assert segs.span == 30
        assert len(segs) == 1
        assert segs[0].addrlo == 10
        assert segs[0].addrhi == 40
        assert segs[0].size == 30
        assert segs[0].data == (bytes(range(12, 22)) + bytes(range(21, 31)) +
                                bytes(range(31, 41)))

    @staticmethod
    def test_add_overlapping_segment_with_overwrite(seg13, seg24):
        """Add overlapping segment with overwrite should replace data."""
        # seg13     10|13--------->32|30
        # seg24             20|22--------->41|40
        segs = Segments([seg13])
        segs.add(seg24, True)
        assert segs.addrlo == 10
        assert segs.addrhi == 40
        assert segs.span == 30
        assert len(segs) == 1
        assert segs[0].data == bytes(range(13, 23)) + bytes(range(22, 42))

    @staticmethod
    def test_add_separated_segment(seg12, seg34):
        """Add separated segment should sort list of segments."""
        # seg12     10|12->21|20
        # seg34                     30|31->40|40
        segs = Segments([seg12])
        segs.add(seg34)
        assert segs.addrlo == 10
        assert segs.addrhi == 40
        assert segs.span == 30
        assert len(segs) == 2
        assert segs[0].addrlo == 10
        assert segs[0].addrhi == 20
        assert segs[0].size == 10
        assert segs[0].data == bytes(range(12, 22))
        assert segs[1].addrlo == 30
        assert segs[1].addrhi == 40
        assert segs[1].size == 10
        assert segs[1].data == bytes(range(31, 41))

        segs = Segments([seg34])
        segs.add(seg12)
        assert segs.addrlo == 10
        assert segs.addrhi == 40
        assert segs.span == 30
        assert len(segs) == 2
        assert segs[0].addrlo == 10
        assert segs[0].addrhi == 20
        assert segs[0].size == 10
        assert segs[0].data == bytes(range(12, 22))
        assert segs[1].addrlo == 30
        assert segs[1].addrhi == 40
        assert segs[1].size == 10
        assert segs[1].data == bytes(range(31, 41))

    @staticmethod
    def test_add_segments(segs, seg14):
        """Add separated segments should create copies of added segments."""
        # segs      10|12->21|20    30|31->40|40
        # seg14     10|14----------------->43|40
        # seg67                                     60|60->69|70
        seg67 = Segment(range(60, 70), 60)
        segs.add([seg14, seg67], True)
        assert segs.addrlo == 10
        assert segs.addrhi == 70
        assert segs.span == 60
        assert len(segs) == 2
        assert segs[0] is not seg14
        assert segs[0].addrlo == seg14.addrlo
        assert segs[0].data == seg14.data
        assert segs[1] is not seg67
        assert segs[1].addrlo == seg67.addrlo
        assert segs[1].data == seg67.data

    @staticmethod
    def test_add_overlapping_segments(segs, seg14):
        """Add overlapping segments with overwrite should replace data."""
        # segs      10|12->21|20    30|31->40|40
        # seg14     10|14----------------->43|40
        # seg67                                     60|60->69|70
        seg67 = Segment(range(60, 70), 60)
        segs.add([seg14, seg67], True)
        assert segs.addrlo == 10
        assert segs.addrhi == 70
        assert segs.span == 60
        assert len(segs) == 2
        assert segs[0].addrlo == 10
        assert segs[0].addrhi == 40
        assert segs[0].size == 30
        assert segs[0].data == bytes(range(14, 44))
        assert segs[1].addrlo == 60
        assert segs[1].addrhi == 70
        assert segs[1].size == 10
        assert segs[1].data == bytes(range(60, 70))


class TestClearMethod:
    """Unit tests for the clear() method."""

    @staticmethod
    def test_clear_segments(segs):
        """Clear should remove segments from a Segments object."""
        assert len(segs) != 0
        segs.clear()
        assert len(segs) == 0

    @staticmethod
    def test_clear_empty():
        """Clear should do nothing to an empty Segments object."""
        segs = Segments()
        assert len(segs) == 0
        segs.clear()
        assert len(segs) == 0


# class TestContainsMethod:
#     """Unit tests for the contains() method."""

#     @staticmethod
#     def test_contains_subsegment(segs):
#         """Contains should return True if segment data is a subset of data in list of segments."""
#         # segs      10|12->21|20    30|31->40|40
#         seg = Segment(range(33, 38), 32)
#         assert segs.contains(seg)

#     @staticmethod
#     def test_contains_segment_in_list(segs, seg12):
#         """Contains should return True if segment is in the list of segments."""
#         # segs      10|12->21|20    30|31->40|40
#         # seg12     10|12->21|20
#         assert segs.contains(seg12)

#     @staticmethod
#     def test_contains_segment_with_non_overlapping_data(segs):
#         """Contains should return False if segment has non-overlapping section."""
#         # segs      10|12->21|20    30|31->40|40
#         seg = Segment(range(1, 5), 5)
#         assert not segs.contains(seg)

#         seg = Segment(range(26, 35), 25)
#         assert not segs.contains(seg)

#         seg = Segment(range(26, 45), 25)
#         assert not segs.contains(seg)

#         seg = Segment(range(36, 45), 35)
#         assert not segs.contains(seg)

#         seg = Segment(range(45, 50), 45)
#         assert not segs.contains(seg)


class TestKeywordMethods:
    """Unit tests for built-in keyword methods."""

    @staticmethod
    def test_keyword_in_with_segment_in_list(segs):
        """Keyword 'in' should return True if segment is in list of segments."""
        # segs      10|12->21|20    30|31->40|40
        for seg in segs:
            assert seg in segs

    @staticmethod
    def test_keyword_in_with_segment_not_in_list(segs, seg12, seg34):
        """Keyword 'in' should return False if segment is not in list of segments."""
        # segs      10|12->21|20    30|31->40|40
        # seg12     10|12->21|20
        # seg34                     30|31->40|40
        assert seg12 not in segs
        assert seg34 not in segs

    @staticmethod
    def test_keyword_reverse(segs, seg12, seg34):
        """Keyword 'reverse' should iterate through segments backwards."""
        # segs      10|12->21|20    30|31->40|40
        # seg12     10|12->21|20
        # seg34                     30|31->40|40
        index = len(segs) - 1
        for seg in reversed(segs):
            if index == 1:
                assert seg.addrlo == seg34.addrlo
                assert seg.data == seg34.data
                assert seg is not seg34
            elif index == 0:
                assert seg.addrlo == seg12.addrlo
                assert seg.data == seg12.data
                assert seg is not seg12
            else:
                pytest.fail('Unexpected number of segments.')
            index -= 1


class TestAddrloProperty:
    """Unit tests for the addrlo property."""

    @staticmethod
    def test_set_addrlo(segs):
        """Set property addrlo should relocate segments to a new address."""
        # segs      10|12->21|20    30|31->40|40
        segs.addrlo = 20
        assert segs.addrlo == 20
        assert segs.addrhi == 50
        assert segs.span == 30
        assert len(segs) == 2
        assert segs[0].addrlo == 20
        assert segs[0].addrhi == 30
        assert segs[0].size == 10
        assert segs[0].data == bytes(range(12, 22))
        assert segs[1].addrlo == 40
        assert segs[1].addrhi == 50
        assert segs[1].size == 10
        assert segs[1].data == bytes(range(31, 41))
