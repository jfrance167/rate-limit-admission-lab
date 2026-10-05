"""Hand-fixture inputs and a separate rational test oracle."""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

FIXTURE_SHA = "631392ba4bc618b0a35cc8c8dde1e3efc3f4bc570fe8b87cee862ea9dc2007a5"
FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "cases.json"


def cases():
    raw = FIXTURE_PATH.read_bytes()
    if hashlib.sha256(raw).hexdigest() != FIXTURE_SHA:
        raise ValueError("frozen fixture mismatch")
    return json.loads(raw)["cases"]


def document(parameters=(2, 2, 1000000, 2, 1000000), events=((0, 1, 1),)):
    capacity, refill, period, quota, window = parameters
    return {"schema_version": 1, "policies": {
        "token_bucket": {"capacity": capacity, "refill_units": refill, "period_us": period},
        "fixed_window": {"quota": quota, "window_us": window}}, "events": [
            {"event_id": f"lab-event-{index:04d}", "identity": f"lab-client-{identity:04d}",
             "time_us": time, "cost": cost}
            for index, (time, cost, identity) in enumerate(events)]}


def encode(doc):
    return json.dumps(doc, separators=(",", ":")).encode("utf-8")


def rational_oracle(doc):
    """Compute tokens as Fraction cost units, not production scaled integers.

    Window state uses an interval start/end rather than production index state.
    This is finite independent arithmetic evidence, not a formal proof.
    """
    token = doc["policies"]["token_bucket"]
    window = doc["policies"]["fixed_window"]
    tokens, intervals, result = {}, {}, []
    for event in doc["events"]:
        identity, timestamp, cost = event["identity"], event["time_us"], event["cost"]
        balance, previous = tokens.get(identity, (Fraction(token["capacity"]), timestamp))
        balance += Fraction(token["refill_units"], token["period_us"]) * (timestamp - previous)
        balance = min(Fraction(token["capacity"]), balance)
        before = balance
        token_admit = cost <= balance
        if token_admit:
            balance -= cost
        tokens[identity] = (balance, timestamp)
        start, spent = intervals.get(identity, (timestamp - timestamp % window["window_us"], 0))
        if timestamp >= start + window["window_us"]:
            start, spent = timestamp - timestamp % window["window_us"], 0
        prior_spent = spent
        window_admit = spent + cost <= window["quota"]
        if window_admit:
            spent += cost
        intervals[identity] = (start, spent)
        result.append((token_admit, before, balance, window_admit, prior_spent, spent, start))
    return result
