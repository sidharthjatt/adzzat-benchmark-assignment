"""Hidden tests for Task 2 (evidence-backed fix). Trusted: never shown to the agent.

Only the standard library and pytest are used. Random inputs come from a fixed
seed, so every run checks the same inputs.
"""

import copy
import random
from datetime import datetime, timedelta, timezone

import pytest

from txdedupe import dedupe

SEED = 20261124


def tx(id_, timestamp, amount="10.00", currency="EUR"):
    return {"id": id_, "timestamp": timestamp, "amount": amount, "currency": currency}


def out(id_, timestamp, amount="10.00", currency="EUR"):
    return tx(id_, timestamp, amount, currency)


def oracle(transactions):
    """Independent implementation written directly from the contract."""
    best = {}
    order = []
    for index, t in enumerate(transactions):
        key = t["id"].strip().casefold()
        moment = datetime.fromisoformat(t["timestamp"])
        if key not in best:
            order.append(key)
            best[key] = (moment, index)
        elif moment > best[key][0]:
            best[key] = (moment, index)
    result = []
    for key in order:
        t = transactions[best[key][1]]
        result.append({"id": t["id"].strip(), "timestamp": t["timestamp"], "amount": t["amount"],
                       "currency": t["currency"].strip().upper()})
    return result


# ------------------------------------------------ rule 1: id matching

@pytest.mark.parametrize(
    "first, second",
    [
        ("TX-1", " TX-1"),
        ("TX-1", "TX-1  "),
        ("TX-1", "\tTX-1\n"),
        ("TX-1", "tx-1"),
        ("TX-1", " Tx-1 "),
        ("STRASSE-1", "straße-1"),   # casefold maps ß to ss; lower() does not
        ("ΣΊΣΥΦΟΣ", "σίσυφος"),      # final sigma
    ],
)
def test_ids_are_duplicates_after_strip_and_casefold(first, second):
    data = [tx(first, "2024-05-01T08:00:00Z", amount="1.00"), tx(second, "2024-05-01T09:00:00Z", amount="2.00")]
    assert dedupe(data) == [out(second.strip(), "2024-05-01T09:00:00Z", amount="2.00")]


@pytest.mark.parametrize("first, second", [("TX 1", "TX1"), ("TX-1", "TX_1"), ("TX-1", "TX-10")])
def test_ids_that_differ_inside_are_distinct(first, second):
    data = [tx(first, "2024-05-01T08:00:00Z"), tx(second, "2024-05-01T09:00:00Z")]
    assert [t["id"] for t in dedupe(data)] == [first, second]


# ------------------------------------------------ rule 2: latest real point in time

@pytest.mark.parametrize(
    "earlier, later",
    [
        ("2024-05-01T10:00:00+05:30", "2024-05-01T05:00:00Z"),       # 04:30Z vs 05:00Z
        ("2024-05-01T05:00:00Z", "2024-05-01T11:00:00+05:30"),       # 05:00Z vs 05:30Z
        ("2024-05-01T23:00:00-08:00", "2024-05-02T08:00:00+00:00"),  # 07:00Z next day vs 08:00Z
        ("2024-05-02T01:00:00+09:00", "2024-05-01T17:00:00Z"),       # 16:00Z vs 17:00Z
        ("2024-05-01T05:00:00.100Z", "2024-05-01T05:00:00.200Z"),
        ("2024-12-31T23:59:59+00:00", "2025-01-01T00:00:00Z"),
        ("2024-05-01T12:00:00+14:00", "2024-04-30T23:00:00-11:00"),  # 22:00Z previous day vs 10:00Z
    ],
)
@pytest.mark.parametrize("later_first", [False, True])
def test_latest_point_in_time_wins_whatever_the_offset(earlier, later, later_first):
    a, b = tx("TX-1", earlier, amount="1.00"), tx("TX-1", later, amount="2.00")
    data = [b, a] if later_first else [a, b]
    assert dedupe(data) == [out("TX-1", later, amount="2.00")]


