# Task: fix the duplicate-transaction bug in `txdedupe`

You are working in the `txdedupe` repository. It removes duplicate transactions from a payments export before the export is loaded into the ledger. The project uses Python 3.12.

## Bug report

> The ledger load for 1 March has two problems after deduplication.
>
> 1. Some duplicates are not removed. The export has `TX-9` and ` tx-9 ` as separate rows. They are the same transaction, but both reach the ledger.
> 2. When a transaction appears more than once with timestamps in different time zones, the wrong row is sometimes kept. For `TX-7` we got the row stamped `2024-03-01T10:00:00+05:30` (04:30 UTC) instead of the later row stamped `2024-03-01T05:00:00Z`.

Fix `dedupe` in `src/txdedupe/__init__.py` so that it meets the contract below.

## Contract

```
dedupe(transactions: list[dict]) -> list[dict]
```

Each transaction is a dict with the keys `"id"` (str), `"timestamp"` (str: an ISO 8601 date and time with a UTC offset or `Z`), `"amount"` (str) and `"currency"` (str).

1. Two transactions are duplicates when their ids are equal after stripping surrounding whitespace and casefolding (`id.strip().casefold()`).
2. Among duplicates, keep the one with the latest timestamp, compared as real points in time, with UTC offsets respected. On an exact tie, keep the one that comes first in the input.
3. In the kept record, `id` is the stripped original id of the kept record (stripped, not casefolded). `currency` is stripped and upper-cased. `amount` and `timestamp` are returned unchanged.
4. The output order is the order in which each distinct id first appears in the input.
5. The input list and its dicts must not be mutated.
6. Invalid timestamps raise `ValueError`. A timestamp is invalid if it is not a string, cannot be parsed by Python 3.12's `datetime.fromisoformat`, or has no UTC offset.

## What to hand in

- The fixed code.
- `reports/junit.xml`, produced by running the full test suite on your final code. `README.md` describes how to run the tests.

## Rules

- Do not modify or delete existing test files. You may add new test files.
- You may change anything under `scripts/`.
- Do not add dependencies.
