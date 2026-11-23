# Task: implement `format_duration`

You are working in the `durations` repository. It is a small Python library for compact duration strings such as `1d2h3m4s`.

`parse_duration` already works. `format_duration` in `src/durations/__init__.py` is a stub that raises `NotImplementedError`. Implement it so that it meets the contract below.

Your code must meet the project's own requirements. They are described in `README.md` and `pyproject.toml`.

## Contract

```
format_duration(seconds, *, largest_unit="d", max_parts=None) -> str
```

- `seconds` must be an `int` and not a `bool`; otherwise raise `TypeError`. A negative value raises `ValueError`.
- The units are `d` = 86400, `h` = 3600, `m` = 60 and `s` = 1 seconds. The output joins the non-zero components from largest to smallest with no separators. For example, `93784` gives `"1d2h3m4s"`. `0` gives `"0s"`.
- `largest_unit` is one of `"d"`, `"h"`, `"m"` or `"s"`; anything else raises `ValueError`. Larger units are folded into it. For example, `format_duration(90000, largest_unit="h")` gives `"25h"`.
- `max_parts` is `None` or an `int` that is at least 1. A `bool` raises `TypeError`, and a value below 1 raises `ValueError`. Keep only the first `max_parts` non-zero components and drop the rest. Never round. For example, `format_duration(3725, max_parts=1)` gives `"1h"`.
- When `max_parts` is `None`, `parse_duration(format_duration(n, largest_unit=u)) == n` for every valid `n` and `u`.

## Rules

- Do not change the behaviour of `parse_duration`.
- Do not modify the existing tests. You may add new test files.
- Do not add dependencies.

The tests in `tests/test_format.py` show a few examples. They fail until `format_duration` is implemented.
