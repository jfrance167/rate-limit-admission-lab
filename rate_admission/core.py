"""Validated synthetic traces and independent exact serial policy transitions."""

from dataclasses import dataclass
import json
import re

from .admission import LabError, MAX_OUTPUT, parse

MAX_EVENTS = 256
MAX_IDENTITIES = 16
MAX_TIME = 3_600_000_000
LABEL = {"event_id": re.compile(r"lab-event-[0-9]{4}", re.ASCII),
         "identity": re.compile(r"lab-client-[0-9]{4}", re.ASCII)}


@dataclass(frozen=True)
class TokenPolicy:
    capacity: int
    refill_units: int
    period_us: int


@dataclass(frozen=True)
class WindowPolicy:
    quota: int
    window_us: int


@dataclass(frozen=True)
class Event:
    event_id: str
    identity: str
    time_us: int
    cost: int


@dataclass(frozen=True)
class Trace:
    token: TokenPolicy
    window: WindowPolicy
    events: tuple[Event, ...]


def _shape(value, names):
    if type(value) is not dict or set(value) != set(names):
        raise LabError("schema.invalid")


def _integer(value, minimum, maximum):
    if type(value) is not int or not minimum <= value <= maximum:
        raise LabError("schema.invalid")
    return value


def validate(document) -> Trace:
    """Validate the complete parsed document before any policy state exists.

    Callers supplying native values must already have bounded their allocation;
    the public bytes API model() applies lexical/decoder/tree gates first.
    """
    _shape(document, ("schema_version", "policies", "events"))
    _integer(document["schema_version"], 1, 1)
    policies = document["policies"]
    _shape(policies, ("token_bucket", "fixed_window"))
    token, window = policies["token_bucket"], policies["fixed_window"]
    _shape(token, ("capacity", "refill_units", "period_us"))
    _shape(window, ("quota", "window_us"))
    token_policy = TokenPolicy(_integer(token["capacity"], 1, 1000),
                               _integer(token["refill_units"], 1, 1000),
                               _integer(token["period_us"], 1, 1_000_000))
    window_policy = WindowPolicy(_integer(window["quota"], 1, 1000),
                                 _integer(window["window_us"], 1, 1_000_000))
    events = document["events"]
    if type(events) is not list:
        raise LabError("schema.invalid")
    if len(events) > MAX_EVENTS:
        raise LabError("input.limit")
    seen, identities, admitted = set(), set(), []
    previous = 0
    for event in events:
        _shape(event, ("event_id", "identity", "time_us", "cost"))
        for field, pattern in LABEL.items():
            if type(event[field]) is not str or pattern.fullmatch(event[field]) is None:
                raise LabError("schema.invalid")
        if event["event_id"] in seen:
            raise LabError("schema.invalid")
        seen.add(event["event_id"])
        identities.add(event["identity"])
        if len(identities) > MAX_IDENTITIES:
            raise LabError("input.limit")
        timestamp = _integer(event["time_us"], 0, MAX_TIME)
        cost = _integer(event["cost"], 1, 1000)
        if timestamp < previous:
            raise LabError("schema.invalid")
        previous = timestamp
        admitted.append(Event(event["event_id"], event["identity"], timestamp, cost))
    return Trace(token_policy, window_policy, tuple(admitted))


def _credit(numerator, denominator):
    # Unreduced scaled credit / period represents cost units, not microseconds.
    return {"numerator": numerator, "denominator": denominator, "unit": "cost_units"}


def _counts():
    return {"attempts": 0, "admitted": 0, "denied": 0,
            "attempted_cost": 0, "admitted_cost": 0, "denied_cost": 0}


def _count(counts, cost, decision):
    counts["attempts"] += 1
    counts["attempted_cost"] += cost
    category = "admitted" if decision == "admit" else "denied"
    counts[category] += 1
    counts[category + "_cost"] += cost


