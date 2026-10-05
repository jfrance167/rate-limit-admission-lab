# Rate-limit admission lab — proposed plan

Tier 3, October 5, 2026. Research authorized at 02:10; stages 1–4 approved by the central coordinator at 02:41 under Jake's verified direct mandate. Approval recorded here before application code. Sole writer: this chat. Separate directory; preserve parent Git, shared tooling and completed labs.

## Approved addendum — recorded before code

Reference: ../.private/coordination/2026-10-05/SUCCESSORS.md, October 5 02:41. Every validated event gets both policy decisions, including denials. Oversize cost still advances/refills/resets state before no-debit denial. Final identity state is at that identity's own last event, with timestamp; never implicitly advance inactive identities to the trace end. Empty traces have no identity states. Credit uses an unreduced integer numerator and denominator P, measured in cost units; comparisons use integers, not rendered fractions.

Freeze CLI/report contract: command `python -m rate_admission FILE`; `--help` exits 0 with fixed usage. Completed valid model exits 0/status `modeled` even with denied events. Errors exit 2 with only stderr JSON `status:error`/closed code, and no successful report. No exit 1 category. Argument validation precedes file I/O; raw byte/string/depth admission precedes UTF-8 decode/strict JSON hooks/tree limits; full schema, parameter and all event validation precedes model/report. Unknown version is `schema.invalid`, never unsupported success. The first encountered failing gate determines its closed code; no promise of classifying every defect in multiply-invalid input. Input I/O failures use `input.io`; serializer/report limit and sink failures use `output.error`; unexpected CLI exceptions use `internal.error`. No raw path/input/argv/native exception in diagnostics. No filesystem-race or output-atomicity guarantee.

Local isolated repository/codex branch and prepared pinned CI approved; no remote, parent Git changes, publication, live clocks/traffic/quotas/authentication/enforcement/effects or spending. All four semantic mutations and normal/optimized/max-report/output/Bandit/ECC checks required. Approval does not bypass app execution review.

## Problem and success

Build a deterministic, offline teaching tool that compares token-bucket and fixed-window admission over one invented sequence of timestamp/cost events. Show how capacity, refill, boundary resets and identity scope affect decisions. Success means every reported decision, exact balance and aggregate matches independently hand-calculated fixtures, and invalid late input cannot yield a partial successful report.

Admission means the model grants a cost budget. It does not establish identity, authorization, successful delivery, executed work or committed effects. Report eventual effects as `unmodeled`; do not invent an effect counter of zero. The retry lab models effects separately; the firewall-counter lab observes snapshots. Neither implements this admission contract.

## Scope and alternatives

Recommend an original Python standard-library model: integer arithmetic, strict JSON admission, pure transitions and a small CLI. Runtime dependencies: none outside the selected Python standard library. Existing reviewed input/output patterns can inform implementation after approval; retain provenance of any reused local code. See RESEARCH.md for inspected upstream alternatives and licenses.

Adopting `limits` would introduce storage/backend semantics and dependencies while its inspected fixed-window hit charges denied attempts. `token-bucket` has no declared runtime dependencies but uses real monotonic time, floating-point credit and documented concurrency compromises. Forking either is unnecessary for this bounded model. A fixed-window-only tool is simpler but cannot demonstrate fractional refill; floating-point or live middleware would need different correctness and operational evidence. Build both policies independently with explicitly chosen rules.

Exclude HTTP, requests, load/traffic generation, providers/accounts/quotas, real client data, network access, sleeps/clocks, middleware deployment, persistent/distributed state, concurrency, eviction, sliding windows, retry scheduling, multiple stacked limits and enforcement claims. Ordinary owned files used for documentation/tests are permitted workflow artifacts, not targets.

## Input contract to freeze before code

One strict UTF-8 JSON document. Root fields exactly `schema_version`, `policies`, `events`. Version is actual integer 1. Policies exactly `token_bucket` and `fixed_window`; each requires the complete fields below, with no defaults or extras. Event fields exactly `event_id`, `identity`, `time_us`, `cost`. No free-form text. Event IDs are unique ASCII `lab-event-NNNN`; supplied identity keys are ASCII `lab-client-NNNN`. IDs are invented labels, not credentials or authentication. Equal identity means shared state by declaration; different identity means independent state. No attempt to establish legitimacy or detect identity rotation.

| Quantity | Unit and admitted range |
| --- | --- |
| token `capacity` B | integer cost units, 1–1,000 |
| token `refill_units` R | integer cost units per period, 1–1,000 |
| token `period_us` P | integer microseconds, 1–1,000,000 |
| window `quota` Q | integer cost units, 1–1,000 |
| window `window_us` W | integer microseconds, 1–1,000,000 |
| event `time_us` t | relative integer microseconds, 0–3,600,000,000 |
| event `cost` c | integer cost units, 1–1,000 |

