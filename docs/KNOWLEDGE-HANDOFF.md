---
record_kind: project
evidence_kind: local-implementation-and-verification
reviewed: 2026-10-05
tags: [rate-limiting, python, admission, offline-lab]
---
# Rate-limit Admission Lab

Approved stages 1–4 implemented locally October 5, 2026. Authoritative project records are README.md, PLAN.md, STATE.md, VERIFICATION.md and REVIEW.md in rate-limit-admission-lab. Local isolated codex/rate-limit-admission-lab repository, no remote/publication/deployment.

Pure standard-library model compares exact single token-bucket credit against origin-zero half-open fixed windows over invented integer timestamp/cost events. Each validated event gets both decisions, including denials. Charge admitted cost only; oversize denials still advance/refill/reset state. Every identity's final state includes its own last event time, without refill to global end. Unreduced C/P credit is measured in cost units. Attempt and cost totals reconcile; eventual effects remain unmodeled. Identity is supplied fictional scope, not authentication/authorization/fairness.

Whole-input schema validation precedes all transitions/report; reject backwards time, duplicate keys/IDs, invalid Unicode, float/nonfinite/bool-as-integer, extra fields and bound excess. Byte/depth/string/numeric lexical gates plus postdecode container caps and 256-event/16-identity limits. CLI stable-regular-file/checked-sink handling with closed errors; exit0 for valid modeled traces even with denials, exit2 errors. No live clocks/traffic/providers/quotas/actual effects/enforcement or real data.

Verified Windows CPython3.13.7: 32 tests normally and optimized; ten frozen hand cases/31 paired rows; 108 separate Fraction policy sets/972 rows; ten demos and no-overwrite control; four assertion-detected semantic mutations in restored isolated copies/original unchanged. Maximum-cardinality input23713/report118822 bytes under fixed caps. Bandit1.9.4 zero remaining findings/errors with six narrow fixed-subprocess exceptions in tests/verifier, none application; unsuppressed control confirms only those six. Final/results.json holds exact source/fixture receipts; fixture SHA256631392ba4bc618b0a35cc8c8dde1e3efc3f4bc570fe8b87cee862ea9dc2007a5 frozen before code.

ECC implementing-agent self-review, not independent: fixed CRLF multiline mutation-target portability with explicit Python LF checkout rule; fixture bytes unnormalized. Initial sandbox temporary-area PermissionErrors resolved using owned ignored workspace temporary folders; honest initial failure summary and full later logs retained. No unresolved actionable code findings; no vulnerability-absence certification.

Research: inspected pinned [limits cb0ff429](https://github.com/alisaifee/limits/tree/cb0ff4294d1b713b7892f975443d04cd21d98dfa) and [token-bucket75bc464c](https://github.com/falconry/token-bucket/tree/75bc464c275f53488a2e5d5029a75e0eaa679113), source/tests/licenses/dependencies/CI. Original model; no upstream code executed/copied/installed. MIT local parsing/file/sink patterns adapted from Jake's structured-log lab. [Strategy docs](https://limits.readthedocs.io/en/stable/strategies.html) and [RFC2697](https://datatracker.ietf.org/doc/html/rfc2697) are context, not conformance claims. Related [[Exact Admission Budgets]], [[Python Input and Serialization Boundaries]], [[Structured Logging Field Minimization]].

Limits: finite synthetic evidence, no Linux/other-runtime/hosted CodeQL/CI/protections/eligibility, no formal proof/throughput/production enforcement, no hard CPU/RSS/I/O or race isolation, partial output/diagnostic-delivery failure, permitted metadata visibility, no distributed consistency/durability. Prepared pinned-action CI has not run; dev dependencies not transitive hash-locked. Two local Ollama prose drafts reviewed/corrected, raw preserved; no remote inference/spending. Next: manual local review; external publication/deployment needs separate Jake authorization. No new chat/scheduler/reply loop.