@pytest.mark.parametrize(
    "first, second",
    [
        ("2024-05-01T05:00:00Z", "2024-05-01T05:00:00+00:00"),
        ("2024-05-01T05:00:00+00:00", "2024-05-01T05:00:00Z"),
        ("2024-05-01T10:30:00+05:30", "2024-05-01T05:00:00Z"),
        ("2024-05-01T05:00:00Z", "2024-05-01T10:30:00+05:30"),
        ("2024-05-01T00:00:00-05:00", "2024-05-01T05:00:00Z"),
        ("2024-05-01T05:00:00Z", "2024-05-01T05:00:00Z"),
    ],
)
def test_exact_tie_keeps_earliest_in_input(first, second):
    data = [tx(" TX-1", first, amount="1.00"), tx("tx-1 ", second, amount="2.00")]
    assert dedupe(data) == [out("TX-1", first, amount="1.00")]


def test_three_way_tie_keeps_first():
    data = [tx("TX-1", "2024-05-01T05:00:00Z", amount="1.00"),
            tx("TX-1", "2024-05-01T10:30:00+05:30", amount="2.00"),
            tx("TX-1", "2024-05-01T05:00:00+00:00", amount="3.00")]
    assert dedupe(data)[0]["amount"] == "1.00"


def test_tie_after_a_later_record_keeps_the_first_of_the_latest():
    data = [tx("TX-1", "2024-05-01T04:00:00Z", amount="1.00"),
            tx("TX-1", "2024-05-01T05:00:00Z", amount="2.00"),
            tx("TX-1", "2024-05-01T10:30:00+05:30", amount="3.00")]
    assert dedupe(data)[0]["amount"] == "2.00"


# ------------------------------------------------ rule 3: shape of kept records

def test_kept_id_is_stripped_original_of_the_kept_record():
    data = [tx("  ABC-1 ", "2024-05-01T05:00:00Z"), tx(" abc-1", "2024-05-01T06:00:00Z")]
    assert dedupe(data)[0]["id"] == "abc-1"


def test_kept_id_keeps_its_case():
    data = [tx("abc-1", "2024-05-01T05:00:00Z"), tx("  AbC-1\t", "2024-05-01T06:00:00Z")]
    assert dedupe(data)[0]["id"] == "AbC-1"


@pytest.mark.parametrize("raw, expected", [(" usd ", "USD"), ("eur", "EUR"), ("Gbp\n", "GBP"), ("JPY", "JPY")])
def test_currency_is_stripped_and_upper_cased(raw, expected):
    assert dedupe([tx("TX-1", "2024-05-01T05:00:00Z", currency=raw)])[0]["currency"] == expected


def test_currency_comes_from_the_kept_record():
    data = [tx("TX-1", "2024-05-01T05:00:00Z", currency="usd"), tx("TX-1", "2024-05-01T06:00:00Z", currency=" chf ")]
    assert dedupe(data)[0]["currency"] == "CHF"


@pytest.mark.parametrize("amount", ["0012.50", "-3.00", " 7.1 ", "1e3", "12,50"])
def test_amount_is_unchanged(amount):
    assert dedupe([tx("TX-1", "2024-05-01T05:00:00Z", amount=amount)])[0]["amount"] == amount


@pytest.mark.parametrize("timestamp", ["2024-05-01T05:00:00Z", "2024-05-01T10:30:00.123456+05:30", "2024-05-01T05:00:00+00:00"])
def test_timestamp_is_unchanged(timestamp):
    assert dedupe([tx("TX-1", timestamp)])[0]["timestamp"] == timestamp


# ------------------------------------------------ rule 4: output order

