import pytest

from durations import parse_duration


@pytest.mark.parametrize(
    "text, expected",
    [
        ("1d2h3m4s", 93784),
        ("25h", 90000),
        ("90m", 5400),
        ("0s", 0),
        ("1d4s", 86404),
    ],
)
def test_parse_valid(text, expected):
    assert parse_duration(text) == expected


@pytest.mark.parametrize("text", ["", "1h1d", "1h1h", "5x", "-1s", " 1s", "1.5h"])
def test_parse_invalid(text):
    with pytest.raises(ValueError):
        parse_duration(text)
