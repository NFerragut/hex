"""Unit tests for the Segment class."""

import pytest

from segment import Segment, DataCollisionError, NonSequentialDataError


class Test0Constructor:
    """Unit tests for the Segment class constructor."""

    @staticmethod
    def test_constructor_default():
        """Default constructor should create empty segment at address zero."""
        seg = Segment()
        assert isinstance(seg, Segment)
        assert seg.addrlo == 0
        assert seg.addrhi == 0
        assert seg.size == 0
        assert seg.data == b''

    @staticmethod
    def test_constructor_copy(seg12):
        """Copy constructor should duplicate data and address."""
        seg = Segment(seg12)
        assert isinstance(seg, Segment)
        assert seg is not seg12
        assert seg.addrlo == 10
        assert seg.addrhi == 20
        assert seg.size == 10
        assert seg.data == bytes(range(12, 22))

    @staticmethod
    def test_constructor_with_none():
        """Constructor with None data should create empty segment at address zero."""
        seg = Segment(None)
        assert seg.addrlo == 0
        assert seg.addrhi == 0
        assert seg.size == 0
        assert seg.data == b''

    @staticmethod
    def test_constructor_with_bytearray():
        """Constructor with bytearray should create segment at address zero."""
        data = bytearray(b'mike')
        seg = Segment(data)
        assert isinstance(seg, Segment)
        assert seg.addrlo == 0
        assert seg.addrhi == len(data)
        assert seg.size == len(data)
        assert seg.data == data

    @staticmethod
    def test_constructor_with_bytes():
        """Constructor with bytes should create segment at address zero."""
        data = b'mike'
        seg = Segment(data)
        assert isinstance(seg, Segment)
        assert seg.addrlo == 0
        assert seg.addrhi == len(data)
        assert seg.size == len(data)
        assert seg.data == data

    @staticmethod
    def test_constructor_with_empty_bytes():
        """Constructor with empty data should create segment at address zero."""
        seg = Segment(b'')
        assert isinstance(seg, Segment)
        assert seg.addrlo == 0
        assert seg.addrhi == 0
        assert seg.size == 0
        assert seg.data == b''

    @staticmethod
    def test_constructor_with_array():
        """Constructor with array should create segment at address zero."""
        data = [109, 105, 107, 101]
        seg = Segment(data)
        assert isinstance(seg, Segment)
        assert seg.addrlo == 0
        assert seg.addrhi == len(data)
        assert seg.size == len(data)
        assert seg.data == bytes(data)

    @staticmethod
    def test_constructor_with_tuple():
        """Constructor with tuple should create segment at address zero."""
        data = (109, 105, 107, 101)
        seg = Segment(data)
        assert isinstance(seg, Segment)
        assert seg.addrlo == 0
        assert seg.addrhi == len(data)
        assert seg.size == len(data)
        assert seg.data == bytes(data)

    @staticmethod
    def test_constructor_with_int():
        """Constructor with int should create segment at address zero."""
        seg = Segment(5)
        assert isinstance(seg, Segment)
        assert seg.addrlo == 0
        assert seg.addrhi == 1
        assert seg.size == 1
        assert seg.data == bytes([5])

    @staticmethod
    def test_constructor_with_data_and_address_none():
        """Constructor with data and address None should create segment at address zero."""
        data = b'mike'
        seg = Segment(data, None)
        assert seg.addrlo == 0
        assert seg.addrhi == len(data)
        assert seg.size == len(data)
        assert seg.data == data

    @staticmethod
    def test_constructor_with_data_and_address_int():
        """Constructor with data and int address should create segment at int address."""
        data = b'mike'
        seg = Segment(data, 100)
        assert seg.addrlo == 100
        assert seg.addrhi == 100 + len(data)
        assert seg.size == len(data)
        assert seg.data == data

    @staticmethod
    def test_constructor_with_data_and_address_too_large():
        """Constructor with data and address too large should raise ValueError."""
        with pytest.raises(ValueError):
            Segment(b'mike', 0x100000000)

    @staticmethod
    def test_constructor_with_data_and_address_too_small():
        """Constructor with data and address too small should raise ValueError."""
        with pytest.raises(ValueError):
            Segment(b'mike', -5)

    @staticmethod
    def test_constructor_with_data_and_wrong_type_address():
        """Constructor with data and wrong type of address should raise TypeError."""
        with pytest.raises(TypeError):
            Segment(b'mike', [5])
        with pytest.raises(TypeError):
            Segment(b'mike', range(1, 5))
        with pytest.raises(ValueError):  # TODO: ValueError instead of TypeError?
            Segment(b'mike', b'mike')
        with pytest.raises(ValueError):  # TODO: ValueError instead of TypeError?
            Segment(b'mike', bytearray(b'mike'))
        with pytest.raises(TypeError):
            Segment(b'mike', set(1, 2, 3))
        with pytest.raises(TypeError):
            Segment(b'mike', {'count': 5})

    @staticmethod
    def test_constructor_with_wrong_type_data_and_valid_address():
        """Constructor with wrong type of data and valid address should raise TypeError."""
        with pytest.raises(TypeError):
            Segment(5.5, 5)
        with pytest.raises(TypeError):
            Segment('', 5)
        with pytest.raises(TypeError):
            Segment(set(1, 2, 3), 5)
        with pytest.raises(TypeError):
            Segment({'data': 'mike'}, 5)
        with pytest.raises(TypeError):
            Segment(['m', 'i', 'k', 'e'], 5)
        with pytest.raises(TypeError):
            Segment(('m', 'i', 'k', 'e'), 5)


