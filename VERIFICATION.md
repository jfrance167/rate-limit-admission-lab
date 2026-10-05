# Verification — October 5, 2026

Final receipt: [docs/verification/final/results.json](docs/verification/final/results.json). Windows CPython **3.13.7**, Bandit **1.9.4**. Reviewed source/test/script hashes are in that receipt. Fixture bytes were frozen in commit 75e371a before application code, SHA256 `631392ba4bc618b0a35cc8c8dde1e3efc3f4bc570fe8b87cee862ea9dc2007a5`.

| Check | Material result | Evidence |
| --- | --- | --- |
| `python -m unittest discover -s tests -v` | PASS, exit0, 32 tests | final/normal.log |
| `python -O -m unittest discover -s tests -v` | PASS, exit0, 32 tests | final/optimized.log |
| Syntax | PASS, ast.parse of 11 owned Python files | final/results.json |
| Hand oracles | PASS, ten frozen cases/31 paired rows; decisions, before/after balances and indices | tests/test_model.py, fixtures/cases.json |
| Independent arithmetic | PASS, 108 parameter sets ×9 events; Fraction balances and separate interval-start oracle | test_independent_rational_oracle |
| Demos/no overwrite | PASS, ten CLI demos exit0; repeat generator exit2 with unchanged files | final/demo-*.json, results.json |
| Four semantic mutations | PASS, each child exit1 with FAIL/AssertionError; isolated copy restored/original unchanged | final/*boundary.log, *refill.log, *cost.log, *clamp.log |
| Maximum-cardinality trace/report | PASS, 256 events/16 identities, attempted cost256000; input23713/report118822 bytes | final/results.json |
| Output/error boundaries | PASS, short/bool/closed/flush sinks, actual closed stdout/stderr/both children exit2, help failure, late invalid input emits no report | tests/test_cli.py |
| `python -m bandit -r rate_admission tests scripts -f json …` | PASS, exit0, zero findings/errors, six narrow skipped checks | final/bandit.json |
| Unsuppressed scanner control | expected exit1, six fixed-subprocess findings, zero analysis errors | bandit-unsuppressed.json |
| ECC actual-change review | one portability finding fixed; zero unresolved findings | REVIEW.md |
| Prepared workflows | manual local policy review; immutable known pins, minimum permissions, checkout false | .github/workflows; REVIEW.md |
| Git/credential-pattern hygiene | see final separate receipt | docs/verification/hygiene.json |
| Linux, other runtimes, hosted CI/CodeQL, formal proof/throughput | NOT RUN | no remote/live workload |
| External type checker/linter | NOT RUN | no extra tool installed; syntax/behavior/SAST above |

Full reusable command: `python scripts/verify.py docs/verification/FRESH_DIRECTORY`. Inputs/outputs/assumptions are documented in its docstring and README. Uses current reviewed Python, installed Bandit, frozen local fixture and owned directories only. No installs/upstream execution/remote fallback. Checker failure does not become successful model output. Partial verification files may remain on tool failure; a missing final pass receipt is not completion.

Mutation definitions: strict `>` window-boundary condition instead of correct reset at equality; floor fractional refill; charge cost on token denial; remove capacity clamp. Tests require actual assertion detection, not any crash/import failure. Original core SHA is recorded; mutation copies are restored before their owned temporary directories are removed.

The measured trace maximizes cardinality and several numeric widths, not a claim it is the longest possible serialized report. Every row has a fixed schema, small closed reasons, bounded ASCII IDs and integers with at most ten digits; output cap also rejects excess defensively before emission. The render-cap test injects an internal oversized report; it does not claim that report is reachable from accepted model input. Raw parser depth/string/key limit tests likewise exercise admission independently of this narrower complete schema.

Six justified exclusions: B404 on subprocess imports in tests/test_cli.py and scripts/verify.py; B603 on three test child sites and the single verifier runner. All use a fixed owned Python/module/test/scanner invocation, constructed synthetic artifact paths and no shell. No raw input is used as executable/module/flag text. Same-user mutation of the interpreter/source is outside the trust model. Unsuppressed control confirms precisely those six warnings, no application findings. Exclusions are line-scoped with explanations; no global skip rules.

Initial run: 32 tests with five CLI temporary-area PermissionErrors, exit1; arithmetic checks passed. Original tool output was truncated, documented honestly in initial-sandbox-failure.md. Moving owned test files into ignored workspace temporary folders yielded normal-stage2.log PASS. Stage3 evidence retained; final supersedes its verifier-source hash after scanner-result accounting was added. No application changes were needed for the sandbox failure.

ECC review reproduced a multiline mutation-target mismatch on simulated CRLF source. `.gitattributes` now enforces Python LF and preserves fixture raw bytes; eol-review.json and `git check-attr` confirm the policy. Attributes did not change tested source bytes, so no redundant full rerun for that configuration-only fix. Log paths normalized to `<workspace>` where applicable; public data is invented. Initial staged whitespace check exited2 on unittest failure-reporter trailing spaces. Original affected logs retained in ignored `.drafts/original-logs`; public copies strip only trailing spaces, with log-formatting.json recording the correction. No assertions/results/source/fixture changed. Final staged whitespace check exited0.

Workload bounds are not OS isolation or wall-clock/RSS guarantees. Stable regular-file races/blocking, traceback/caller memory, partial writes and silent diagnostic delivery failure remain explicit limits. No runtime auth, rate enforcement, durability, application effects or data-redaction claim. No hosted eligibility/protections/secret services/transitive-hash-lock evidence. Keyword hygiene is a bounded pattern scan, not a comprehensive secret/privacy audit.
