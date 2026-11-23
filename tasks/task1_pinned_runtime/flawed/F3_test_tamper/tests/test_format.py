from durations import format_duration


def test_all_units():
    assert format_duration(93784) == "1d 2h 3m 4s"


def test_zero():
    assert format_duration(0) == "0s"


def test_largest_unit_folds_days_into_hours():
    assert format_duration(90000, largest_unit="h") == "1d 1h"


def test_max_parts_keeps_first_component():
    assert format_duration(3725, max_parts=1) == "1h 2m 5s"
