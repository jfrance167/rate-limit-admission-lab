import copy
from fractions import Fraction
import itertools
import json
import unittest
from unittest.mock import patch

from rate_admission import model, render
from rate_admission.admission import LabError
from rate_admission.core import validate
from tests.support import cases, document, encode, rational_oracle


class ModelTests(unittest.TestCase):
    def test_frozen_hand_oracles(self):
        for case in cases():
            with self.subTest(case=case["name"]):
                result = model(encode(document(case["parameters"], case["events"])))
                rows = result["rows"]
                self.assertEqual([row["token_bucket"]["decision"] for row in rows], case["token_decisions"])
                self.assertEqual([row["fixed_window"]["decision"] for row in rows], case["window_decisions"])
                for side in ("before", "after"):
                    self.assertEqual([row["token_bucket"]["credit_" + side]["numerator"] for row in rows],
                                     case["credit_" + side])
                    self.assertEqual([row["fixed_window"]["spent_" + side] for row in rows], case["spent_" + side])
                self.assertEqual([row["fixed_window"]["window_index"] for row in rows], case["window_indices"])

    def test_independent_rational_oracle(self):
        # 108 policy sets, nine events each, cost changes/two declared identities.
        for capacity, period, refill in itertools.product(range(1, 4), range(1, 5), range(1, 4)):
            doc = document((capacity, refill, period, capacity, period),
                           [(index, 1 + index % 3, 1 + index % 2) for index in range(9)])
            report = model(encode(doc))
            for row, expected in zip(report["rows"], rational_oracle(doc), strict=True):
                token, window = row["token_bucket"], row["fixed_window"]
                self.assertEqual(token["decision"] == "admit", expected[0])
                self.assertEqual(Fraction(token["credit_before"]["numerator"], period), expected[1])
                self.assertEqual(Fraction(token["credit_after"]["numerator"], period), expected[2])
                self.assertEqual(window["decision"] == "admit", expected[3])
                self.assertEqual((window["spent_before"], window["spent_after"], window["window_index"] * period),
                                 expected[4:])

    def test_totals_and_identity_reconciliation(self):
        for case in cases():
            doc = document(case["parameters"], case["events"])
            report = model(encode(doc))
            self.assertEqual(report["effects"], "unmodeled")
            for name, summary in report["summary"].items():
                totals = summary["totals"]
                self.assertEqual(totals["attempts"], len(doc["events"]))
                self.assertEqual(totals["attempted_cost"], sum(event["cost"] for event in doc["events"]))
                self.assertEqual(totals["admitted_cost"], sum(row["cost"] for row in report["rows"]
                                                           if row[name]["decision"] == "admit"))
                for field in totals:
                    self.assertEqual(totals[field], sum(item["totals"][field] for item in summary["identities"]))
                for counts in [totals] + [item["totals"] for item in summary["identities"]]:
                    self.assertEqual(counts["attempts"], counts["admitted"] + counts["denied"])
                    self.assertEqual(counts["attempted_cost"], counts["admitted_cost"] + counts["denied_cost"])

    def test_inactive_final_state_not_global_end(self):
        report = model(encode(document((1, 1, 3, 1, 3), [(0, 1, 1), (3, 1, 2)])))
        states = report["summary"]["token_bucket"]["identities"]
        self.assertEqual([state["final_state"]["last_time_us"] for state in states], [0, 3])
        self.assertEqual([state["final_state"]["credit"]["numerator"] for state in states], [0, 0])
        fixed = report["summary"]["fixed_window"]["identities"]
        self.assertEqual([state["final_state"]["window_index"] for state in fixed], [0, 1])

    def test_oversize_denial_advances_both_states(self):
        doc = document((2, 1, 3, 2, 3), [(0, 2, 1), (100, 3, 1)])
        report = model(encode(doc))
        last = report["rows"][-1]
        self.assertEqual(last["token_bucket"]["reason"], "cost_exceeds_capacity")
        self.assertEqual(last["token_bucket"]["credit_after"]["numerator"], 6)
        self.assertEqual(last["fixed_window"]["reason"], "cost_exceeds_quota")
        self.assertEqual(last["fixed_window"]["spent_after"], 0)
        for summary in report["summary"].values():
            self.assertEqual(summary["identities"][0]["final_state"]["last_time_us"], 100)

    def test_reset_below_at_above_and_large_jump(self):
        doc = document((1, 1, 3, 1, 3), [(0, 1, 1), (2, 1, 1), (3, 1, 1), (4, 1, 1), (3600000000, 1, 1)])
        report = model(encode(doc))
        self.assertEqual([row["fixed_window"]["decision"] for row in report["rows"]],
                         ["admit", "deny", "admit", "deny", "admit"])
        self.assertEqual(report["rows"][-1]["fixed_window"]["window_index"], 1200000000)

    def test_empty_trace(self):
        report = model(encode(document(events=[])))
        self.assertEqual(report["rows"], [])
        for summary in report["summary"].values():
            self.assertEqual(summary["identities"], [])
            self.assertEqual(set(summary["totals"].values()), {0})

    def test_unreduced_units(self):
        report = model(encode(document((1, 1, 6, 1, 6), [(0, 1, 1), (3, 1, 1)])))
        self.assertEqual(report["rows"][-1]["token_bucket"]["credit_after"],
                         {"numerator": 3, "denominator": 6, "unit": "cost_units"})

    def test_input_immutability_and_determinism(self):
        doc = document()
        original = copy.deepcopy(doc)
        validate(doc)
        raw = encode(doc)
        self.assertEqual(render(model(raw)), render(model(raw)))
        self.assertEqual(doc, original)
        self.assertEqual(json.loads(render(model(raw)))["status"], "modeled")

    def test_parameters_exact_types_ranges_and_version(self):
        for version in (True, False, 0, 2, None, "1", 1.0):
            doc = document()
            doc["schema_version"] = version
            with self.subTest(version=version), self.assertRaises(LabError):
                model(encode(doc))
        for policy, fields in (("token_bucket", {"capacity": 1000, "refill_units": 1000, "period_us": 1000000}),
                               ("fixed_window", {"quota": 1000, "window_us": 1000000})):
            for field, upper in fields.items():
                for value in (True, 0, -1, upper + 1, None, "1", 1.0):
                    doc = document()
                    doc["policies"][policy][field] = value
                    with self.subTest(field=field, value=value), self.assertRaises(LabError):
                        model(encode(doc))
                for value in (1, upper):
                    doc = document()
                    doc["policies"][policy][field] = value
                    self.assertEqual(model(encode(doc))["status"], "modeled")

    def test_event_schema_bounds_and_labels(self):
        for field, values in {"cost": (True, 0, -1, 1001, None, "1", 1.0),
                              "time_us": (True, -1, 3600000001, None, "1", 0.0),
                              "event_id": ("lab-event-0000\n", "lab-event-１２３４", "x", None, 1),
                              "identity": ("lab-client-0000\n", "lab-client-１２３４", "x", None, 1)}.items():
            for value in values:
                doc = document()
                doc["events"][0][field] = value
                with self.subTest(field=field, value=value), self.assertRaises(LabError):
                    model(encode(doc))
        self.assertEqual(model(encode(document(events=[(3600000000, 1000, 1)])))["status"], "modeled")

    def test_unknown_missing_and_null_fields(self):
        base = document()
        positions = [(), ("policies",), ("policies", "token_bucket"),
                     ("policies", "fixed_window"), ("events", 0)]
        for position in positions:
            for mode in ("unknown", "missing", "null"):
                doc = copy.deepcopy(base)
                target = doc
                for part in position:
                    target = target[part]
                if mode == "unknown":
                    target["extra"] = 1
                elif mode == "missing":
                    del target[next(iter(target))]
                else:
                    target[next(iter(target))] = None
                with self.subTest(position=position, mode=mode), self.assertRaises(LabError):
                    model(encode(doc))
        for events in (None, {}, True):
            doc = document()
            doc["events"] = events
            with self.assertRaises(LabError):
                model(encode(doc))

    def test_late_error_prevents_any_transition(self):
        for kind in ("backwards", "duplicate", "malformed", "identity-limit"):
            doc = document(events=[(1, 1, 1), (2, 1, 1)])
            if kind == "backwards":
                doc["events"][-1]["time_us"] = 0
            elif kind == "duplicate":
                doc["events"][-1]["event_id"] = doc["events"][0]["event_id"]
            elif kind == "malformed":
                doc["events"][-1]["cost"] = False
            else:
                doc = document(events=[(index, 1, index) for index in range(17)])
            with patch("rate_admission.core._simulate") as transition:
                with self.assertRaises(LabError):
                    model(encode(doc))
                transition.assert_not_called()

    def test_maximum_trace_report_fit(self):
        doc = document((1000, 1000, 1000000, 1000, 1),
                       [(3600000000, 1000, 9984 + index % 16) for index in range(256)])
        raw = encode(doc)
        self.assertLess(len(raw), 65536)
        report = model(raw)
        self.assertEqual(len(report["rows"]), 256)
        self.assertEqual(len(report["summary"]["token_bucket"]["identities"]), 16)
        for summary in report["summary"].values():
            self.assertEqual(summary["totals"]["attempted_cost"], 256000)
        self.assertLess(len(render(report).encode()), 262144)
        with self.assertRaises(LabError):
            model(encode(document(events=[(0, 1, 1)] * 257)))

    def test_defensive_render_cap(self):
        # Injected internal report: unreachable from the admitted model corpus.
        with self.assertRaises(LabError) as caught:
            render({"injected": "x" * 262144})
        self.assertEqual(caught.exception.code, "output.error")


if __name__ == "__main__":
    unittest.main()
