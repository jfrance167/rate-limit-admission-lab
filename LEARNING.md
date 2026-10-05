# Learning goals

The concepts were proposed during research; local implementation evidence is now in VERIFICATION.md.

- A token bucket permits a bounded initial burst while replenishing fractional credit; a fixed-window reset can allow adjacent-window bursts. Average budget alone does not describe event decisions.
- Integer numerator/denominator state can express exact fractional tokens. Capacity clamping discards surplus; denial need not consume cost, but timestamp advancement still matters.
- Window anchor, boundary equality, charge-on-denial policy and identity scope belong to the contract. A shared algorithm name does not make two libraries equivalent.
- Attempts, admitted cost and completed work are different quantities. This model can account for the first two; effects remain unmodeled.
- Resource admission checks and serial arithmetic do not establish deployable authentication, distributed atomicity, durability or process isolation.

Verified lessons: 31 hand-calculated paired event rows and 972 Fraction-oracle rows matched; all four intentional semantic defects produced assertion failures. Oversize denials still advance/refill/reset, and inactive identities remain at their own timestamps. These are finite synthetic checks, not production guarantees.

Practical mistakes: sandbox temporary folders were unwritable in CLI tests, so owned workspace temporary folders were used instead. A simulated CRLF checkout broke a multiline mutation target; explicit Python LF attributes preserve repeatable verification. Local small drafts omitted facts/introduced uncertainty; Codex corrected them from source and actual receipts.

Optional exercise: explain why the adjacent-window example admits four cost units under its fixed-window policy while the same token bucket admits two. No teaching pause blocks authorized stages.
