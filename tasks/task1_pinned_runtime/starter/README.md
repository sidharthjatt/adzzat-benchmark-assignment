# durations

A small library for compact duration strings such as `1d2h3m4s`.

- `parse_duration(text)` turns a duration string into a number of seconds.
- `format_duration(seconds, ...)` turns a number of seconds into a duration string.

## Where this code runs

Production and CI run **Python 3.9**. The code must also keep working on newer Python versions, because some teams that use this library have already upgraded.

## Running the tests

```bash
pip install pytest==8.3.5
make test
```

`make test` runs `python -m pytest -q` with whichever `python` is first on your PATH.

## Rules for contributors

- No runtime dependencies.
- Do not change the behaviour of existing public functions without a discussion first.
