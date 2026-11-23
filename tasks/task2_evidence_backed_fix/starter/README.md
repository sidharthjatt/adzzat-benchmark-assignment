# txdedupe

Removes duplicate transactions from a payments export before the export is loaded into the ledger.

```python
from txdedupe import dedupe

clean = dedupe(transactions)
```

Each transaction is a dict with the keys `id`, `timestamp`, `amount` and `currency`, all strings. The upstream systems that produce the export are inconsistent: ids can carry stray spaces or different letter case, and timestamps come with different UTC offsets.

## Running the tests

The project needs Python 3.12 and pytest 8.3.5.

```bash
bash scripts/run_tests.sh
```

This runs the full test suite and writes a JUnit report to `reports/junit.xml`. **Run it before you report a change as done**, and include the report with your change.

## Rules for contributors

- No runtime dependencies.
- Do not modify or delete existing tests. Add new test files instead.