class Test1ComparisonMethods:
    """Unit tests for methods that compare segments."""

    # @staticmethod
    # def test_cancombine_with_adjacent_segments(seg12, seg23):
    #     """CanCombine should return True if the segments are adjacent."""
    #     # seg12     10|12->21|20
    #     # seg23             20|21->30|30
    #     assert seg12.cancombine(seg23)
    #     assert seg12.cancombine(seg23, overwrite=True)
    #     assert seg12.cancombine(seg23, overwrite=False)
    #     assert seg23.cancombine(seg12)
    #     assert seg23.cancombine(seg12, overwrite=True)
    #     assert seg23.cancombine(seg12, overwrite=False)

    # @staticmethod
    # def test_cancombine_with_non_overlapping_segments(seg12, seg34):
    #     """CanCombine should return False if the segments are non-overlapping."""
    #     # seg12     10|12->21|20
    #     # seg34                     30|31->40|40
    #     assert not seg12.cancombine(seg34)
    #     assert not seg12.cancombine(seg34, overwrite=True)
    #     assert not seg12.cancombine(seg34, overwrite=False)
    #     assert not seg34.cancombine(seg12)
    #     assert not seg34.cancombine(seg12, overwrite=True)
    #     assert not seg34.cancombine(seg12, overwrite=False)

    # @staticmethod
    # def test_cancombine_with_overlapping_segments_with_overwrite(seg12, seg23, seg34, seg14):
    #     """CanCombine with overwrite should return True if the segments share any addresses."""
    #     # seg12     10|12->21|20
    #     # seg23             20|21->30|30
    #     # seg34                     30|31->40|40
    #     # seg14     10|14----------------->43|40
    #     assert seg12.cancombine(seg14, overwrite=True)
    #     assert seg23.cancombine(seg14, overwrite=True)
    #     assert seg34.cancombine(seg14, overwrite=True)
    #     assert seg14.cancombine(seg12, overwrite=True)
    #     assert seg14.cancombine(seg23, overwrite=True)
    #     assert seg14.cancombine(seg34, overwrite=True)

    # @staticmethod
    # def test_cancombine_with_overlapping_segments_without_overwrite(seg12, seg23, seg34, seg14):
    #     """CanCombine without overwrite should return False if the segments share any addresses."""
    #     # seg12     10|12->21|20
    #     # seg23             20|21->30|30
    #     # seg34                     30|31->40|40
    #     # seg14     10|14----------------->43|40
    #     assert not seg12.cancombine(seg14, overwrite=False)
    #     assert not seg23.cancombine(seg14, overwrite=False)
    #     assert not seg34.cancombine(seg14, overwrite=False)
    #     assert not seg14.cancombine(seg12, overwrite=False)
    #     assert not seg14.cancombine(seg23, overwrite=False)
    #     assert not seg14.cancombine(seg34, overwrite=False)

    # @staticmethod
    # def test_contains_with_non_overlapping_parts(seg34):
    #     """Contains with non-overlapping parts should return False."""
    #     # seg34                     30|31->40|40
    #     seg = Segment(range(26, 35), 25)
    #     assert not seg34.contains(seg)

    #     seg = Segment(range(26, 45), 25)
    #     assert not seg34.contains(seg)

    #     seg = Segment(range(36, 45), 35)
    #     assert not seg34.contains(seg)

    # @staticmethod
    # def test_contains_with_subsegments_with_different_data(seg23):
    #     """Contains with subsegments with different data should return False."""
    #     # seg23             20|21->30|30
    #     seg = Segment(range(22, 26), 20)
    #     assert not seg23.contains(seg)

    #     seg = Segment(range(25, 30), 22)
    #     assert not seg23.contains(seg)

    #     seg = Segment(range(25, 29), 25)
    #     assert not seg23.contains(seg)

    # @staticmethod
    # def test_contains_with_subsegments_with_same_data(seg23):
    #     """Contains with subsegments with same data should return True."""
    #     # seg23             20|21->30|30
    #     seg = Segment(range(21, 25), 20)
    #     assert seg23.contains(seg)

    #     seg = Segment(range(23, 28), 22)
    #     assert seg23.contains(seg)

    #     seg = Segment(range(26, 30), 25)
    #     assert seg23.contains(seg)

    # @staticmethod
    # def test_contains_with_same_segment(seg23):
    #     """Contains with same segment should return True."""
    #     # seg23             20|21->30|30
    #     seg = Segment(seg23)
    #     assert seg23.contains(seg)

    @staticmethod
    def test_isadjacent_with_adjacent_segments(seg12, seg23):
        """Adjacent should return True with segments that are adjacent."""
        # seg12     10|12->21|20
        # seg23             20|21->30|30
        assert seg12.isadjacent(seg23)
        assert seg23.isadjacent(seg12)

    @staticmethod
    def test_isadjacent_with_non_overlapping_segments(seg12, seg34):
        """Adjacent should return False with segments that have a gap between them."""
        # seg12     10|12->21|20
        # seg34                     30|31->40|40
        assert not seg12.isadjacent(seg34)
        assert not seg34.isadjacent(seg12)

    @staticmethod
    def test_isadjacent_with_overlapping_segments(seg12, seg13):
        """Adjacent should return False with segments that share any addresses."""
        # seg12     10|12->21|20
        # seg13     10|13--------->32|30
        assert not seg12.isadjacent(seg13)
        assert not seg13.isadjacent(seg12)

    @staticmethod
    def test_overlaps_with_adjacent_segments(seg12, seg23):
        """Overlaps should return False with adjacent segments."""
        # seg12     10|12->21|20
        # seg23             20|21->30|30
        assert not seg12.overlaps(seg23)
        assert not seg23.overlaps(seg12)

    @staticmethod
    def test_overlaps_with_non_overlapping_segments(seg12, seg34):
        """Overlaps should return False with segments that have a gap between them."""
        # seg12     10|12->21|20
        # seg34                     30|31->40|40
        assert not seg12.overlaps(seg34)
        assert not seg34.overlaps(seg12)

    @staticmethod
    def test_overlaps_with_overlapping_segments(seg12, seg13):
        """Overlaps should return True with segments that share any addresses."""
        # seg12     10|12->21|20
        # seg13     10|13--------->32|30
        assert seg12.overlaps(seg13)
        assert seg13.overlaps(seg12)