def test_output_order_is_first_appearance_of_each_id():
    data = [tx("B", "2024-05-01T01:00:00Z", amount="b1"),
            tx("A", "2024-05-01T01:00:00Z", amount="a1"),
            tx("b ", "2024-05-01T09:00:00Z", amount="b2"),
            tx("C", "2024-05-01T01:00:00Z", amount="c1"),
            tx(" a", "2024-05-01T09:00:00Z", amount="a2")]
    assert [(t["id"], t["amount"]) for t in dedupe(data)] == [("b", "b2"), ("a", "a2"), ("C", "c1")]


def test_output_order_with_offsets():
    data = [tx("Z-1", "2024-05-01T10:00:00+05:30"), tx("Y-1", "2024-05-01T05:00:00Z"),
            tx("z-1", "2024-05-01T05:00:00Z"), tx("y-1", "2024-05-01T10:00:00+05:30")]
    assert dedupe(data) == [out("z-1", "2024-05-01T05:00:00Z"), out("Y-1", "2024-05-01T05:00:00Z")]


# ------------------------------------------------ rule 5: no mutation

def test_input_list_and_dicts_are_not_mutated():
    data = [tx(" TX-1 ", "2024-05-01T10:00:00+05:30", currency=" usd "),
            tx("tx-1", "2024-05-01T05:00:00Z", currency="eur"),
            tx("TX-2 ", "2024-05-01T05:00:00Z", currency="gbp")]
    snapshot = copy.deepcopy(data)
    ids = [id(t) for t in data]
    dedupe(data)
    assert data == snapshot
    assert [id(t) for t in data] == ids


def test_returned_dicts_are_not_the_input_dicts():
    data = [tx("TX-1", "2024-05-01T05:00:00Z")]
    result = dedupe(data)
    result[0]["amount"] = "changed"
    assert data[0]["amount"] == "10.00"


# ------------------------------------------------ rule 6: invalid timestamps

@pytest.mark.parametrize(
    "bad",
    ["", "yesterday", "2024-05-01T05:00:00", "2024-05-01", "2024-13-01T05:00:00Z", "2024-05-32T05:00:00Z",
     "2024-05-01T25:00:00Z", None, 1714539600],
)
def test_invalid_timestamp_raises_value_error(bad):
    with pytest.raises(ValueError):
        dedupe([tx("TX-1", bad)])


def test_invalid_timestamp_in_a_later_duplicate_raises():
    with pytest.raises(ValueError):
        dedupe([tx("TX-1", "2024-05-01T05:00:00Z"), tx("TX-1", "not a time")])


def test_invalid_timestamp_in_a_distinct_record_raises():
    with pytest.raises(ValueError):
        dedupe([tx("TX-1", "2024-05-01T05:00:00Z"), tx("TX-2", "2024-05-01T05:00:00")])


# ------------------------------------------------ all rules together, seeded

def _random_timestamp(rng):
    base = datetime(2024, 5, 1, tzinfo=timezone.utc) + timedelta(minutes=rng.randrange(0, 600))
    minutes = rng.choice([0, 0, 330, -480, 540, 345, -210])
    local = base.astimezone(timezone(timedelta(minutes=minutes)))
    text = local.isoformat()
    if minutes == 0 and rng.random() < 0.5:
        text = text.replace("+00:00", "Z")
    return text


def _random_id(rng):
    core = rng.choice(["tx-1", "tx-2", "tx-3", "straße-4", "ab-5"])
    core = "".join(c.upper() if rng.random() < 0.5 else c for c in core)
    return rng.choice(["", " ", "\t"]) + core + rng.choice(["", " ", "  "])


@pytest.mark.parametrize("case", range(5))
def test_seeded_random_batches_match_oracle(case):
    rng = random.Random(SEED + case)
    for _ in range(200):
        data = [tx(_random_id(rng), _random_timestamp(rng), amount=str(i), currency=rng.choice(["eur", " USD ", "Gbp"]))
                for i in range(rng.randint(1, 12))]
        snapshot = copy.deepcopy(data)
        assert dedupe(data) == oracle(data), data
        assert data == snapshot
