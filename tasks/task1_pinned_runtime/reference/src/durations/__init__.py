"""Parse and format compact duration strings such as "1d2h3m4s"."""

import re
from typing import Optional

__all__ = ["parse_duration", "format_duration"]

UNIT_SECONDS = {"d": 86400, "h": 3600, "m": 60, "s": 1}

# Units d, h, m, s, each at most once, in descending order, each with a
# non-negative integer written in ASCII digits. At least one unit is required.
_DURATION_RE = re.compile(
    r"(?:(?P<d>[0-9]+)d)?"
    r"(?:(?P<h>[0-9]+)h)?"
    r"(?:(?P<m>[0-9]+)m)?"
    r"(?:(?P<s>[0-9]+)s)?"
)


def parse_duration(text: str) -> int:
    """Return the number of seconds in a duration string such as "1d2h3m4s".

    Accepted: the units d, h, m and s, each at most once and in that order,
    each preceded by a non-negative integer. Examples: "1d2h3m4s", "25h",
    "90m", "0s".

    Raises TypeError if text is not a string, and ValueError for any string
    that does not match the format above (including the empty string).
    """
    if not isinstance(text, str):
        raise TypeError(f"expected a string, got {type(text).__name__}")
    match = _DURATION_RE.fullmatch(text)
    if match is None or not any(match.groupdict().values()):
        raise ValueError(f"invalid duration: {text!r}")
    total = 0
    for unit, value in match.groupdict().items():
        if value is not None:
            total += int(value) * UNIT_SECONDS[unit]
    return total


_UNIT_ORDER = ("d", "h", "m", "s")


def format_duration(seconds: int, *, largest_unit: str = "d", max_parts: Optional[int] = None) -> str:
    """Return a compact duration string for a number of seconds.

    seconds: a non-negative int (not a bool).
    largest_unit: "d", "h", "m" or "s". Larger units are folded into it.
    max_parts: None, or an int >= 1. Keeps only the first max_parts non-zero
    components and drops the rest, without rounding.
    """
    if isinstance(seconds, bool) or not isinstance(seconds, int):
        raise TypeError(f"seconds must be an int, got {type(seconds).__name__}")
    if seconds < 0:
        raise ValueError("seconds must not be negative")
    if not isinstance(largest_unit, str) or largest_unit not in UNIT_SECONDS:
        raise ValueError(f"largest_unit must be one of 'd', 'h', 'm', 's', got {largest_unit!r}")
    if max_parts is not None:
        if isinstance(max_parts, bool) or not isinstance(max_parts, int):
            raise TypeError(f"max_parts must be an int or None, got {type(max_parts).__name__}")
        if max_parts < 1:
            raise ValueError("max_parts must be at least 1")

    if seconds == 0:
        return "0s"

    units = _UNIT_ORDER[_UNIT_ORDER.index(largest_unit):]
    parts = []
    remaining = seconds
    for unit in units:
        value, remaining = divmod(remaining, UNIT_SECONDS[unit])
        if value:
            parts.append(f"{value}{unit}")
    if max_parts is not None:
        parts = parts[:max_parts]
    return "".join(parts)
