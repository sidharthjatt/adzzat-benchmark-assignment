"""Hidden tests for Task 1 (pinned runtime). Trusted: never shown to the agent.

Only the standard library and pytest are used. The random values come from a
fixed seed, so every run checks the same inputs.
"""

import random

import pytest

from durations import format_duration, parse_duration

SEED = 20261123
UNITS = ("d", "h", "m", "s")
UNIT_SECONDS = {"d": 86400, "h": 3600, "m": 60, "s": 1}


def expected_format(seconds, largest_unit="d", max_parts=None):
    """Independent oracle written directly from the contract."""
    if seconds == 0:
        return "0s"
    out = []
    remaining = seconds
    for unit in UNITS[UNITS.index(largest_unit):]:
        size = UNIT_SECONDS[unit]
        value = remaining // size
        remaining -= value * size
        if value:
            out.append(str(value) + unit)
    if max_parts is not None:
        out = out[:max_parts]
    return "".join(out)


# ---------------------------------------------------------------- examples

@pytest.mark.parametrize(
    "seconds, kwargs, expected",
    [
        (93784, {}, "1d2h3m4s"),
        (0, {}, "0s"),
        (90000, {"largest_unit": "h"}, "25h"),
        (3725, {"max_parts": 1}, "1h"),
        (1, {}, "1s"),
        (86404, {}, "1d4s"),
        (3601, {}, "1h1s"),
        (90061, {}, "1d1h1m1s"),
    ],
)
def test_contract_examples(seconds, kwargs, expected):
    assert format_duration(seconds, **kwargs) == expected


# ---------------------------------------------------------------- boundaries

BOUNDARIES = {
    59: {"d": "59s", "h": "59s", "m": "59s", "s": "59s"},
    60: {"d": "1m", "h": "1m", "m": "1m", "s": "60s"},
    3599: {"d": "59m59s", "h": "59m59s", "m": "59m59s", "s": "3599s"},
    3600: {"d": "1h", "h": "1h", "m": "60m", "s": "3600s"},
    86399: {"d": "23h59m59s", "h": "23h59m59s", "m": "1439m59s", "s": "86399s"},
    86400: {"d": "1d", "h": "24h", "m": "1440m", "s": "86400s"},
}


@pytest.mark.parametrize("seconds", sorted(BOUNDARIES))
@pytest.mark.parametrize("unit", UNITS)
def test_boundaries_for_every_largest_unit(seconds, unit):
    assert format_duration(seconds, largest_unit=unit) == BOUNDARIES[seconds][unit]


@pytest.mark.parametrize("unit", UNITS)
def test_zero_for_every_largest_unit(unit):
    assert format_duration(0, largest_unit=unit) == "0s"


def test_default_largest_unit_is_days():
    assert format_duration(2 * 86400 + 5) == "2d5s"


def test_large_value():
    assert format_duration(10**9) == "11574d1h46m40s"
    assert format_duration(10**9, largest_unit="s") == "1000000000s"


# ---------------------------------------------------------------- max_parts

@pytest.mark.parametrize(
    "seconds, unit, max_parts, expected",
    [
        (93784, "d", 1, "1d"),
        (93784, "d", 2, "1d2h"),
        (93784, "d", 3, "1d2h3m"),
        (93784, "d", 4, "1d2h3m4s"),
        (93784, "h", 1, "26h"),
        (93784, "h", 2, "26h3m"),
        (93784, "m", 1, "1563m"),
        (93784, "s", 1, "93784s"),
        # truncation, never rounding
        (7140, "d", 1, "1h"),            # 1h59m
        (7199, "d", 2, "1h59m"),         # 1h59m59s
        (86399, "d", 1, "23h"),
        (86399, "d", 2, "23h59m"),
        (172799, "d", 1, "1d"),          # 1d23h59m59s
        (89, "d", 1, "1m"),              # 1m29s
        (119, "m", 1, "1m"),             # 1m59s
        # zero components are skipped before counting
        (3601, "d", 1, "1h"),
        (3601, "d", 2, "1h1s"),
        (86401, "d", 2, "1d1s"),
        # max_parts larger than the number of non-zero components
        (3600, "d", 2, "1h"),
        (3600, "d", 4, "1h"),
        (61, "d", 3, "1m1s"),
        (0, "d", 1, "0s"),
        (0, "s", 4, "0s"),
    ],
)
def test_max_parts(seconds, unit, max_parts, expected):
    assert format_duration(seconds, largest_unit=unit, max_parts=max_parts) == expected


def test_max_parts_never_rounds_seeded():
    rng = random.Random(SEED + 1)
    for _ in range(500):
        n = rng.randrange(0, 10**9)
        unit = rng.choice(UNITS)
        parts = rng.randint(1, 4)
        assert format_duration(n, largest_unit=unit, max_parts=parts) == expected_format(n, unit, parts), (n, unit, parts)


# ---------------------------------------------------------------- errors

@pytest.mark.parametrize("bad", [True, False, 1.0, 3600.5, "60", None, [60]])
def test_seconds_type_error(bad):
    with pytest.raises(TypeError):
        format_duration(bad)


@pytest.mark.parametrize("bad", [-1, -86400])
def test_seconds_negative(bad):
    with pytest.raises(ValueError):
        format_duration(bad)


@pytest.mark.parametrize("bad", ["x", "D", "", "days", "ms", None])
def test_largest_unit_value_error(bad):
    with pytest.raises(ValueError):
        format_duration(60, largest_unit=bad)


@pytest.mark.parametrize("bad", [True, False, 1.0, "2"])
def test_max_parts_type_error(bad):
    with pytest.raises(TypeError):
        format_duration(60, max_parts=bad)


@pytest.mark.parametrize("bad", [0, -1])
def test_max_parts_value_error(bad):
    with pytest.raises(ValueError):
        format_duration(60, max_parts=bad)


def test_options_are_keyword_only():
    with pytest.raises(TypeError):
        format_duration(60, "h")  # type: ignore[misc]


# ---------------------------------------------------------------- round trip

@pytest.mark.parametrize("unit", UNITS)
def test_round_trip_seeded(unit):
    rng = random.Random(SEED)
    values = [rng.randint(0, 10**9) for _ in range(2000)]
    for n in values:
        text = format_duration(n, largest_unit=unit)
        assert parse_duration(text) == n, (n, unit, text)
        assert text == expected_format(n, unit), (n, unit, text)


# ---------------------------------------------------------------- parse_duration unchanged

@pytest.mark.parametrize(
    "text, expected",
    [("1d2h3m4s", 93784), ("25h", 90000), ("90m", 5400), ("0s", 0), ("0d", 0),
     ("1000000000s", 10**9), ("1d1s", 86401), ("2h30m", 9000)],
)
def test_parse_duration_unchanged_valid(text, expected):
    assert parse_duration(text) == expected


@pytest.mark.parametrize(
    "text", ["", "1h1d", "1h1h", "1s1m", "5x", "-1s", " 1s", "1s ", "1.5h", "h", "1 h", "1H", "1d2h3m4s5"],
)
def test_parse_duration_unchanged_invalid(text):
    with pytest.raises(ValueError):
        parse_duration(text)
