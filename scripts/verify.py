"""Reproduce fixed local checks and four isolated semantic mutations.

Runs only reviewed owned Python/tests and installed Bandit, never upstream code.
Evidence must use a fresh folder. Failed checks remain recorded; no auto retries.
Six narrow subprocess scanner exceptions are documented in VERIFICATION.md.
"""

import ast
import hashlib
import json
from pathlib import Path
import shutil
import subprocess  # nosec B404: fixed owned Python/tests and installed scanner commands.
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rate_admission import model, render  # noqa: E402
from tests.support import FIXTURE_SHA, cases, document, encode  # noqa: E402

MUTATIONS = {
    "strict-window-boundary": ('if index != state["window_index"]:',
                               'if event.time_us > (state["window_index"] + 1) * policy.window_us:'),
    "lost-fractional-refill": ('(event.time_us - state["last_time_us"]) * policy.refill_units)',
                              '((event.time_us - state["last_time_us"]) * policy.refill_units // period) * period)'),
    "charge-denied-token-cost": ('after = before - event.cost * period if decision == "admit" else before',
                                'after = before - event.cost * period'),
    "no-capacity-clamp": ('before = min(policy.capacity * period,\n                 state["credit"] + (event.time_us - state["last_time_us"]) * policy.refill_units)',
                          'before = state["credit"] + (event.time_us - state["last_time_us"]) * policy.refill_units'),
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(args, cwd, destination):
    # Caller constructs argv from fixed modules/flags and owned artifact paths.
    child = subprocess.run([sys.executable, *args], cwd=cwd, capture_output=True,  # nosec B603
                           text=True, encoding="utf-8", errors="replace", timeout=40, check=False)
    text = child.stdout + child.stderr
    normalized = text.replace(str(ROOT), "<workspace>")
    destination.write_text(normalized, encoding="utf-8", newline="\n")
    return child.returncode, text


def check_mutations(evidence):
    source = ROOT / "rate_admission" / "core.py"
    original = source.read_bytes()
    text = original.decode("utf-8")
    results = []
    base = ROOT / ".test-tmp"
    base.mkdir(exist_ok=True)
    for name, (old, new) in MUTATIONS.items():
        if text.count(old) != 1:
            raise ValueError("mutation target mismatch")
        with tempfile.TemporaryDirectory(dir=base) as folder:
            copy = Path(folder)
            for directory in ("rate_admission", "tests"):
                (copy / directory).mkdir()
                for file in (ROOT / directory).glob("*.py"):
                    shutil.copyfile(file, copy / directory / file.name)
            (copy / "fixtures").mkdir()
            shutil.copyfile(ROOT / "fixtures" / "cases.json", copy / "fixtures" / "cases.json")
            mutated = copy / "rate_admission" / "core.py"
            mutated.write_text(text.replace(old, new), encoding="utf-8", newline="\n")
            try:
                code, output = run(["-B", "-m", "unittest", "tests.test_model.ModelTests.test_frozen_hand_oracles", "-v"],
                                   copy, evidence / (name + ".log"))
                detected = code == 1 and "FAIL:" in output and "AssertionError" in output
            finally:
                mutated.write_bytes(original)
            restored = mutated.read_bytes() == original and source.read_bytes() == original
            results.append({"mutation": name, "exit": code, "assertion_detected": detected,
                            "copy_restored_original_unchanged": restored})
    return results


def check_demos(evidence):
    base = ROOT / ".test-tmp"
    base.mkdir(exist_ok=True)
    results = []
    with tempfile.TemporaryDirectory(dir=base) as folder:
        target = Path(folder) / "demos"
        code, _ = run(["scripts/make_demo.py", str(target)], ROOT, evidence / "demo-create.log")
        if code != 0:
            raise ValueError("demo creation failed")
        before = {path.name: digest(path) for path in target.glob("*.json")}
        for case in cases():
            name = case["name"]
            code, output = run(["-m", "rate_admission", str(target / (name + ".json"))], ROOT,
                               evidence / ("demo-" + name + ".json"))
            report = json.loads(output) if code == 0 else {}
            rows = report.get("rows", [])
            passed = (code == 0 and report.get("status") == "modeled"
                      and [row["token_bucket"]["decision"] for row in rows] == case["token_decisions"]
                      and [row["fixed_window"]["decision"] for row in rows] == case["window_decisions"])
            results.append({"name": name, "exit": code, "oracle_decisions_match": passed})
        code, _ = run(["scripts/make_demo.py", str(target)], ROOT, evidence / "demo-existing-refused.log")
        after = {path.name: digest(path) for path in target.glob("*.json")}
        results.append({"name": "refuse-existing-directory", "exit": code,
                        "oracle_decisions_match": code == 2 and before == after})
    return results


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        return 2
    evidence = Path(args[0])
    evidence.mkdir(parents=False, exist_ok=False)
    records = {"python": sys.version.split()[0], "platform": sys.platform, "fixture_sha256": FIXTURE_SHA}
    files = sorted(path for folder in ("rate_admission", "tests", "scripts")
                   for path in (ROOT / folder).glob("*.py"))
    for path in files:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path.relative_to(ROOT)))
    records["syntax_files"] = len(files)
    for name, flags in (("normal", []), ("optimized", ["-O"])):
        code, _ = run([*flags, "-m", "unittest", "discover", "-s", "tests", "-v"], ROOT,
                      evidence / (name + ".log"))
        records[name + "_exit"] = code
    code, _ = run(["-m", "bandit", "-r", "rate_admission", "tests", "scripts", "-f", "json",
                   "-o", str(evidence / "bandit.json")], ROOT, evidence / "bandit-command.log")
    records["bandit_exit"] = code
    scanner = json.loads((evidence / "bandit.json").read_text(encoding="utf-8"))
    records["bandit_findings"] = len(scanner["results"])
    records["bandit_analysis_errors"] = len(scanner["errors"])
    records["bandit_narrow_skips"] = scanner["metrics"]["_totals"]["skipped_tests"]
    records["mutations"] = check_mutations(evidence)
    records["demos"] = check_demos(evidence)
    max_doc = document((1000, 1000, 1000000, 1000, 1),
                       [(3600000000, 1000, 9984 + index % 16) for index in range(256)])
    records["max_trace"] = {"input_bytes": len(encode(max_doc)),
                            "report_bytes": len(render(model(encode(max_doc))).encode())}
    records["source_sha256"] = {str(path.relative_to(ROOT)).replace("\\", "/"): digest(path) for path in files}
    passed = (records["normal_exit"] == records["optimized_exit"] == records["bandit_exit"] == 0
              and records["bandit_findings"] == records["bandit_analysis_errors"] == 0
              and all(item["assertion_detected"] and item["copy_restored_original_unchanged"]
                      for item in records["mutations"])
              and all(item["oracle_decisions_match"] for item in records["demos"]))
    records["status"] = "pass" if passed else "fail"
    (evidence / "results.json").write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": records["status"], "normal_exit": records["normal_exit"],
                      "optimized_exit": records["optimized_exit"], "bandit_exit": records["bandit_exit"]}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