class Test2CombineMethods:
    """Unit tests for methods that combine multiple segments."""

    @staticmethod
    def test_add_separated_segment(seg12, seg34):
        """Add segment separated by a gap should raise NonSequentialDataError."""
        # seg12     10|12->21|20
        # seg34                     30|31->40|40
        with pytest.raises(NonSequentialDataError):
            seg34.add(seg12, overwrite=False)
        with pytest.raises(NonSequentialDataError):
            seg34.add(seg12, overwrite=True)
        with pytest.raises(NonSequentialDataError):
            seg12.add(seg34, overwrite=False)
        with pytest.raises(NonSequentialDataError):
            seg12.add(seg34, overwrite=True)

    @staticmethod
    def test_add_higher_adjacent_segment_with_overwrite(seg12, seg23):
        """Add higher adjacent segment with overwrite should combine segments."""
        # seg12     10|12->21|20
        # seg23             20|21->30|30
        seg12.add(seg23, overwrite=True)
        assert seg12.addrlo == 10
        assert seg12.addrhi == 30
        assert seg12.size == 20
        assert seg12.data == bytes(range(12, 22)) + bytes(range(21, 31))

    @staticmethod
    def test_add_higher_adjacent_segment_without_overwrite(seg12, seg23):
        """Add higher adjacent segment without overwrite should combine segments."""
        # seg12     10|12->21|20
        # seg23             20|21->30|30
        seg12.add(seg23, overwrite=False)
        assert seg12.addrlo == 10
        assert seg12.addrhi == 30
        assert seg12.size == 20
        assert seg12.data == bytes(range(12, 22)) + bytes(range(21, 31))

    @staticmethod
    def test_add_lower_adjacent_segment_with_overwrite(seg12, seg23):
        """Add lower adjacent segment with overwrite should combine segments."""
        # seg23             20|21->30|30
        # seg12     10|12->21|20
        seg23.add(seg12, overwrite=True)
        assert seg23.addrlo == 10
        assert seg23.addrhi == 30
        assert seg23.size == 20
        assert seg23.data == bytes(range(12, 22)) + bytes(range(21, 31))

    @staticmethod
    def test_add_lower_adjacent_segment_without_overwrite(seg12, seg23):
        """Add lower adjacent segment without ovewrite should combine segments."""
        # seg23             20|21->30|30
        # seg12     10|12->21|20
        seg23.add(seg12, overwrite=False)
        assert seg23.addrlo == 10
        assert seg23.addrhi == 30
        assert seg23.size == 20
        assert seg23.data == bytes(range(12, 22)) + bytes(range(21, 31))

    @staticmethod
    def test_add_overlapping_segment_without_overwrite(seg13, seg23, seg24, seg14, seg14a):
        """Add overlapping segment without overwrite should raise DataCollisionError."""
        # seg13     10|13--------->32|30
        # seg23             20|21->30|30
        # seg24             20|22--------->41|40
        # seg14     10|14----------------->43|40
        # seg14a    10|15----------------->44|40
        with pytest.raises(DataCollisionError):
            seg13.add(seg14, overwrite=False)
        with pytest.raises(DataCollisionError):
            seg23.add(seg14, overwrite=False)
        with pytest.raises(DataCollisionError):
            seg24.add(seg14, overwrite=False)
        with pytest.raises(DataCollisionError):
            seg14.add(seg13, overwrite=False)
        with pytest.raises(DataCollisionError):
            seg14.add(seg23, overwrite=False)
        with pytest.raises(DataCollisionError):
            seg14.add(seg24, overwrite=False)
        with pytest.raises(DataCollisionError):
            seg14.add(seg14a, overwrite=False)

        # seg13     10|13--------->32|30
        # seg24             20|22--------->41|40
        with pytest.raises(DataCollisionError):
            seg13.add(seg24, overwrite=False)
        with pytest.raises(DataCollisionError):
            seg24.add(seg13, overwrite=False)

    @staticmethod
    def test_add_center_aligned_larger_segment(seg14, seg23):
        """Add center-aligned larger segment should replace whole segment."""
        # seg23             20|21->30|30
        # seg14     10|14----------------->43|40
        seg23.add(seg14, overwrite=True)
        assert seg23.addrlo == 10
        assert seg23.addrhi == 40
        assert seg23.size == 30
        assert seg23.data == bytes(range(14, 44))

    @staticmethod
    def test_add_center_aligned_smaller_segment(seg14, seg23):
        """Add center-aligned smaller segment should replace part of segment."""
        # seg14     10|14----------------->43|40
        # seg23             20|21->30|30
        seg14.add(seg23, overwrite=True)
        assert seg14.addrlo == 10
        assert seg14.addrhi == 40
        assert seg14.size == 30
        assert seg14.data == bytes(range(14, 24)) + bytes(range(21, 31)) + bytes(range(34, 44))

    @staticmethod
    def test_add_left_aligned_larger_segment(seg12, seg13):
        """Add left-aligned larger segment should replace whole segment."""
        # seg12     10|12->21|20
        # seg13     10|13--------->32|30
        seg12.add(seg13, overwrite=True)
        assert seg12.addrlo == 10
        assert seg12.addrhi == 30
        assert seg12.size == 20
        assert seg12.data == bytes(range(13, 33))

    @staticmethod
    def test_add_left_aligned_smaller_segment(seg12, seg13):
        """Add left-aligned smaller segment should replace part of segment."""
        # seg13     10|13--------->32|30
        # seg12     10|12->21|20
        seg13.add(seg12, overwrite=True)
        assert seg13.addrlo == 10
        assert seg13.addrhi == 30
        assert seg13.size == 20
        assert seg13.data == bytes(range(12, 22)) + bytes(range(23, 33))

    @staticmethod
    def test_add_left_overlapping_segment(seg13, seg24):
        """Add segment that overlaps the left side should replace the left side."""
        # seg24             20|22--------->41|40
        # seg13     10|13--------->32|30
        seg24.add(seg13, overwrite=True)
        assert seg24.addrlo == 10
        assert seg24.addrhi == 40
        assert seg24.size == 30
        assert seg24.data == bytes(range(13, 33)) + bytes(range(32, 42))

    @staticmethod
    def test_add_right_overlapping_segment(seg13, seg24):
        """Add segment that overlaps the right side should replace the right side."""
        # seg13     10|13--------->32|30
        # seg24             20|22--------->41|40
        seg13.add(seg24, overwrite=True)
        assert seg13.addrlo == 10
        assert seg13.addrhi == 40
        assert seg13.size == 30
        assert seg13.data == bytes(range(13, 23)) + bytes(range(22, 42))

    @staticmethod
    def test_add_right_aligned_larger_segment(seg24, seg34):
        """Add right-aligned larger segment should replace whole segment."""
        # seg34                     30|31->40|40
        # seg24             20|22--------->41|40
        seg34.add(seg24, overwrite=True)
        assert seg34.addrlo == 20
        assert seg34.addrhi == 40
        assert seg34.size == 20
        assert seg34.data == bytes(range(22, 42))

    @staticmethod
    def test_add_right_aligned_smaller_segment(seg24, seg34):
        """Add right-aligned smaller segment should replace part of segment."""
        # seg24             20|22--------->41|40
        # seg34                     30|31->40|40
        seg24.add(seg34, overwrite=True)
        assert seg24.addrlo == 20
        assert seg24.addrhi == 40
        assert seg24.size == 20
        assert seg24.data == bytes(range(22, 32)) + bytes(range(31, 41))

    @staticmethod
    def test_add_center_aligned_same_sized_segment(seg14, seg14a):
        """Add same-size and same address segment should replace whole segment."""
        # seg14     10|14----------------->43|40
        # seg14a    10|15----------------->44|40
        seg14.add(seg14a, overwrite=True)
        assert seg14.addrlo == 10
        assert seg14.addrhi == 40
        assert seg14.size == 30
        assert seg14.data == bytes(range(15, 45))


