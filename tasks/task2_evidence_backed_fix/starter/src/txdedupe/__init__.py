"""Remove duplicate transactions from a payments export."""

from datetime import datetime

__all__ = ["dedupe"]


def _parse_timestamp(text):
    """Return an aware datetime for an ISO 8601 timestamp with a UTC offset or "Z".

    Raises ValueError if text is not a string, cannot be parsed by
    datetime.fromisoformat, or has no UTC offset.
    """
    if not isinstance(text, str):
        raise ValueError(f"invalid timestamp: {text!r}")
    try:
        moment = datetime.fromisoformat(text)
    except ValueError:
        raise ValueError(f"invalid timestamp: {text!r}") from None
    if moment.utcoffset() is None:
        raise ValueError(f"timestamp has no UTC offset: {text!r}")
    return moment


def _normalise(tx):
    out = dict(tx)
    out["id"] = tx["id"].strip()
    out["currency"] = tx["currency"].strip().upper()
    return out


def dedupe(transactions):
    """Return the transactions with duplicates removed.

    See the contract in the task description for the exact rules.
    """
    kept = {}
    order = []
    for tx in transactions:
        _parse_timestamp(tx["timestamp"])
        key = tx["id"]
        if key not in kept:
            kept[key] = tx
            order.append(key)
        elif tx["timestamp"] > kept[key]["timestamp"]:
            kept[key] = tx
    return [_normalise(kept[key]) for key in order]