def _token_step(policy, state, event):
    period = policy.period_us
    before = min(policy.capacity * period,
                 state["credit"] + (event.time_us - state["last_time_us"]) * policy.refill_units)
    if event.cost > policy.capacity:
        decision, reason = "deny", "cost_exceeds_capacity"
    elif event.cost * period > before:
        decision, reason = "deny", "insufficient_credit"
    else:
        decision, reason = "admit", "within_budget"
    after = before - event.cost * period if decision == "admit" else before
    state.update(credit=after, last_time_us=event.time_us)
    return {"decision": decision, "reason": reason,
            "credit_before": _credit(before, period), "credit_after": _credit(after, period)}


def _window_step(policy, state, event):
    index = event.time_us // policy.window_us
    # Half-open origin-zero windows reset BEFORE the exact-boundary event.
    if index != state["window_index"]:
        state["spent"] = 0
    before = state["spent"]
    if event.cost > policy.quota:
        decision, reason = "deny", "cost_exceeds_quota"
    elif before + event.cost > policy.quota:
        decision, reason = "deny", "quota_exhausted"
    else:
        decision, reason = "admit", "within_budget"
    after = before + event.cost if decision == "admit" else before
    state.update(spent=after, window_index=index, last_time_us=event.time_us)
    return {"decision": decision, "reason": reason, "window_index": index,
            "spent_before": before, "spent_after": after}


def _simulate(trace):
    """Internal transition entry: accepts only a fully admitted Trace."""
    tokens, windows = {}, {}
    summary = {name: {"totals": _counts(), "identities": []}
               for name in ("token_bucket", "fixed_window")}
    identity_counts = {name: {} for name in summary}
    rows = []
    for event in trace.events:
        identity = event.identity
        if identity not in tokens:
            tokens[identity] = {"credit": trace.token.capacity * trace.token.period_us,
                                "last_time_us": event.time_us}
            windows[identity] = {"spent": 0, "window_index": event.time_us // trace.window.window_us,
                                 "last_time_us": event.time_us}
            for name in summary:
                identity_counts[name][identity] = _counts()
        decisions = {"token_bucket": _token_step(trace.token, tokens[identity], event),
                     "fixed_window": _window_step(trace.window, windows[identity], event)}
        rows.append({"event_id": event.event_id, "identity": identity,
                     "time_us": event.time_us, "cost": event.cost, **decisions})
        for name, outcome in decisions.items():
            _count(summary[name]["totals"], event.cost, outcome["decision"])
            _count(identity_counts[name][identity], event.cost, outcome["decision"])
    for identity in sorted(tokens):
        token, window = tokens[identity], windows[identity]
        # Final states are at each identity's own last event, never global end.
        final_states = {"token_bucket": {"last_time_us": token["last_time_us"],
                                         "credit": _credit(token["credit"], trace.token.period_us)},
                        "fixed_window": dict(window)}
        for name in summary:
            summary[name]["identities"].append({"identity": identity,
                                               "totals": identity_counts[name][identity],
                                               "final_state": final_states[name]})
    return {"schema_version": 1, "profile": "rate-admission-lab/1", "status": "modeled",
            "effects": "unmodeled", "policies": {
                "token_bucket": {"capacity": trace.token.capacity, "refill_units": trace.token.refill_units,
                                 "period_us": trace.token.period_us},
                "fixed_window": {"quota": trace.window.quota, "window_us": trace.window.window_us}},
            "rows": rows, "summary": summary}


def model(raw: bytes) -> dict:
    """Model the entire bounded invented trace, or raise a closed LabError.

    Both policies appear for every validated event, including budget denials.
    This is admission accounting only; it executes no application effects.
    """
    return _simulate(validate(parse(raw)))


def render(report: dict) -> str:
    """Render an internally produced report before writing to any sink.

    The cap is a defensive guard as well as a contract; no report truncation.
    """
    output = json.dumps(report, ensure_ascii=True, sort_keys=True,
                        separators=(",", ":"), allow_nan=False) + "\n"
    if len(output.encode("utf-8")) > MAX_OUTPUT:
        raise LabError("output.error")
    return output