class Test3SplitMethods:
    """Unit tests for methods that break up segments."""

    @staticmethod
    def test_subsegment_separated_address_space(seg14):
        """Subsegment at separated address should return empty segment."""
        # seg14             10|14----------------->43|40
        # subseg     1|---|5                           45|---|50
        seg = seg14.subsegment(1, 5)
        assert seg.size == 0
        assert seg.data == b''

        seg = seg14.subsegment(45, 50)
        assert seg.size == 0
        assert seg.data == b''

    @staticmethod
    def test_subsegment_adjacent_address_space(seg14):
        """Subsegment at adjacent address should return empty segment."""
        # seg14             10|14----------------->43|40
        # subseg     1|------|10                    40|------|50
        seg = seg14.subsegment(1, 10)
        assert seg.size == 0
        assert seg.data == b''

        seg = seg14.subsegment(40, 50)
        assert seg.size == 0
        assert seg.data == b''

    @staticmethod
    def test_subsegment_left_overlap_address_space(seg14):
        """Subsegment at left overlapping address should return left part of segment."""
        # seg14             10|14----------------->43|40
        # subseg      1|-------------|20
        seg = seg14.subsegment(1, 20)
        assert seg.addrlo == 10
        assert seg.addrhi == 20
        assert seg.size == 10
        assert seg.data == bytes(range(14, 24))

    @staticmethod
    def test_subsegment_right_overlap_address_space(seg14):
        """Subsegment at right overlapping address should return right part of segment."""
        # seg14     10|14----------------->43|40
        # subseg                    30|-------------|50
        seg = seg14.subsegment(30, 50)
        assert seg.addrlo == 30
        assert seg.addrhi == 40
        assert seg.size == 10
        assert seg.data == bytes(range(34, 44))

    @staticmethod
    def test_subsegment_full_overlap_address_space(seg14):
        """Subsegment at fully overlapping address should return whole segment."""
        # seg14             10|14----------------->43|40
        # subseg      1|------------------------------------|50
        seg = seg14.subsegment(10, 50)
        assert seg != seg14
        assert seg.addrlo == 10
        assert seg.addrhi == 40
        assert seg.size == 30
        assert seg.data == bytes(range(14, 44))

    @staticmethod
    def test_subsegment_centered_partial_overlap_address_space(seg14):
        """Subsegment at internal address should return internal part of segment."""
        # seg14     10|14----------------->43|40
        # subseg            20|------|30
        seg = seg14.subsegment(20, 30)
        assert seg != seg14
        assert seg.addrlo == 20
        assert seg.addrhi == 30
        assert seg.size == 10
        assert seg.data == bytes(range(24, 34))

    @staticmethod
    def test_split_segment(seg14):
        """Split should split the segment into equally sized segments plus the final left-overs."""
        # seg14     10|14----------------->43|40
        segments = seg14.split(12)
        assert len(segments) == 3
        assert segments[0].addrlo == 10
        assert segments[0].addrhi == 22
        assert segments[0].size == 12
        assert segments[0].data == bytes(range(14, 26))
        assert segments[1].addrlo == 22
        assert segments[1].addrhi == 34
        assert segments[1].size == 12
        assert segments[1].data == bytes(range(26, 38))
        assert segments[2].addrlo == 34
        assert segments[2].addrhi == 40
        assert segments[2].size == 6
        assert segments[2].data == bytes(range(38, 44))
