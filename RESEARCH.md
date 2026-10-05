# Research — October 5, 2026

This records preimplementation research. Recommendation adopted after October 5 02:41 approval: **build an original bounded standard-library model**, with the precisely chosen semantics in PLAN.md. No upstream package installed or upstream source/test executed. Local implementation results now appear in VERIFICATION.md; this targeted comparison is not an exhaustive ecosystem audit or safety certification.

## Reuse and access

Read workspace instructions, shared STARTUP/routing guide, vault Home/Codex Integration and Python Input and Serialization Boundaries. The relevant vault note separates successful parsing from application validation and warns about nonfinite JSON/resource costs. A targeted source/Markdown `token.bucket|fixed.window` search excluding private evidence, environments, vendor, Git and GLPI returned no matching local implementation. Reviewed retry-idempotency-lab/PLAN.md (explicitly defers rate accounting) and firewall-counter-window-lab/README.md (snapshot observation). Completed structured-log lab provides reviewed bounded decoding/whole-input/output patterns; no files changed there or in the prior Marshal/pickle labs.

Connected GitHub repository search attempted once for this task and failed transport. Fallback: public GitHub REST through installed gh, plus primary web documentation. Firecrawl skill consulted but no Firecrawl call made: current free eligibility was not verified, and zero-spending policy controls optional calls. No Scorecard retrieved; no insecurity conclusion follows from that absence. License and dependencies verified from actual pinned source, not stars or metadata alone.

## Candidates actually inspected

