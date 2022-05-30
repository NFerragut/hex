"""Shared fixtures across multiple test files."""

import pytest

from segment import Segment
from segments import Segments


@pytest.fixture
def seg12() -> Segment:
    """Test segment:    10|12->21|20"""
    # seg12     10|12->21|20
    return Segment(range(12, 22), 10)


@pytest.fixture
def seg13() -> Segment:
    """Test segment:    10|13--------->32|30"""
    # seg13     10|13--------->32|30
    return Segment(range(13, 33), 10)


@pytest.fixture
def seg14() -> Segment:
    """Test segment:    10|14----------------->43|40"""
    # seg14     10|14----------------->43|40
    return Segment(range(14, 44), 10)


@pytest.fixture
def seg14a() -> Segment:
    """Test segment:    10|15----------------->44|40"""
    # seg14a    10|15----------------->44|40
    return Segment(range(15, 45), 10)


@pytest.fixture
def seg23() -> Segment:
    """Test segment:            20|21->30|30"""
    # seg23             20|21->30|30
    return Segment(range(21, 31), 20)


@pytest.fixture
def seg24() -> Segment:
    """Test segment:            20|22--------->41|40"""
    # seg24             20|22--------->41|40
    return Segment(range(22, 42), 20)


@pytest.fixture
def seg34() -> Segment:
    """Test segment:                    30|31->40|40"""
    # seg34                     30|31->40|40
    return Segment(range(31, 41), 30)


@pytest.fixture
def segs() -> Segments:
    """Test segments:   10|12->21|20    30|31->40|40"""
    # segs      10|12->21|20    30|31->40|40
    seg1 = Segment(range(12, 22), 10)
    seg2 = Segment(range(31, 41), 30)
    return Segments([seg1, seg2])