Reject booleans as integers, floating numbers including integral-looking forms, nonfinite constants, duplicate decoded object keys, unknown fields, invalid Unicode and missing/null fields. Global timestamps must be nondecreasing in array order; reject backwards time for the whole document rather than sort or clamp it. Equal timestamps use supplied order, a serial model convention without a concurrency guarantee. Empty events are valid and yield zero totals/no identity state.

Validate the entire document and all limits before any transitions or report. Schema validation is separate from syntax validation. Use the strict standard-library JSON decoder as syntax authority; a bounded lexical preflight limits nesting/numeric/string input without becoming another permissive grammar.

## Exact transition rules

Each policy processes the same sequence independently; neither consumes the other's outcomes. State is scoped by declared identity under its policy. Cost exceeding a policy's capacity/quota is a valid denied event (`cost_exceeds_capacity` or `cost_exceeds_quota`), not malformed input. Denials otherwise use `insufficient_credit` or `quota_exhausted`. Admission requires the full cost; no partial debit or negative balance.

**Token bucket:** represent token balance as scaled integer C with denominator P. A new identity first appears full (`C=B*P`) with last timestamp equal to its first event's t. For an existing identity, before each event compute delta `t-last_t` and `C_refilled=min(B*P,C+delta*R)`. Admit iff `c*P<=C_refilled`; on admission subtract `c*P`, otherwise retain `C_refilled`. Update `last_t=t` on every valid event, including denials. Clamping discards surplus beyond capacity; fractional credit below capacity is retained exactly. Report balance before debit and after debit as numerator/denominator, without floats or rounding. This is a continuously refilled single-bucket model, not RFC 2697's complete two-bucket color marker.

**Fixed window:** boundaries are anchored at relative origin zero. At event t use window index `k=t//W`, representing `[kW,(k+1)W)`. Each identity starts with spent cost zero in that index. A changed index resets spent to zero before the event, including exact boundary equality and jumps across many windows. Admit iff `spent+c<=Q`; add c only on admission. Denial leaves spent unchanged. This is admitted-cost accounting; attempted cost is a separate aggregate. It differs from the inspected `limits` in-memory first-hit expiry and increment-before-comparison behavior.

The two policies may have different supplied parameters. Never label one generally superior from unequal budgets. A demo comparing burst shapes should use B=Q and R/P=Q/W and label the shared average rate/capacity while noting different boundary semantics.

## State, arithmetic and report bounds

Predecode input cap 65,536 bytes, nesting 8 containers, numeric token 16 characters, encoded string body 128 bytes. Read at most cap+1 from a checked regular input file; no directory/device/pipe input or recursive scanning. Reject invalid UTF-8 and decoded lone surrogates, including keys. Postdecode container cap: arrays 256 items, total object keys 2,048. These cardinality checks occur after decoding; they are not preallocation controls.

At most 256 events and 16 distinct identities, established before modeling. No eviction or implicit reset from state pressure. At most 32 identity states (two policies). Attempted/admitted aggregate cost is at most 256,000 per policy; bucket multiplication B*P is at most 1,000,000,000 and refill delta*R at most 3,600,000,000,000. Python integers remain exact, with admitted operands bounding growth. No iteration over skipped time or empty windows. Report one paired policy row per admitted input event, then bounded per-policy/per-identity totals and final state; cap serialized UTF-8 output at 262,144 bytes, reject excess rather than truncate. A worst-case fixture must establish that supported traces fit, or the explicit report cap may reject them before emission.

Every policy reports attempts, admitted/denied event counts, attempted/admitted/denied cost, and final state. Reconcile attempts=admitted+denied and attempted_cost=admitted_cost+denied_cost globally and per identity. For each event include only validated synthetic ID/identity/time/cost plus the two decisions and exact relevant state. Mark effects `unmodeled` once in the report. No successful request/work metric. Do not emit raw input, tracebacks or parser/argv exception strings on errors; use closed error codes. Rendering finishes before output. Stdout is the sole report sink; check short/failed writes and return failure. Output cannot be transactional across failures; partial writes are possible and no successful delivery is promised. No output-path overwrite feature.

These are bounded admission/model/report policies, not hard process CPU, RSS, blocking-I/O deadlines, filesystem-race isolation or protection against a compromised interpreter/same-user process. Input/output remains visible to the running process. Use synthetic traces only.

## Independent oracle examples

