# Decisions

Approved October 5 at 02:41; implemented and locally verified. Research rationale is retained below.

- Build a distinct offline admission lab rather than extend retry/effect or counter-observation labs. Preserve adjacent projects.
- Exact scaled integer token credit makes fractional refill auditable without floating-point drift; report the explicit denominator.
- Fixed windows use relative origin zero and half-open intervals. Charge admitted cost only under both policies; attempt totals stay separate. These rules deliberately differ from inspected library semantics and must be labeled.
- Serial supplied order defines equal-time behavior. Reject backwards input globally before any report, rather than infer clocks or reorder data.
- Identity keys are bounded synthetic declarations; no authentication, fairness, eviction or rotation-detection claims. New identity gets its declared independent full bucket.
- Standard-library runtime avoids unnecessary backend dependencies. This is a fit decision, not proof that fewer dependencies guarantees security.
- Approval addendum recorded and ten hand cases committed before application code. No live enforcement, quotas, network, publication or effects in this scope.

- Reused reviewed MIT input/file/output patterns from Jake's structured-log lab; retained copyright/attribution. No upstream library code or runtime dependency adopted.
- Python files use explicit LF checkout policy: exact multiline mutation targets and source receipts must survive Windows autocrlf. Frozen fixture bytes remain unnormalized.
- Verifier mutates isolated copies and restores them; production source never changes. Six narrow subprocess scanner exclusions are justified by fixed owned commands without shell; unsuppressed control retained.
- CodeQL/Bandit/test workflows prepared with previously verified immutable pins for a future main branch. No remote or hosted security/protection claim.