| Candidate | Identity, maintenance evidence and license | Fit |
| --- | --- | --- |
| [alisaifee/limits](https://github.com/alisaifee/limits) | Nonarchived; public metadata push Aug 5, 2026. Inspected default-head [cb0ff429](https://github.com/alisaifee/limits/tree/cb0ff4294d1b713b7892f975443d04cd21d98dfa), commit July 13. Actual LICENSE.txt is MIT. | Useful reference for cost/storage/window distinctions; do not adopt for this offline contract. |
| [falconry/token-bucket](https://github.com/falconry/token-bucket) | Nonarchived; push June 12, 2026; inspected [75bc464c](https://github.com/falconry/token-bucket/tree/75bc464c275f53488a2e5d5029a75e0eaa679113). API license NOASSERTION resolved by actual LICENSE and pyproject: Apache-2.0. | Useful refill/capacity reference; clock/float/concurrency contract differs. |
| [alexdelorenzo/limiter](https://github.com/alexdelorenzo/limiter) | Metadata-only triage: nonarchived, last push Feb 26, 2024, LGPL-3.0 metadata. | Did not inspect source/tests or resolve full licensing obligations; not a strongest candidate for further adoption in this scope. |

Metadata push and inspected default-head commit dates need not match; neither establishes released-package identity or safe maintenance. Snapshots were downloaded at immutable revisions as base64 then decoded to inert `.txt` files under ignored research/upstream. They remain research evidence; no borrowed implementation is proposed.

### limits

Inspected [strategies.py](https://github.com/alisaifee/limits/blob/cb0ff4294d1b713b7892f975443d04cd21d98dfa/limits/strategies.py) FixedWindowRateLimiter.hit: calls storage.incr with cost before comparing to amount. Therefore denied hits still increment the inspected counter. [memory.py](https://github.com/alisaifee/limits/blob/cb0ff4294d1b713b7892f975443d04cd21d98dfa/limits/storage/memory.py) schedules expiry and sets expiry from first increment using time.time; it is not this lab's origin-zero window model.

Inspected [test_strategy.py](https://github.com/alisaifee/limits/blob/cb0ff4294d1b713b7892f975443d04cd21d98dfa/tests/test_strategy.py): fixed-window limit/empty stats, weighted-cost and reset/time checks across storage fixtures; timing-dependent tests exist. These were read, not run. [pyproject.toml](https://github.com/alisaifee/limits/blob/cb0ff4294d1b713b7892f975443d04cd21d98dfa/pyproject.toml) declares deprecated, packaging and typing_extensions runtime dependencies, with optional backend packages. Those extra dependencies are unnecessary for this lab, not thereby insecure.

Inspected [main.yml](https://github.com/alisaifee/limits/blob/cb0ff4294d1b713b7892f975443d04cd21d98dfa/.github/workflows/main.yml): test/lint/type jobs and Python matrix; visible checkout/setup-uv references use mutable version tags. Do not copy that pinning policy. Read [open issue 371](https://github.com/alisaifee/limits/issues/371), which reports separately issued async coredis increment/expiry commands causing missing expiry; [PR 372](https://github.com/alisaifee/limits/pull/372) appeared open in metadata. This is a reported backend issue, not independently reproduced here, and not an accusation against every backend. No remote backend is proposed.

### token-bucket

Inspected [limiter.py](https://github.com/falconry/token-bucket/blob/75bc464c275f53488a2e5d5029a75e0eaa679113/token_bucket/limiter.py): full initial bucket, supplied identity key, replenishment before all-or-nothing consume. [storage.py](https://github.com/falconry/token-bucket/blob/75bc464c275f53488a2e5d5029a75e0eaa679113/token_bucket/storage.py) uses time.monotonic, float balances, capacity clamping and a key dictionary; comments explicitly describe remaining threaded races. These are inspected design choices, not claims that its deployment is safe/unsafe. Our serial, bounded, exact model is a different contract.

Inspected [tests/test_limiter.py](https://github.com/falconry/token-bucket/blob/75bc464c275f53488a2e5d5029a75e0eaa679113/tests/test_limiter.py): initial/oversize cost, repeated refill with sleeps, separate keys and validation tests. Inspected [pyproject.toml](https://github.com/falconry/token-bucket/blob/75bc464c275f53488a2e5d5029a75e0eaa679113/pyproject.toml): no runtime dependencies; setuptools build dependency. [tests.yaml](https://github.com/falconry/token-bucket/blob/75bc464c275f53488a2e5d5029a75e0eaa679113/.github/workflows/tests.yaml) shows Python/Ubuntu test matrix, immutable SHA action references and checkout persist-credentials false; installs tooling at CI time. Read a bounded open issue/PR sample: usage example PR21, Redis backend request issue14 and subclass support PR10. This sample proves neither full issue coverage nor absence of security findings. Hosted results were not checked/run.

## Primary context and licensing

[limits strategy documentation](https://limits.readthedocs.io/en/stable/strategies.html) explains fixed-window boundary bursts. Its documented first-request window differs from our declared origin-zero policy. [RFC 2697](https://datatracker.ietf.org/doc/html/rfc2697) is an informational single-rate three-color marker reference; this lab does not implement or claim conformance to that full mechanism. rfc-editor fetch returned HTTP429; the datatracker alternate returned the document. Avoid conflating general token-bucket vocabulary with a standards-conformant traffic meter.

If code were borrowed, preserve MIT copyright/permission for limits and Apache-2.0 license/notices and change notices as applicable for token-bucket. Proposed original code needs source attribution links, AI-assistance disclosure and its own appropriate license after implementation approval. Research snapshots are ignored and should not be shipped wholesale. No external dependency needs introducing solely to match production semantics.

## Worker evidence and limits

Local Ollama qwen3.5:2b ran once through the existing helper, 5,566ms, stop completion, no helper contract warning. `.drafts/comparison-brief.txt` contains acceptance criteria and a 45-second deadline; `.drafts/comparison-raw.json` contains raw text despite its extension. Review: omitted the actual burst comparison/equal/backwards rules and ambiguously described reset at zero. Only its general admission-versus-effects distinction is usable; PLAN contains the reviewed explicit contract. No remote inference, paid fallback, model download, routing change or Laya invocation. Source verification, math and security judgments remain Codex work.

## Remaining uncertainties

At research handoff, implementation/oracle checks were pending. After approval they were completed locally; see VERIFICATION.md for exact finite evidence and maximum-cardinality report fit. No third-party package execution, differential production comparison, concurrency, provider quota or throughput evidence. Windows Python 3.13.7 was verified; Linux, other interpreters, hosted CI/security controls and publication remain unverified/unapproved.

Implementation usage draft: local Ollama once, 1,379ms, public supplied facts only, raw `.drafts/readme-run-raw.txt` retained. Preserved correct commands; corrected its unnecessary uncertainty about known standard-library dependencies and added omitted optimized test command/results. No retries, remote inference or spending. Codex retains code/math/security judgment.