Freeze exact input bytes and expected decisions/states before implementation, then hash fixtures and preserve raw evidence. The following hand calculations define key checks; A=admit, D=deny, all events use one identity unless stated.

| Scenario | Parameters and events `(time_us,cost)` | Expected |
| --- | --- | --- |
| Equal-time burst | B=Q=2,R=2,P=W=1,000,000; (0,1) three times | Both A,A,D; token C=0; window spent=2; attempted cost 3, admitted cost 2 |
| Fractional threshold | Same params; (0,2),(499999,1),(500000,1) | Token A,D,A; predebit C at last two events 999998 and 1000000; final C=0. Window A,D,D; spent=2 |
| Adjacent windows | Same params; (999999,1) twice,(1000000,1) twice | Window A,A,A,A, final spent=2/index1; token A,A,D,D, final C=2/P; first appearance starts full |
| Denied cost uncharged | B=Q=3,R=1,P=W=1,000,000; (0,2),(0,2),(0,1) | Both A,D,A; final zero balance/quota; attempted cost5, admitted cost3 |
| Surplus clamped | B=2,R=1,P=3; (0,2),(100,1),(100,1),(100,1) | Token A,A,A,D; idle surplus discarded; final C=0 |
| Fraction preserved | B=1,R=1,P=3; (0,1),(1,1),(2,1),(3,1) | Token A,D,D,A; predebit C=3,1,2,3; final C=0 |
| Identity scope | B=Q=1,R=1,P=W=1,000,000; x:(0,1),x:(0,1),y:(0,1) | Both A,D,A; two independent identities, no authentication claim |
| Oversize cost | B=Q=2,R=2,P=W=1,000,000; (0,3),(0,2) | Both D,A; first denial consumes no budget |

Add exact below/at/above reset checks, window jump, empty trace, late backwards timestamp, each bound at/over limit, duplicate decoded keys and IDs, 17th identity, malformed late event, bool/float/nonfinite/negative/zero inputs, excessive nesting/encoded strings and Unicode. Invalid inputs produce no successful report prefix. Check input immutability, independent policy states and deterministic repeated output. Use a second oracle based on standard-library rational arithmetic in tests, plus hand fixtures; never derive expected values by calling production transitions. Targeted mutations (reset `>` versus `>=`, loss of fractional credit, charging denials, skipping capacity clamp) must be detected and restored. This is finite evidence, not formal verification or a throughput benchmark.

## Threat model

Trust the owned reviewed code/interpreter and invented fixture provenance. Treat input bytes as hostile for parsing/resource/error handling. Protect integrity of admission calculations, bounded state and truthful report meaning. Threats include bool/int confusion, rounded credit, misplaced boundaries, identity cardinality exhaustion, late-invalid partial reports, reflected input in errors and confusing admission with effects. Mitigate through exact integer contract, whole-input validation, fixed limits, independent oracles, closed errors and explicit limitations. Supplied identity is untrusted metadata; deployable enforcement would require authentic scope, atomic state transitions, durable/distributed consistency and operational evidence outside this lab.

## Approved stages and definitions of done

1. Freeze schema, arithmetic, hand oracles and synthetic fixture provenance/hashes; scaffold only after approval. Record STATE/DECISIONS/LEARNING and approval addendum.
2. Implement bounded JSON admission and pure independent transitions; pass hand fixtures, malformed-input and reconciliation checks. Explain the scaled-credit concept before this stage.
3. Implement bounded CLI/report and synthetic demos; verify complete-validation-before-output, normal/optimized runs, output failure behavior and maximum permitted trace/report.
4. Run meaningful mutations, Bandit and actual ECC self-review; fix findings and rerun affected checks. Write README with problem, demo, architecture, setup, model, limitations, exact verification, learning, license/attribution and AI disclosure. Prepare pinned-action minimum-permission CI/CodeQL/Bandit per owned-repository baseline if local repository creation is approved; do not publish or claim hosted runs. Capture milestone in Obsidian and make local reviewed commits only within approved scope.

Local interpreter target: installed CPython 3.13.7 on Windows. Other runtimes/Linux/hosted checks remain unverified until run. No package installs are needed for the model; existing Bandit is available. Publication, PR, merge, deployment and real-target work require separate explicit authorization. No new scheduler/chat/agent/message loop.

Worker choice: local Ollama tried once with a bounded supplied-facts paragraph; raw draft retained. Its incomplete/ambiguous comparison is not authoritative. After reviewing the routing guide, considered OpenRouter's public structured/code route; no remaining suitable remote draft justifies a call, and current pricing/readiness was not refreshed. Mathematics/security/source review stays with Codex. No remote inference or paid fallback. Laya's tested classification/triage schemas do not fit this task.
