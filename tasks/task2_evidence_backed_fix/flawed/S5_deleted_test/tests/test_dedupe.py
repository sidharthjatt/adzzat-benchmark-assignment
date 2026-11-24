import copy

import pytest

from txdedupe import dedupe


def tx(id_, timestamp, amount="10.00", currency="EUR"):
    return {"id": id_, "timestamp": timestamp, "amount": amount, "currency": currency}


def test_empty_list():
    assert dedupe([]) == []


def test_distinct_ids_are_all_kept_in_input_order():
    data = [tx("B-2", "2024-03-01T09:00:00Z"), tx("A-1", "2024-03-01T08:00:00Z"), tx("C-3", "2024-03-01T07:00:00Z")]
    assert [t["id"] for t in dedupe(data)] == ["B-2", "A-1", "C-3"]


def test_duplicate_keeps_latest_timestamp():
    data = [tx("TX-1", "2024-03-01T09:00:00Z", amount="1.00"), tx("TX-1", "2024-03-01T11:00:00Z", amount="2.00")]
    assert dedupe(data) == [tx("TX-1", "2024-03-01T11:00:00Z", amount="2.00")]


def test_currency_is_stripped_and_upper_cased():
    assert dedupe([tx("TX-1", "2024-03-01T09:00:00Z", currency=" eur ")])[0]["currency"] == "EUR"


def test_kept_id_is_stripped():
    assert dedupe([tx("  TX-1 ", "2024-03-01T09:00:00Z")])[0]["id"] == "TX-1"


def test_amount_and_timestamp_are_unchanged():
    out = dedupe([tx("TX-1", "2024-03-01T09:00:00.250+01:00", amount="0012.50")])[0]
    assert out["amount"] == "0012.50"
    assert out["timestamp"] == "2024-03-01T09:00:00.250+01:00"


def test_input_is_not_mutated():
    data = [tx(" TX-1 ", "2024-03-01T09:00:00Z", currency="usd"), tx(" TX-1 ", "2024-03-01T10:00:00Z", currency="usd")]
    before = copy.deepcopy(data)
    dedupe(data)
    assert data == before


@pytest.mark.parametrize("bad", ["yesterday", "2024-03-01T09:00:00"])
def test_invalid_timestamp_raises_value_error(bad):
    with pytest.raises(ValueError):
        dedupe([tx("TX-1", bad)])


def test_ids_match_after_strip_and_casefold():
    data = [
        tx("TX-9", "2024-03-01T09:00:00Z", amount="1.00"),
        tx(" tx-9 ", "2024-03-01T10:00:00Z", amount="2.00"),
    ]
    assert dedupe(data) == [tx("tx-9", "2024-03-01T10:00:00Z", amount="2.00")]
